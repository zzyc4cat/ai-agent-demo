"""Tools-A：个人助手外部能力（按 contextvars 中的 user_id 隔离）。"""
from __future__ import annotations

import os
from contextvars import ContextVar
from datetime import datetime
from pathlib import Path

from langchain_core.tools import tool

from agent.tools.prompt_guard import wrap_untrusted
from rag.rag_service import RagSummarizeService
from services import note_service, task_service, user_service
from utils.logger_handler import log_event, logger
from utils.path_tool import get_abs_path

_current_user_id: ContextVar[int] = ContextVar("current_user_id", default=0)
_workspace_root = Path(get_abs_path("workspace")).resolve()

_rag: RagSummarizeService | None = None


def _get_rag() -> RagSummarizeService:
    global _rag
    if _rag is None:
        _rag = RagSummarizeService()
    return _rag


def set_current_user_id(user_id: int) -> None:
    _current_user_id.set(int(user_id))


def get_current_user_id() -> int:
    uid = _current_user_id.get()
    if not uid:
        raise ValueError("当前无有效用户，请先创建或切换本地用户")
    return uid


def _safe_workspace_path(relative: str) -> Path:
    rel = (relative or "").strip().replace("\\", "/")
    if not rel or rel.startswith("/") or ".." in rel.split("/"):
        raise ValueError("非法路径：禁止绝对路径与 ..")
    target = (_workspace_root / rel).resolve()
    if not str(target).startswith(str(_workspace_root)):
        raise ValueError("路径越界：仅允许 workspace/ 内文件")
    return target


@tool(description="从示例/个人知识库检索并总结。依据不足时返回「不知道」。入参 query 为检索问题。")
def rag_summarize(query: str) -> str:
    result = _get_rag().rag_summarize(query)
    return wrap_untrusted("tool:rag_summarize", result)


@tool(description="网页搜索（未配置搜索 Key 时返回未启用说明）。入参 query。")
def web_search(query: str) -> str:
    # MVP：无 Key 时明确降级；有 TAVILY_API_KEY 可扩展
    if not os.getenv("TAVILY_API_KEY", "").strip():
        msg = "web_search 未启用：请在 .env 配置 TAVILY_API_KEY。当前不知道公开网页检索结果。"
        return wrap_untrusted("tool:web_search", msg)
    return wrap_untrusted("tool:web_search", "搜索后端尚未接通，不知道结果。")


@tool(description="查询城市天气。未配置天气服务时说明未启用。入参 city。")
def get_weather(city: str) -> str:
    city = (city or "").strip()
    if not city:
        return wrap_untrusted("tool:get_weather", "不知道：未提供城市名。")
    # MVP 无第三方 Key：返回明确未启用，避免假数据冒充实况
    msg = (
        f"天气服务未启用（无 API Key）。不知道「{city}」的真实天气。"
        "请配置天气 API 或自行查询。"
    )
    return wrap_untrusted("tool:get_weather", msg)


@tool(description="返回当前本地日期时间（ISO 格式）与星期。无入参。")
def datetime_now() -> str:
    now = datetime.now().astimezone()
    text = now.strftime("%Y-%m-%d %H:%M:%S %Z %A")
    return wrap_untrusted("tool:datetime_now", text)


@tool(description="新增待办。入参 title 必填；due_at 可选 YYYY-MM-DD；priority 可选 P0/P1/P2。")
def task_add(title: str, due_at: str = "", priority: str = "") -> str:
    uid = get_current_user_id()
    task = task_service.add_task(uid, title, due_at or None, priority or None)
    return wrap_untrusted("tool:task_add", str(task))


@tool(description="列出当前用户待办。status=open|done|all，默认 open。")
def task_list(status: str = "open") -> str:
    uid = get_current_user_id()
    rows = task_service.list_tasks(uid, status=status or "open")
    if not rows:
        return wrap_untrusted("tool:task_list", "无待办")
    return wrap_untrusted("tool:task_list", str(rows))


