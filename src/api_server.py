"""
可选 HTTP API（uvicorn api_server:app）。

GET /health 公开。POST /chat 与 GET /rag/summarize 必须 AGENT_API_KEY
（Bearer 或 X-API-Key）。username 只在鉴权之后选择数据空间，不是口令。
skill 必须在 SKILL_WHITELIST。异常对客户端脱敏。
"""
from __future__ import annotations

import json
import os
import secrets
import time
import uuid
from collections import deque
from contextlib import asynccontextmanager
from pathlib import Path
from threading import Lock
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from agent.react_agent import ReactAgent
from agent.tools.agent_tools import set_current_user_id
from agent.tools.middleware import SKILL_WHITELIST
from rag.rag_service import RagSummarizeService
from rag.tenant import load_tenant, list_tenants
from services import user_service
from services.storage import ensure_db, get_conn
from utils.logger_handler import log_event

_agent: ReactAgent | None = None
_kb_cache: dict[str, RagSummarizeService] = {}

RATE_LIMIT_PER_MIN = int(os.getenv("RATE_LIMIT_PER_MIN", "10"))
_rate_buckets: dict[str, deque[float]] = {}
_rate_lock = Lock()
INDEX_HTML = Path(__file__).resolve().parents[1] / "web" / "static" / "index.html"
DIST_DIR = Path(__file__).resolve().parents[1] / "web" / "dist"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """进程生命周期：启动时确保 SQLite 表存在。"""
    ensure_db()
    yield


app = FastAPI(title="个人综合助手 API", version="0.2.0", lifespan=lifespan)

if DIST_DIR.is_dir():
    app.mount("/app", StaticFiles(directory=str(DIST_DIR), html=True), name="web")


@app.middleware("http")
async def trace_middleware(request: Request, call_next):
    """为每个请求生成 trace id，并记录访问日志。"""
    rid = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
    started = time.perf_counter()
    response = await call_next(request)
    elapsed = int((time.perf_counter() - started) * 1000)
    response.headers["X-Request-ID"] = rid
    log_event(
        "api.access",
        request_id=rid,
        path=request.url.path,
        status=response.status_code,
        ms=elapsed,
    )
    return response


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=16000)
    username: str = Field(default="api_user", max_length=64)
    skill: str = Field(default="default", max_length=64)
    conversation_id: str | None = Field(default=None, max_length=128)


class ChatResponse(BaseModel):
    request_id: str
    conversation_id: str
    reply: str
    user_id: int


def _expected_api_key() -> str:
    """读取环境变量 AGENT_API_KEY。"""
    return (os.getenv("AGENT_API_KEY") or "").strip()


def _extract_api_key(
    authorization: str | None,
    x_api_key: str | None,
) -> str:
    """从 Bearer 或 X-API-Key 头取出客户端密钥。"""
    if x_api_key and x_api_key.strip():
        return x_api_key.strip()
    auth = (authorization or "").strip()
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return ""


