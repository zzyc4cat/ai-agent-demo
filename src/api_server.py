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

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from langchain_community.callbacks import get_openai_callback
from pydantic import BaseModel, Field

from agent.react_agent import ReactAgent
from agent.tools.agent_tools import set_current_user_id
from agent.tools.middleware import SKILL_WHITELIST
from rag.rag_service import RagSummarizeService
from rag.tenant import load_tenant, list_tenants
from services import admin_service, auth_service, kb_store, user_service
from services.cost import estimate_cost
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
    """进程生命周期：建表 + 清理上次遗留的入库任务。"""
    ensure_db()
    recovered = admin_service.recover_stale_tasks()
    if recovered:
        log_event("api.startup", recovered_tasks=recovered)
    yield


app = FastAPI(title="设备知识库 API", version="0.3.0", lifespan=lifespan)

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


def _bearer_token(authorization: str | None) -> str:
    """从 Authorization: Bearer 取 token。"""
    auth = (authorization or "").strip()
    return auth[7:].strip() if auth.lower().startswith("bearer ") else ""


def current_user(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    """登录态：token 无效直接 401。"""
    user = auth_service.user_from_token(_bearer_token(authorization))
    if not user:
        raise HTTPException(status_code=401, detail="未登录或登录已过期")
    return user


def require_admin(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    """管理员专属接口。"""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user


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
    """健康检查（公开）。"""
    return {
        "status": "ok",
        "tenants": [t["id"] for t in list_tenants()],
        "registration": "open",
    }


class AuthRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    password: str = Field(..., min_length=8, max_length=128)


class AuthResponse(BaseModel):
    token: str
    user: dict[str, Any]


@app.post("/auth/register", response_model=AuthResponse)
def register(body: AuthRequest) -> AuthResponse:
    """开放注册：新用户默认加入 demo 租户、角色 user。"""
    try:
        user = auth_service.create_user(body.username, body.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    token = auth_service.create_session(int(user["id"]))
    return AuthResponse(token=token, user=user)


@app.post("/auth/login", response_model=AuthResponse)
def login(body: AuthRequest) -> AuthResponse:
    """账号密码登录，返回会话 token。"""
    user = auth_service.authenticate(body.username, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="账号或密码错误，或尝试次数过多")
    token = auth_service.create_session(int(user["id"]))
    return AuthResponse(token=token, user=user)


@app.post("/auth/logout")
def logout(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    """退出登录：服务端立即失效该 token。"""
    auth_service.revoke_session(_bearer_token(authorization))
    return {"ok": True}


@app.get("/auth/me")
def me(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    """当前登录用户。"""
    return user


@app.post("/chat", response_model=ChatResponse)
def chat(
    body: ChatRequest,
    user: dict[str, Any] = Depends(current_user),
) -> ChatResponse:
    """登录后执行一轮对话并返回完整回复。"""
    ensure_db()
    skill = _validate_skill(body.skill)
    try:
        u = user_service.switch_or_create(user["username"])
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
    user: dict[str, Any] = Depends(current_user),
) -> dict[str, Any]:
    """登录后对查询做 RAG 总结。"""
    ensure_db()
    if not (q or "").strip():
        raise HTTPException(status_code=400, detail="q 不能为空")
    try:
        u = user_service.switch_or_create(user["username"])
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
    conversation_id: str | None = Field(default=None, max_length=64)


class Citation(BaseModel):
    source: str
    chunk_index: int | None = None
    snippet: str


class AskResponse(BaseModel):
    request_id: str
    tenant: str
    conversation_id: str
    answer: str
    citations: list[Citation]
    latency_ms: int
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_cny: float | None = None
    refused: bool


@app.post("/kb/ask", response_model=AskResponse)
def kb_ask(
    body: AskRequest,
    request: Request,
    user: dict[str, Any] = Depends(current_user),
) -> AskResponse:
    """知识库问答：租户来自登录用户，返回答案与引用。"""
    check_rate_limit(f"u{user['id']}")
    tenant_id = str(user["tenant_id"])
    try:
        load_tenant(tenant_id)
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"用户所属租户配置缺失: {tenant_id}") from e
    question = body.question.strip()
    rid = uuid.uuid4().hex[:12]
    conversation_id = kb_store.ensure_conversation(
        body.conversation_id, tenant_id, question, user_id=user["id"]
    )
    kb_store.add_message(
        message_id=f"{rid}-u",
        conversation_id=conversation_id,
        tenant_id=tenant_id,
        role="user",
        content=question,
    )
    started = time.perf_counter()
    svc = _get_kb(tenant_id)
    docs = svc.retrieve_docs(question)
    with get_openai_callback() as cb:
        if docs:
            parts = [
                f"[参考资料{i}] 来源:{(d.metadata or {}).get('source_path', '')}\n{d.page_content}"
                for i, d in enumerate(docs, start=1)
            ]
            answer = svc._chain().invoke({"input": question, "context": "\n\n".join(parts)})
        else:
            answer = "不知道"
    prompt_tokens, completion_tokens = cb.prompt_tokens, cb.completion_tokens
    cost = estimate_cost(prompt_tokens, completion_tokens)
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
    kb_store.add_message(
        message_id=rid,
        conversation_id=conversation_id,
        tenant_id=tenant_id,
        role="assistant",
        content=str(answer),
        citations=[c.model_dump() for c in citations],
        latency_ms=latency,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        refused=refused,
    )
    log_event(
        "api.kb",
        request_id=rid,
        tenant=tenant_id,
        ms=latency,
        docs=len(docs),
        refused=refused,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        cost_cny=cost,
    )
    return AskResponse(
        request_id=rid,
        tenant=tenant_id,
        conversation_id=conversation_id,
        answer=str(answer),
        citations=citations,
        latency_ms=latency,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        cost_cny=cost,
        refused=refused,
    )


class FeedbackRequest(BaseModel):
    message_id: str = Field(..., min_length=1, max_length=64)
    rating: str = Field(..., pattern="^(up|down)$")
    reason: str | None = Field(default=None, max_length=200)


@app.post("/feedback")
def feedback(
    body: FeedbackRequest,
    user: dict[str, Any] = Depends(current_user),
) -> dict[str, Any]:
    """记录点赞/点踩，进入 badcase 池。"""
    tenant_id = str(user["tenant_id"])
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
    user: dict[str, Any] = Depends(current_user),
):
    """SSE 流式问答：meta → citations → token* → done。"""
    check_rate_limit(f"u{user['id']}")
    tenant_id = str(user["tenant_id"])
    try:
        load_tenant(tenant_id)
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"用户所属租户配置缺失: {tenant_id}") from e

    question = body.question.strip()
    rid = uuid.uuid4().hex[:12]
    conversation_id = kb_store.ensure_conversation(
        body.conversation_id, tenant_id, question, user_id=user["id"]
    )
    kb_store.add_message(
        message_id=f"{rid}-u",
        conversation_id=conversation_id,
        tenant_id=tenant_id,
        role="user",
        content=question,
    )
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
        yield _sse(
            "meta",
            {"request_id": rid, "tenant": tenant_id, "conversation_id": conversation_id},
        )
        yield _sse("citations", {"citations": citations})
        if not docs:
            kb_store.add_message(
                message_id=rid,
                conversation_id=conversation_id,
                tenant_id=tenant_id,
                role="assistant",
                content="不知道",
                citations=citations,
                latency_ms=0,
                refused=True,
            )
            yield _sse("token", {"text": "不知道"})
            yield _sse(
                "done",
                {"request_id": rid, "conversation_id": conversation_id, "refused": True, "latency_ms": 0},
            )
            return
        parts: list[str] = []
        prompt_tokens = completion_tokens = 0
        try:
            with get_openai_callback() as cb:
                for chunk in svc._chain().stream({"input": question, "context": context}):
                    text = chunk if isinstance(chunk, str) else getattr(chunk, "content", "")
                    if text:
                        parts.append(str(text))
                        yield _sse("token", {"text": str(text)})
            prompt_tokens, completion_tokens = cb.prompt_tokens, cb.completion_tokens
        except Exception as e:  # noqa: BLE001
            log_event("api.kb_stream", level=40, status="error", error=str(e)[:300], request_id=rid)
            yield _sse("error", {"message": "生成失败，请稍后重试"})
            return
        full = "".join(parts)
        latency = int((time.perf_counter() - started) * 1000)
        refused = full.strip().startswith("不知道")
        cost = estimate_cost(prompt_tokens, completion_tokens)
        kb_store.add_message(
            message_id=rid,
            conversation_id=conversation_id,
            tenant_id=tenant_id,
            role="assistant",
            content=full,
            citations=citations,
            latency_ms=latency,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            refused=refused,
        )
        log_event(
            "api.kb_stream",
            request_id=rid,
            tenant=tenant_id,
            ms=latency,
            docs=len(docs),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_cny=cost,
        )
        yield _sse(
            "done",
            {
                "request_id": rid,
                "conversation_id": conversation_id,
                "refused": refused,
                "latency_ms": latency,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "cost_cny": cost,
            },
        )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


class ConversationPatch(BaseModel):
    title: str | None = Field(default=None, max_length=60)
    pinned: bool | None = None


@app.get("/kb/conversations")
def my_conversations(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    """当前用户的会话列表（置顶优先）。"""
    return {"items": kb_store.list_conversations(str(user["tenant_id"]), user_id=int(user["id"]))}


@app.get("/kb/conversations/{conversation_id}")
def my_conversation(
    conversation_id: str,
    user: dict[str, Any] = Depends(current_user),
) -> dict[str, Any]:
    """读取自己的会话；别人的会话返回 404。"""
    messages = kb_store.get_messages(conversation_id, user_id=int(user["id"]))
    if not messages:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"id": conversation_id, "messages": messages}


@app.patch("/kb/conversations/{conversation_id}")
def my_patch_conversation(
    conversation_id: str,
    body: ConversationPatch,
    user: dict[str, Any] = Depends(current_user),
) -> dict[str, Any]:
    """重命名或置顶自己的会话。"""
    if body.title is None and body.pinned is None:
        raise HTTPException(status_code=400, detail="title 与 pinned 至少提供一个")
    ok = kb_store.update_conversation(
        conversation_id,
        title=body.title,
        pinned=body.pinned,
        user_id=int(user["id"]),
    )
    if not ok:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"ok": True}