@tool(description="将待办标为完成。入参 task_id 为整数。")
def task_complete(task_id: int) -> str:
    uid = get_current_user_id()
    ok = task_service.complete_task(uid, int(task_id))
    return wrap_untrusted("tool:task_complete", "ok" if ok else "不知道：未找到该待办或不属于当前用户")


@tool(description="写入笔记。入参 title 与 body。")
def note_write(title: str, body: str) -> str:
    uid = get_current_user_id()
    note = note_service.add_note(uid, title, body)
    return wrap_untrusted("tool:note_write", str({"id": note["id"], "title": note["title"]}))


@tool(description="搜索当前用户笔记。入参 query。")
def note_search(query: str) -> str:
    uid = get_current_user_id()
    hits = note_service.search_notes(uid, query)
    if not hits:
        return wrap_untrusted("tool:note_search", "不知道：未找到匹配笔记")
    return wrap_untrusted("tool:note_search", str(hits))


@tool(description="写入长期记忆片段。入参 kind（如 preference/episodic）与 content。")
def memory_set(kind: str, content: str) -> str:
    uid = get_current_user_id()
    mem = note_service.add_memory(uid, kind, content)
    return wrap_untrusted("tool:memory_set", str(mem))


@tool(description="读取长期记忆。入参 kind 可选；空则返回最近记忆。")
def memory_get(kind: str = "") -> str:
    uid = get_current_user_id()
    rows = note_service.list_memories(uid, kind or None)
    if not rows:
        return wrap_untrusted("tool:memory_get", "不知道：暂无记忆")
    return wrap_untrusted("tool:memory_get", str(rows))


@tool(description="列出 workspace/ 沙箱内文件。relative_dir 相对路径，默认空为根。")
def workspace_list(relative_dir: str = "") -> str:
    base = _safe_workspace_path(relative_dir) if (relative_dir or "").strip() else _workspace_root
    if not base.exists():
        return wrap_untrusted("tool:workspace_list", "不知道：目录不存在")
    names = sorted(p.name for p in base.iterdir())
    return wrap_untrusted("tool:workspace_list", str(names) if names else "空目录")


@tool(description="读取 workspace/ 内文本文件。relative_path 相对路径。")
def workspace_read(relative_path: str) -> str:
    path = _safe_workspace_path(relative_path)
    if not path.is_file():
        return wrap_untrusted("tool:workspace_read", "不知道：文件不存在")
    text = path.read_text(encoding="utf-8", errors="replace")
    return wrap_untrusted("tool:workspace_read", text[:8000])


@tool(description="将 data/sample 或已允许目录的知识重新入库（示例库）。无入参。")
def kb_ingest_sample() -> str:
    from rag.vector_store import VectorStoreService

    VectorStoreService().load_document()
    log_event("kb.ingest", corpus="sample")
    return wrap_untrusted("tool:kb_ingest_sample", "已触发 sample 知识库加载（MD5 去重，已存在则跳过）")


@tool(description="切换技能白名单中的 skill。入参 skill_name，如 weekly_review、study_tutor。")
def set_skill(skill_name: str) -> str:
    from agent.tools.middleware import SKILL_WHITELIST

    name = (skill_name or "").strip()
    if name not in SKILL_WHITELIST:
        return wrap_untrusted(
            "tool:set_skill",
            f"不知道：skill 不在白名单。允许：{sorted(SKILL_WHITELIST)}",
        )
    # 实际切换由调用方写入 runtime context；此处返回确认供模型知晓
    return wrap_untrusted("tool:set_skill", f"已请求切换 skill={name}（由会话 context 生效）")


TOOLS_A = [
    rag_summarize,
    web_search,
    get_weather,
    datetime_now,
    task_add,
    task_list,
    task_complete,
    note_write,
    note_search,
    memory_set,
    memory_get,
    workspace_list,
    workspace_read,
    kb_ingest_sample,
    set_skill,
]
