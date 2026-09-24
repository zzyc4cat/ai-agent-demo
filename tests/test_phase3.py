"""Phase 3：Tools-A 行为测试（不依赖真实 LLM）。"""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)


@pytest.fixture()
def user_ctx(tmp_path, monkeypatch):
    import services.storage as storage
    from services import user_service
    from agent.tools import agent_tools

    monkeypatch.setattr(storage, "DB_PATH", str(tmp_path / "t.db"))
    storage.ensure_db()
    u = user_service.create_user("ToolUser")
    agent_tools.set_current_user_id(u["id"])
    # sandbox
    ws = tmp_path / "workspace"
    ws.mkdir()
    (ws / "hello.txt").write_text("hello-sandbox", encoding="utf-8")
    monkeypatch.setattr(agent_tools, "_workspace_root", ws.resolve())
    return u


def test_tasks_notes_tools(user_ctx):
    from agent.tools.agent_tools import task_add, task_list, task_complete, note_write, note_search

    r = task_add.invoke({"title": "写周报", "due_at": "2026-09-30", "priority": "P1"})
    assert "写周报" in r
    listed = task_list.invoke({"status": "open"})
    assert "写周报" in listed
    # extract id roughly
    import re

    m = re.search(r"'id':\s*(\d+)", listed)
    assert m
    done = task_complete.invoke({"task_id": int(m.group(1))})
    assert "ok" in done
    note_write.invoke({"title": "t", "body": "番茄工作法笔记"})
    hits = note_search.invoke({"query": "番茄"})
    assert "番茄" in hits


def test_workspace_sandbox(user_ctx):
    from agent.tools.agent_tools import workspace_list, workspace_read, _safe_workspace_path
    import pytest

    assert "hello.txt" in workspace_list.invoke({"relative_dir": ""})
    assert "hello-sandbox" in workspace_read.invoke({"relative_path": "hello.txt"})
    with pytest.raises(ValueError):
        _safe_workspace_path("../secrets.txt")


def test_weather_and_web_degrade_honestly(user_ctx):
    from agent.tools.agent_tools import get_weather, web_search

    w = get_weather.invoke({"city": "上海"})
    assert "不知道" in w or "未启用" in w
    s = web_search.invoke({"query": "pytest"})
    assert "未启用" in s or "不知道" in s


def test_old_mock_tools_removed():
    import agent.tools.agent_tools as t

    assert not hasattr(t, "get_user_id") or "fetch_external_data" not in dir(t)
    assert "fetch_external_data" not in dir(t)
    assert "fill_context_for_report" not in dir(t)
    assert "TOOLS_A" in dir(t)