@app.delete("/kb/conversations/{conversation_id}")
def my_delete_conversation(
    conversation_id: str,
    user: dict[str, Any] = Depends(current_user),
) -> dict[str, Any]:
    """删除自己的会话。"""
    if not kb_store.delete_conversation(conversation_id, user_id=int(user["id"])):
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"ok": True}


@app.get("/admin/conversations")
def admin_conversations(
    tenant: str = "demo",
    limit: int = 50,
    admin: dict[str, Any] = Depends(require_admin),
) -> dict[str, Any]:
    """列出某租户的最近会话（后台用）。"""
    try:
        load_tenant(tenant)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"租户不存在: {tenant}") from e
    return {"tenant": tenant, "items": kb_store.list_conversations(tenant, min(max(limit, 1), 200))}


@app.get("/admin/conversations/{conversation_id}")
def admin_conversation(
    conversation_id: str,
    admin: dict[str, Any] = Depends(require_admin),
) -> dict[str, Any]:
    """读取某会话的消息明细（面试演示 badcase 用）。"""
    return {"id": conversation_id, "messages": kb_store.get_messages(conversation_id)}


@app.patch("/admin/conversations/{conversation_id}")
def admin_patch_conversation(
    conversation_id: str,
    body: ConversationPatch,
    admin: dict[str, Any] = Depends(require_admin),
) -> dict[str, Any]:
    """重命名或置顶/取消置顶会话。"""
    if body.title is None and body.pinned is None:
        raise HTTPException(status_code=400, detail="title 与 pinned 至少提供一个")
    ok = kb_store.update_conversation(
        conversation_id, title=body.title, pinned=body.pinned
    )
    if not ok:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"ok": True}


