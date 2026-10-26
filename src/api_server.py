"""
可选 HTTP API（uvicorn api_server:app）。

GET /health 公开。POST /chat 与 GET /rag/summarize 必须 AGENT_API_KEY
（Bearer 或 X-API-Key）。username 只在鉴权之后选择数据空间，不是口令。
skill 必须在 SKILL_WHITELIST。异常对客户端脱敏。
"""
from __future__ import annotations

import os
import secrets
import uuid
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from agent.react_agent import ReactAgent
from agent.tools.agent_tools import set_current_user_id
from agent.tools.middleware import SKILL_WHITELIST
from services import user_service
from services.storage import ensure_db
from utils.logger_handler import log_event

_agent: ReactAgent | None = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """进程生命周期：启动时确保 SQLite 表存在。"""
    ensure_db()
    yield


app = FastAPI(title="个人综合助手 API", version="0.2.0", lifespan=lifespan)


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


def _validate_skill(skill: str) -> str:
    """校验 skill 是否在白名单，非法则 400。"""
    name = (skill or "default").strip() or "default"
    if name not in SKILL_WHITELIST:
        raise HTTPException(
            status_code=400,
            detail=f"skill 不在白名单：{sorted(SKILL_WHITELIST)}",
        )
    return name


@app.get("/health")
def health() -> dict[str, Any]:
    """健康检查，并告知是否已配置 API Key。"""
    keyed = bool(_expected_api_key())
    return {"status": "ok", "api_key_configured": keyed}


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
