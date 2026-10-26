"""
LangGraph ReAct Agent 封装。

被 app.py（Streamlit）与 api_server 调用。一轮对话：
1. 解析 user_id → SQLite 主键，写入工具 ContextVar
2. 白名单 skill 写入「按用户」的运行时状态
3. PromptGuard：泄露则直接拒答；忽略规则则在用户消息前加安全提醒
4. stream_mode=values 过滤 ToolMessage / 中间 tool_calls，只 yield 最终文本
5. Auto 额度错误则换模重建 agent 并重试本轮；手动模式不换模
"""
from __future__ import annotations

import uuid
from typing import Generator

from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

from agent.tools.agent_tools import TOOLS_A, set_active_skill, set_current_user_id
from agent.tools.tools_b import TOOLS_B
from agent.tools.middleware import SKILL_WHITELIST, log_before_model, monitor_tool, skill_prompt_switch
from agent.tools.prompt_guard import get_prompt_guard
from model.factory import get_model_router
from services import user_service
from utils.logger_handler import bind_log_context, clear_log_context, log_event
from utils.path_tool import get_abs_path
from utils.prompt_loader import load_system_prompts


def _make_checkpointer():
    """优先 SQLite 持久化；失败则回退 MemorySaver。"""
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
        import sqlite3

        path = get_abs_path("storage/checkpoints.db")
        conn = sqlite3.connect(path, check_same_thread=False)
        return SqliteSaver(conn)
    except Exception as e:
        log_event("checkpointer", level=30, status="fallback_memory", error=str(e)[:120])
        return MemorySaver()


class ReactAgent:
    """单用户会话上的 ReAct 循环；thread_id = {user_pk}:{conversation_id}。"""
    def __init__(self, *, model_mode: str = "auto", manual_model_id: str | None = None):
        """按 Auto/手动模式构建 LangGraph Agent，并挂上 SQLite/内存 Checkpointer。"""
        self.model_mode = model_mode
        self.manual_model_id = manual_model_id
        self._exhausted: set[str] = set()
        self.checkpointer = _make_checkpointer()
        self._build_agent()

    def _build_agent(self) -> None:
        """用当前模型与全部工具、中间件创建（或额度换模后重建）agent。"""
        chat_model, spec = get_model_router().get_chat_model(
            mode=self.model_mode,
            manual_model_id=self.manual_model_id,
            exhausted_ids=set(self._exhausted),
        )
        self.active_model_id = spec.id
        bind_log_context(model_id=spec.id)
        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompts(),
            tools=TOOLS_A + TOOLS_B,
            middleware=[monitor_tool, log_before_model, skill_prompt_switch],
            checkpointer=self.checkpointer,
        )

    def _thread_id(self, user_id: str, conversation_id: str) -> str:
        """拼 Checkpointer 线程键，保证不同用户/会话状态隔离。"""
        return f"{user_id}:{conversation_id}"

    def _resolve_user_pk(self, user_id: str | int) -> int:
        """将会话中的 user 标识解析为 SQLite 用户主键。"""
        if isinstance(user_id, int):
            return user_id
        text = str(user_id).strip()
        if text.isdigit():
            return int(text)
        from services.storage import ensure_db

        ensure_db()
        found = user_service.find_user_by_name(text)
        if found:
            return int(found["id"])
        if text in ("default", "", "anonymous"):
            last = user_service.get_last_user()
            if last:
                return int(last["id"])
            created = user_service.switch_or_create("default")
            return int(created["id"])
        created = user_service.switch_or_create(text)
        return int(created["id"])

    def execute_stream(
        self,
        query: str,
        *,
        user_id: str = "default",
        conversation_id: str = "default",
        skill: str = "default",
        request_id: str | None = None,
    ) -> Generator[str, None, None]:
        """
        执行一轮用户问题并逐步 yield 展示文本。

        空最终答复时 yield「不知道」。异常不对用户回传堆栈。
        """
        rid = request_id or uuid.uuid4().hex[:12]
        user_pk = self._resolve_user_pk(user_id)
        set_current_user_id(user_pk)
        ctx_skill = (skill or "default").strip() or "default"
        if ctx_skill not in SKILL_WHITELIST:
            ctx_skill = "default"
        set_active_skill(ctx_skill)
        thread_id = self._thread_id(str(user_pk), conversation_id)
        bind_log_context(
            request_id=rid,
            user_id=str(user_pk),
            session_id=conversation_id,
            thread_id=thread_id,
            model_id=getattr(self, "active_model_id", "-"),
        )
        log_event("chat.start", query_preview=query[:120], skill=ctx_skill)

        guard = get_prompt_guard().check(query)
        if guard.action == "refuse_leak":
            log_event("chat.end", status="guard_refuse")
            yield (guard.message or "无法提供内部系统设定。") + "\n"
            clear_log_context()
            return

        effective_query = query
        if guard.action == "remind_ignore" and guard.message:
            effective_query = f"{guard.message}\n\n用户请求：{query}"

        config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 25}
        input_dict = {"messages": [{"role": "user", "content": effective_query}]}
        context = {"skill": ctx_skill, "report": False}

        try:
            from langchain_core.messages import AIMessage, ToolMessage

            last_ai = ""
            for chunk in self.agent.stream(
                input_dict,
                config=config,
                stream_mode="values",
                context=context,
            ):
                latest_message = chunk["messages"][-1]
                # 不对用户展示工具原始返回（含 UNTRUSTED 标记）
                if isinstance(latest_message, ToolMessage):
                    continue
                if isinstance(latest_message, AIMessage):
                    # 仍有 tool_calls 的中间轮不作为最终答复刷屏
                    if getattr(latest_message, "tool_calls", None):
                        continue
                    content = getattr(latest_message, "content", None)
                    if not content:
                        continue
                    text = str(content).strip()
                    if "<<<UNTRUSTED_DATA" in text:
                        continue
                    if text and text != last_ai:
                        last_ai = text
                        yield text + "\n"
            if not last_ai:
                yield "不知道\n"
            log_event("chat.end", status="ok")
        except Exception as e:
            router = get_model_router()
            if self.model_mode == "auto" and router.is_quota_error(e):
                nxt = router.next_auto_model(self.active_model_id, self._exhausted)
                if nxt is not None:
                    _, spec = nxt
                    self._exhausted.add(self.active_model_id)
                    self.active_model_id = spec.id
                    self._build_agent()
                    yield f"【系统】模型额度不足或限流，Auto 已切换至 {spec.model_name}，正在重试本轮…\n"
                    yield from self.execute_stream(
                        query,
                        user_id=str(user_pk),
                        conversation_id=conversation_id,
                        skill=skill,
                        request_id=rid,
                    )
                    return
            if self.model_mode == "manual" and router.is_quota_error(e):
                yield (
                    "【系统】当前手动选择的模型额度不足或被限流，不会自动换模。"
                    "请更换模型或切换到 Auto 模式后重试。\n"
                )
                clear_log_context()
                return
            log_event("chat.end", level=40, status="error", error=str(e))
            yield "【系统】执行失败，请稍后重试或查看服务端日志。\n"
        finally:
            clear_log_context()