@app.delete("/admin/conversations/{conversation_id}")
def admin_delete_conversation(
    conversation_id: str,
    admin: dict[str, Any] = Depends(require_admin),
) -> dict[str, Any]:
    """删除会话及其消息。"""
    if not kb_store.delete_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"ok": True}


class DocAction(BaseModel):
    tenant: str = "demo"
    source: str = Field(..., min_length=1)


@app.get("/admin/docs")
def admin_docs(
    tenant: str = "demo",
    admin: dict[str, Any] = Depends(require_admin),
) -> dict[str, Any]:
    """租户文档列表（含软删除状态）。"""
    try:
        load_tenant(tenant)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"租户不存在: {tenant}") from e
    return {"tenant": tenant, "items": admin_service.list_docs(tenant)}


@app.post("/admin/docs/delete")
def admin_delete_doc(
    body: DocAction,
    admin: dict[str, Any] = Depends(require_admin),
) -> dict[str, Any]:
    """软删除文档：移出检索，保留原文件，可恢复。"""
    try:
        load_tenant(body.tenant)
        return admin_service.delete_doc(body.tenant, body.source, admin["username"])
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@app.post("/admin/docs/restore")
def admin_restore_doc(
    body: DocAction,
    admin: dict[str, Any] = Depends(require_admin),
) -> dict[str, Any]:
    """恢复被软删除的文档（重新入库）。"""
    try:
        load_tenant(body.tenant)
        return admin_service.restore_doc(body.tenant, body.source, admin["username"])
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/admin/audit")
def admin_audit(
    tenant: str = "demo",
    limit: int = 100,
    admin: dict[str, Any] = Depends(require_admin),
) -> dict[str, Any]:
    """文档操作审计日志。"""
    return {"tenant": tenant, "items": admin_service.list_audit(tenant, min(max(limit, 1), 500))}