def require_api_key(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    """
    鉴权策略：
    - 已配置 AGENT_API_KEY：必须 Bearer 或 X-API-Key 匹配
    - 未配置：拒绝受保护端点（避免「用户名即身份」裸奔）；/health 仍开放
    """
    expected = _expected_api_key()
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="服务未配置 AGENT_API_KEY，已拒绝受保护接口。请在 .env 设置后重启。",
        )
    provided = _extract_api_key(authorization, x_api_key)
    if not provided or not secrets.compare_digest(provided, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")


def _get_agent() -> ReactAgent:
    """懒创建并缓存进程内 ReactAgent 单例。"""
    global _agent
    if _agent is None:
        _agent = ReactAgent(model_mode="auto")
    return _agent


def _get_kb(tenant_id: str) -> RagSummarizeService:
    """按租户懒创建并缓存知识库问答服务。"""
    svc = _kb_cache.get(tenant_id)
    if svc is None:
        svc = RagSummarizeService(tenant_id=tenant_id)
        _kb_cache[tenant_id] = svc
    return svc


def _client_key(authorization: str | None, x_api_key: str | None, request: Request) -> str:
    """限流键：优先 API Key，其次客户端 IP。"""
    provided = _extract_api_key(authorization, x_api_key)
    if provided:
        return provided
    return request.client.host if request.client else "unknown"


def check_rate_limit(key: str) -> None:
    """按分钟滑动窗口限流，超限返回 429。"""
    now = time.time()
    with _rate_lock:
        bucket = _rate_buckets.setdefault(key, deque())
        while bucket and now - bucket[0] > 60:
            bucket.popleft()
        if len(bucket) >= RATE_LIMIT_PER_MIN:
            raise HTTPException(
                status_code=429,
                detail=f"请求过于频繁，限制 {RATE_LIMIT_PER_MIN} 次/分钟",
            )
        bucket.append(now)


def _validate_skill(skill: str) -> str:
    """校验 skill 是否在白名单，非法则 400。"""
    name = (skill or "default").strip() or "default"
    if name not in SKILL_WHITELIST:
        raise HTTPException(
            status_code=400,
            detail=f"skill 不在白名单：{sorted(SKILL_WHITELIST)}",
        )
    return name


@app.get("/", include_in_schema=False)
def index():
    """浏览器入口：优先 React 页面，其次内置静态页。"""
    if DIST_DIR.is_dir():
        return RedirectResponse(url="/app/")
    if INDEX_HTML.is_file():
        return FileResponse(INDEX_HTML)
    return {"status": "ok", "docs": "/docs", "kb": "/kb/ask"}


@app.get("/health")
def health() -> dict[str, Any]:
    """健康检查，并告知是否已配置 API Key 与可用租户。"""
    keyed = bool(_expected_api_key())
    return {
        "status": "ok",
        "api_key_configured": keyed,
        "tenants": [t["id"] for t in list_tenants()],
    }


@app.post("/chat", response_model=ChatResponse)
def chat(
    body: ChatRequest,
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> ChatResponse:
    """鉴权后执行一轮对话并返回完整回复。"""
    require_api_key(authorization, x_api_key)
    ensure_db()
    skill = _validate_skill(body.skill)
    try:
        u = user_service.switch_or_create(body.username.strip() or "api_user")
    except Exception as e:
        raise HTTPException(status_code=400, detail="无效用户名") from e
    set_current_user_id(u["id"])
    conv = body.conversation_id or uuid.uuid4().hex
    rid = uuid.uuid4().hex[:12]
    try:
        agent = _get_agent()
        chunks: list[str] = []
        for piece in agent.execute_stream(
            body.message,
            user_id=str(u["id"]),
            conversation_id=conv,
            skill=skill,
            request_id=rid,
        ):
            if piece:
                chunks.append(piece)
        reply = "".join(chunks).strip() or "不知道"
    except Exception as e:
        log_event("api.chat", level=40, status="error", error=str(e)[:500], request_id=rid)
        raise HTTPException(status_code=500, detail="执行失败，请查看服务端日志") from e
    return ChatResponse(request_id=rid, conversation_id=conv, reply=reply, user_id=int(u["id"]))


@app.get("/rag/summarize")
def rag_summarize(
    q: str,
    username: str = "api_user",
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> dict[str, Any]:
    """鉴权后对查询做 RAG 总结。"""
    require_api_key(authorization, x_api_key)
    ensure_db()
    if not (q or "").strip():
        raise HTTPException(status_code=400, detail="q 不能为空")
    try:
        u = user_service.switch_or_create(username.strip() or "api_user")
    except Exception as e:
        raise HTTPException(status_code=400, detail="无效用户名") from e
    set_current_user_id(u["id"])
    from rag.rag_service import RagSummarizeService

    try:
        text = RagSummarizeService().rag_summarize(q, user_id=u["id"])
    except Exception as e:
        log_event("api.rag", level=40, status="error", error=str(e)[:500])
        raise HTTPException(status_code=500, detail="检索失败，请查看服务端日志") from e
    return {"query": q, "answer": text, "user_id": u["id"]}


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class Citation(BaseModel):
    source: str
    chunk_index: int | None = None
    snippet: str


class AskResponse(BaseModel):
    request_id: str
    tenant: str
    answer: str
    citations: list[Citation]
    latency_ms: int
    refused: bool


@app.post("/kb/ask", response_model=AskResponse)
def kb_ask(
    body: AskRequest,
    request: Request,
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    x_tenant: str | None = Header(default="demo", alias="X-Tenant"),
) -> AskResponse:
    """知识库问答：按 X-Tenant 选择租户，返回答案与引用。"""
    require_api_key(authorization, x_api_key)
    check_rate_limit(_client_key(authorization, x_api_key, request))
    tenant_id = (x_tenant or "demo").strip() or "demo"
    try:
        load_tenant(tenant_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"租户不存在: {tenant_id}") from e
    question = body.question.strip()
    rid = uuid.uuid4().hex[:12]
    started = time.perf_counter()
    svc = _get_kb(tenant_id)
    docs = svc.retrieve_docs(question)
    if docs:
        parts = [
            f"[参考资料{i}] 来源:{(d.metadata or {}).get('source_path', '')}\n{d.page_content}"
            for i, d in enumerate(docs, start=1)
        ]
        answer = svc._chain().invoke({"input": question, "context": "\n\n".join(parts)})
    else:
        answer = "不知道"
    latency = int((time.perf_counter() - started) * 1000)
    citations = [
        Citation(
            source=str((d.metadata or {}).get("source_path", "")),
            chunk_index=(d.metadata or {}).get("chunk_index"),
            snippet=(d.page_content or "")[:200],
        )
        for d in docs[:5]
    ]
    refused = str(answer).strip().startswith("不知道")
    log_event("api.kb", request_id=rid, tenant=tenant_id, ms=latency, docs=len(docs), refused=refused)
    return AskResponse(
        request_id=rid,
        tenant=tenant_id,
        answer=str(answer),
        citations=citations,
        latency_ms=latency,
        refused=refused,
    )


class FeedbackRequest(BaseModel):
    message_id: str = Field(..., min_length=1, max_length=64)
    rating: str = Field(..., pattern="^(up|down)$")
    reason: str | None = Field(default=None, max_length=200)


@app.post("/feedback")
def feedback(
    body: FeedbackRequest,
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    x_tenant: str | None = Header(default="demo", alias="X-Tenant"),
) -> dict[str, Any]:
    """记录点赞/点踩，进入 badcase 池。"""
    require_api_key(authorization, x_api_key)
    tenant_id = (x_tenant or "demo").strip() or "demo"
    try:
        load_tenant(tenant_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"租户不存在: {tenant_id}") from e
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO feedback(tenant_id, message_id, rating, reason) VALUES(?,?,?,?)",
            (tenant_id, body.message_id, body.rating, body.reason),
        )
    log_event("api.feedback", tenant=tenant_id, rating=body.rating, message_id=body.message_id)
    return {"ok": True}


def _sse(event: str, data: dict[str, Any]) -> str:
    """拼一条 SSE 消息。"""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.post("/kb/stream")
def kb_stream(
    body: AskRequest,
    request: Request,
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    x_tenant: str | None = Header(default="demo", alias="X-Tenant"),
):
    """SSE 流式问答：meta → citations → token* → done。"""
    require_api_key(authorization, x_api_key)
    check_rate_limit(_client_key(authorization, x_api_key, request))
    tenant_id = (x_tenant or "demo").strip() or "demo"
    try:
        load_tenant(tenant_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"租户不存在: {tenant_id}") from e

    question = body.question.strip()
    rid = uuid.uuid4().hex[:12]
    svc = _get_kb(tenant_id)
    docs = svc.retrieve_docs(question)
    citations = [
        {
            "source": str((d.metadata or {}).get("source_path", "")),
            "chunk_index": (d.metadata or {}).get("chunk_index"),
            "snippet": (d.page_content or "")[:300],
        }
        for d in docs[:5]
    ]
    context = "\n\n".join(
        f"[参考资料{i}] 来源:{(d.metadata or {}).get('source_path', '')}\n{d.page_content}"
        for i, d in enumerate(docs, start=1)
    )

    def generate():
        started = time.perf_counter()
        yield _sse("meta", {"request_id": rid, "tenant": tenant_id})
        yield _sse("citations", {"citations": citations})
        if not docs:
            yield _sse("token", {"text": "不知道"})
            yield _sse("done", {"request_id": rid, "refused": True, "latency_ms": 0})
            return
        parts: list[str] = []
        try:
            for chunk in svc._chain().stream({"input": question, "context": context}):
                text = chunk if isinstance(chunk, str) else getattr(chunk, "content", "")
                if text:
                    parts.append(str(text))
                    yield _sse("token", {"text": str(text)})
        except Exception as e:  # noqa: BLE001
            log_event("api.kb_stream", level=40, status="error", error=str(e)[:300], request_id=rid)
            yield _sse("error", {"message": "生成失败，请稍后重试"})
            return
        full = "".join(parts)
        latency = int((time.perf_counter() - started) * 1000)
        log_event("api.kb_stream", request_id=rid, tenant=tenant_id, ms=latency, docs=len(docs))
        yield _sse(
            "done",
            {
                "request_id": rid,
                "refused": full.strip().startswith("不知道"),
                "latency_ms": latency,
            },
        )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
