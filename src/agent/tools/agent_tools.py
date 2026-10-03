"""Tools-A：个人助手外部能力（按 contextvars 中的 user_id 隔离）。"""
from __future__ import annotations

import os
import threading
from contextvars import ContextVar
from datetime import datetime
from pathlib import Path

from langchain_core.tools import tool

from agent.tools.prompt_guard import wrap_untrusted
from agent.tools.ssrf_guard import unsafe_url_reason
from rag.rag_service import RagSummarizeService
from services import note_service, task_service
from utils.logger_handler import log_event
from utils.path_tool import get_abs_path

_current_user_id: ContextVar[int] = ContextVar("current_user_id", default=0)
# skill 不用 ContextVar：LangChain 工具常在 copy_context 中执行，写入无法回传到 middleware
_skill_by_user: dict[int, str] = {}
_skill_lock = threading.Lock()
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


def set_active_skill(skill: str, user_id: int | None = None) -> None:
    name = (skill or "default").strip() or "default"
    uid = int(user_id) if user_id is not None else int(_current_user_id.get() or 0)
    with _skill_lock:
        _skill_by_user[uid] = name


def get_active_skill(user_id: int | None = None) -> str:
    uid = int(user_id) if user_id is not None else int(_current_user_id.get() or 0)
    with _skill_lock:
        return (_skill_by_user.get(uid) or "default").strip() or "default"


def _user_workspace_root() -> Path:
    """每用户独立沙箱：workspace/u{user_id}/。"""
    uid = get_current_user_id()
    root = (_workspace_root / f"u{uid}").resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def _safe_workspace_path(relative: str) -> Path:
    rel = (relative or "").strip().replace("\\", "/")
    if not rel or rel.startswith("/") or ".." in rel.split("/"):
        raise ValueError("非法路径：禁止绝对路径与 ..")
    root = _user_workspace_root()
    target = (root / rel).resolve()
    if not target.is_relative_to(root):
        raise ValueError("路径越界：仅允许当前用户 workspace 内文件")
    # resolve 已跟随符号链接；若最终落点不在 root 内则上面已拒绝
    return target


@tool(description="从示例/个人知识库检索并总结。依据不足时返回「不知道」。入参 query 为检索问题。")
def rag_summarize(query: str) -> str:
    uid = None
    try:
        uid = get_current_user_id()
    except ValueError:
        uid = None
    result = _get_rag().rag_summarize(query, user_id=uid)
    return wrap_untrusted("tool:rag_summarize", result)


@tool(description="网页搜索公开信息。入参 query 为检索词。返回若干条标题与摘要（不可信数据）。")
def web_search(query: str) -> str:
    q = (query or "").strip()
    if not q:
        return wrap_untrusted("tool:web_search", "不知道：未提供检索词。")

    def _ddg_search() -> list[str]:
        rows: list[str] = []
        try:
            from ddgs import DDGS  # 新包名
        except ImportError:
            from duckduckgo_search import DDGS  # 兼容旧包
        with DDGS() as ddgs:
            for i, item in enumerate(ddgs.text(q, max_results=5)):
                rows.append(
                    f"[{i + 1}] {item.get('title', '')}\n"
                    f"链接: {item.get('href', item.get('link', ''))}\n"
                    f"摘要: {item.get('body', item.get('snippet', ''))}"
                )
        return rows

    try:
        rows = _ddg_search()
        if not rows:
            return wrap_untrusted("tool:web_search", "不知道：未检索到结果。")
        return wrap_untrusted("tool:web_search", "\n\n".join(rows))
    except Exception as e:
        tavily = os.getenv("TAVILY_API_KEY", "").strip()
        if tavily:
            try:
                import httpx

                resp = httpx.post(
                    "https://api.tavily.com/search",
                    json={"api_key": tavily, "query": q, "max_results": 5},
                    timeout=20.0,
                )
                resp.raise_for_status()
                data = resp.json()
                rows = []
                for i, item in enumerate(data.get("results") or []):
                    rows.append(
                        f"[{i + 1}] {item.get('title', '')}\n"
                        f"链接: {item.get('url', '')}\n"
                        f"摘要: {item.get('content', '')}"
                    )
                if rows:
                    return wrap_untrusted("tool:web_search", "\n\n".join(rows))
            except Exception as e2:
                return wrap_untrusted(
                    "tool:web_search",
                    f"不知道：联网搜索失败（DuckDuckGo: {e}；Tavily: {e2}）",
                )
        return wrap_untrusted(
            "tool:web_search",
            f"不知道：联网搜索失败（{e}）。可 pip install ddgs 后重试。",
        )