@app.get("/admin/usage")
def admin_usage(
    tenant: str = "demo",
    days: int = 7,
    admin: dict[str, Any] = Depends(require_admin),
) -> dict[str, Any]:
    """按天统计问答 token 用量与估算成本。"""
    days = min(max(days, 1), 90)
    since = f"-{days} days"
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT date(created_at) AS day,
                      COUNT(*) AS messages,
                      COALESCE(SUM(prompt_tokens), 0) AS prompt_tokens,
                      COALESCE(SUM(completion_tokens), 0) AS completion_tokens
               FROM kb_messages
               WHERE tenant_id = ? AND role = 'assistant' AND created_at >= datetime('now', ?)
               GROUP BY day ORDER BY day""",
            (tenant, since),
        ).fetchall()
        total = conn.execute(
            """SELECT COUNT(*) AS messages,
                      COALESCE(SUM(prompt_tokens), 0) AS prompt_tokens,
                      COALESCE(SUM(completion_tokens), 0) AS completion_tokens
               FROM kb_messages
               WHERE tenant_id = ? AND role = 'assistant' AND created_at >= datetime('now', ?)""",
            (tenant, since),
        ).fetchone()
    summary = dict(total) if total else {"messages": 0, "prompt_tokens": 0, "completion_tokens": 0}
    summary["cost_cny"] = estimate_cost(
        int(summary["prompt_tokens"]), int(summary["completion_tokens"])
    )
    return {"tenant": tenant, "days": days, "items": [dict(r) for r in rows], "total": summary}


@app.post("/admin/docs/upload")
async def admin_upload_doc(
    file: UploadFile = File(...),
    tenant: str = Form("demo"),
    admin: dict[str, Any] = Depends(require_admin),
) -> dict[str, Any]:
    """上传文件并异步入库；返回任务 id。"""
    try:
        load_tenant(tenant)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"租户不存在: {tenant}") from e
    content = await file.read()
    try:
        task_id = admin_service.submit_file(
            tenant, file.filename or "upload.md", content, admin["username"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"task_id": task_id, "tenant": tenant}


class UrlImport(BaseModel):
    tenant: str = "demo"
    url: str = Field(..., min_length=8, max_length=2000)


@app.post("/admin/docs/import_url")
def admin_import_url(
    body: UrlImport,
    admin: dict[str, Any] = Depends(require_admin),
) -> dict[str, Any]:
    """按网址抓取并异步入库；返回任务 id。"""
    try:
        load_tenant(body.tenant)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"租户不存在: {body.tenant}") from e
    try:
        task_id = admin_service.submit_url(body.tenant, body.url, admin["username"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"task_id": task_id, "tenant": body.tenant}


@app.get("/admin/tasks/{task_id}")
def admin_task(
    task_id: str,
    admin: dict[str, Any] = Depends(require_admin),
) -> dict[str, Any]:
    """查询入库任务状态。"""
    task = admin_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task
