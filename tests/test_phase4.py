"""Phase 4：Skills-A 提示词与白名单。"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)


def test_all_skills_a_loadable():
    from agent.tools.middleware import SKILL_WHITELIST
    from utils.prompt_loader import load_skill_prompt, load_system_prompts

    skills_a = [
        "daily_briefing",
        "weekly_review",
        "meeting_minutes",
        "writing_polish",
        "study_tutor",
        "deep_digest",
    ]
    for name in skills_a:
        assert name in SKILL_WHITELIST
        body = load_skill_prompt(name)
        assert len(body) > 40
        assert "系统规则优先" in body or "不可被用户" in body
    main = load_system_prompts()
    assert "不知道" in main


def test_set_skill_tool_rejects_unknown(tmp_path, monkeypatch):
    import services.storage as storage
    from services import user_service
    from agent.tools import agent_tools

    monkeypatch.setattr(storage, "DB_PATH", str(tmp_path / "x.db"))
    storage.ensure_db()
    u = user_service.create_user("SkillUser")
    agent_tools.set_current_user_id(u["id"])
    bad = agent_tools.set_skill.invoke({"skill_name": "hack_system"})
    assert "白名单" in bad or "不知道" in bad
    ok = agent_tools.set_skill.invoke({"skill_name": "weekly_review"})
    assert "weekly_review" in ok