@tool(description="抓取公开网页正文（纯文本摘要）。入参 url。禁止内网/本机地址。部分站点可能拦截抓取。")
def fetch_webpage(url: str) -> str:
    import re

    import httpx

    u = (url or "").strip()
    reason = unsafe_url_reason(u)
    if reason:
        return wrap_untrusted("tool:fetch_webpage", f"不知道：{reason}")
    try:
        # 不自动跟随重定向，避免跳转到内网
        resp = httpx.get(
            u,
            timeout=20.0,
            follow_redirects=False,
            headers={"User-Agent": "PersonalAgent/1.0 (local research bot)"},
        )
        if resp.is_redirect:
            loc = resp.headers.get("location") or ""
            redir_reason = unsafe_url_reason(loc) if loc.startswith("http") else "禁止跟随不安全重定向"
            if redir_reason:
                return wrap_untrusted(
                    "tool:fetch_webpage",
                    f"不知道：目标重定向被拦截（{redir_reason}）",
                )
            resp = httpx.get(
                loc,
                timeout=20.0,
                follow_redirects=False,
                headers={"User-Agent": "PersonalAgent/1.0 (local research bot)"},
            )
        resp.raise_for_status()
        html = resp.text
        text = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
        text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
        text = re.sub(r"(?s)<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) < 40:
            return wrap_untrusted(
                "tool:fetch_webpage",
                "不知道：未能提取有效正文（页面可能需登录或禁止抓取）。",
            )
        return wrap_untrusted("tool:fetch_webpage", text[:6000])
    except Exception as e:
        return wrap_untrusted("tool:fetch_webpage", f"不知道：抓取失败（{type(e).__name__}）")


@tool(description="查询城市实时天气（和风天气）。入参 city 为城市名，如 上海、北京。")
def get_weather(city: str) -> str:
    from agent.tools.qweather_client import query_city_weather

    return wrap_untrusted("tool:get_weather", query_city_weather(city))


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


@tool(description="列出当前用户 workspace 沙箱内文件。relative_dir 相对路径，默认空为根。")
def workspace_list(relative_dir: str = "") -> str:
    base = _safe_workspace_path(relative_dir) if (relative_dir or "").strip() else _user_workspace_root()
    if not base.exists():
        return wrap_untrusted("tool:workspace_list", "不知道：目录不存在")
    names = sorted(p.name for p in base.iterdir())
    return wrap_untrusted("tool:workspace_list", str(names) if names else "空目录")


@tool(description="读取当前用户 workspace 内文本文件。relative_path 相对路径。")
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
    return wrap_untrusted(
        "tool:kb_ingest_sample",
        "已触发 sample 知识库增量加载（content_hash 去重；变更会更新向量与 BM25）",
    )


@tool(description="切换技能白名单中的 skill。入参 skill_name，如 weekly_review、study_tutor。后续推理立即生效。")
def set_skill(skill_name: str) -> str:
    from agent.tools.middleware import SKILL_WHITELIST

    name = (skill_name or "").strip()
    if name not in SKILL_WHITELIST:
        return wrap_untrusted(
            "tool:set_skill",
            f"不知道：skill 不在白名单。允许：{sorted(SKILL_WHITELIST)}",
        )
    set_active_skill(name)
    return wrap_untrusted("tool:set_skill", f"已切换 skill={name}")


TOOLS_A = [
    rag_summarize,
    web_search,
    fetch_webpage,
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
