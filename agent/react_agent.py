"""Agent 主体：懒加载模型、Checkpointer、skill context、防护入口"""
from __future__ import annotations

import uuid
from typing import Generator, Iterator

from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

from agent.tools.agent_tools import (
    fetch_external_data,
    fill_context_for_report,
    get_current_month,
    get_user_id,
    get_user_location,
    get_weather,
    rag_summarize,
)
from agent.tools.middleware import log_before_model, monitor_tool, skill_prompt_switch
from agent.tools.prompt_guard import get_prompt_guard
from model.factory import get_chat_model, get_model_router
from utils.logger_handler import bind_log_context, clear_log_context, log_event
from utils.prompt_loader import load_system_prompts


class ReactAgent:
    """Agent 调用类（Phase 0：平台骨架；Tools 仍兼容旧工具，后续阶段替换）"""

    def __init__(self, *, model_mode: str = "auto", manual_model_id: str | None = None):
        self.model_mode = model_mode
        self.manual_model_id = manual_model_id
        self._exhausted: set[str] = set()
        self.checkpointer = MemorySaver()
        self._build_agent()

    def _build_agent(self) -> None:
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
            tools=[
                rag_summarize,
                get_weather,
                get_user_location,
                get_user_id,
                get_current_month,
                fetch_external_data,
                fill_context_for_report,
            ],
            middleware=[monitor_tool, log_before_model, skill_prompt_switch],
            checkpointer=self.checkpointer,
        )

    def _thread_id(self, user_id: str, conversation_id: str) -> str:
        return f"{user_id}:{conversation_id}"

    def execute_stream(
        self,
        query: str,
        *,
        user_id: str = "default",
        conversation_id: str = "default",
        skill: str = "default",
        request_id: str | None = None,
    ) -> Generator[str, None, None]:
        rid = request_id or uuid.uuid4().hex[:12]
        thread_id = self._thread_id(user_id, conversation_id)
        bind_log_context(
            request_id=rid,
            user_id=user_id,
            session_id=conversation_id,
            thread_id=thread_id,
            model_id=getattr(self, "active_model_id", "-"),
        )
        log_event("chat.start", query_preview=query[:120], skill=skill)

        guard = get_prompt_guard().check(query)
        if guard.action == "refuse_leak":
            log_event("chat.end", status="guard_refuse")
            yield (guard.message or "无法提供内部系统设定。") + "\n"
            clear_log_context()
            return

        effective_query = query
        if guard.action == "remind_ignore" and guard.message:
            # 不覆盖系统提示；仅在用户侧附加提醒，系统规则仍由 system_prompt/middleware 保证最高优先
            effective_query = f"{guard.message}\n\n用户请求：{query}"

        config = {
            "configurable": {"thread_id": thread_id},
            "recursion_limit": 25,
        }
        input_dict = {"messages": [{"role": "user", "content": effective_query}]}
        context = {"skill": skill or "default", "report": False}

        try:
            for chunk in self.agent.stream(
                input_dict,
                config=config,
                stream_mode="values",
                context=context,
            ):
                latest_message = chunk["messages"][-1]
                content = getattr(latest_message, "content", None)
                if content:
                    yield str(content).strip() + "\n"
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
                    log_event(
                        "model.switch",
                        notify=True,
                        message=f"模型额度或限流，已切换至 {spec.id}，正在重试本轮",
                    )
                    yield f"【系统】模型额度不足或限流，Auto 已切换至 {spec.model_name}，正在重试本轮…\n"
                    yield from self.execute_stream(
                        query,
                        user_id=user_id,
                        conversation_id=conversation_id,
                        skill=skill,
                        request_id=rid,
                    )
                    return
            if self.model_mode == "manual" and router.is_quota_error(e):
                log_event("chat.end", status="quota_manual")
                yield (
                    "【系统】当前手动选择的模型额度不足或被限流，"
                    "不会自动换模。请更换模型或切换到 Auto 模式后重试。\n"
                )
                clear_log_context()
                return
            log_event("chat.end", level=40, status="error", error=str(e))
            yield f"【系统】执行失败：{e}\n"
        finally:
            clear_log_context()
