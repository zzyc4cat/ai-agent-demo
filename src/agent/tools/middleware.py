"""中间件：工具监控、模型前日志、动态 Prompt（skill 白名单）、提示词防护钩子"""
from __future__ import annotations

import time
from typing import Callable

from langchain.agents import AgentState
from langchain.agents.middleware import before_model, dynamic_prompt, wrap_tool_call, ModelRequest
from langchain_core.messages import ToolMessage
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.runtime import Runtime
from langgraph.types import Command

from utils.logger_handler import log_event, logger, redact_mapping
from utils.prompt_loader import load_system_prompts, load_skill_prompt

# 仅允许白名单 skill（须有对应 prompts/skills/*.txt，default 用主 Prompt）
SKILL_WHITELIST = frozenset(
    {
        "default",
        "daily_briefing",
        "weekly_review",
        "meeting_minutes",
        "writing_polish",
        "study_tutor",
        "deep_digest",
        "spaced_repetition",
        "error_attribution",
        "study_plan",
    }
)


@wrap_tool_call
def monitor_tool(
    request: ToolCallRequest,
    handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    name = request.tool_call.get("name", "?")
    args = redact_mapping(request.tool_call.get("args") or {})
    log_event("tool.start", tool=name, args=args)
    started = time.perf_counter()
    try:
        result = handler(request)
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        preview = ""
        if isinstance(result, ToolMessage):
            preview = (result.content or "")[:200]
        log_event("tool.end", tool=name, ok=True, elapsed_ms=elapsed_ms, result_preview=preview)
        return result
    except Exception as e:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        log_event("tool.end", level=40, tool=name, ok=False, elapsed_ms=elapsed_ms, error=str(e))
        # 降级：返回错误 ToolMessage，避免整轮直接崩溃
        tool_call_id = request.tool_call.get("id") or name
        return ToolMessage(
            content=f"工具 {name} 暂不可用：{e}",
            tool_call_id=tool_call_id,
        )


@before_model
def log_before_model(state: AgentState, runtime: Runtime):
    messages = state.get("messages") or []
    logger.info("[log_before_model]即将调用模型，带有%d条消息", len(messages))
    if messages:
        last = messages[-1]
        content = getattr(last, "content", "") or ""
        if isinstance(content, str):
            content = content.strip()[:300]
        logger.debug("[log_before_model] %s | %s", type(last).__name__, content)
    return None


@dynamic_prompt
def skill_prompt_switch(request: ModelRequest):
    """优先 ContextVar（set_skill 可中途切换），否则 runtime.context['skill']。"""
    from agent.tools.agent_tools import get_active_skill

    # ContextVar 由 execute_stream / set_skill 写入；缺省时回退 runtime.context
    skill = get_active_skill()
    if not skill or skill == "default":
        ctx = {}
        try:
            ctx = request.runtime.context or {}
        except Exception:
            ctx = {}
        ctx_skill = str(ctx.get("skill") or "").strip()
        if ctx_skill:
            skill = ctx_skill
    skill = (skill or "default").strip() or "default"
    if skill not in SKILL_WHITELIST:
        log_event("skill.reject", skill=skill, reason="not_in_whitelist")
        skill = "default"
    if skill == "default":
        return load_system_prompts()
    try:
        return load_skill_prompt(skill)
    except Exception as e:
        logger.warning("加载 skill=%s 失败，回退主 Prompt: %s", skill, e)
        return load_system_prompts()


# 兼容旧导入名
report_prompt_switch = skill_prompt_switch
