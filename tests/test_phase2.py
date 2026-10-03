"""Phase 2：用户隔离与任务/笔记存储。"""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, ROOT)
sys.path.insert(0, SRC)


@pytest.fixture()
def fresh_db(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    import services.storage as storage

    monkeypatch.setattr(storage, "DB_PATH", str(db))
    storage.ensure_db()
    return storage


def test_user_create_switch_isolation(fresh_db):
    from services import user_service, task_service

    a = user_service.create_user("Alice")
    b = user_service.create_user("Bob")
    task_service.add_task(a["id"], "Alice任务A")
    task_service.add_task(b["id"], "Bob任务B")
    assert len(task_service.list_tasks(a["id"])) == 1
    assert task_service.list_tasks(a["id"])[0]["title"] == "Alice任务A"
    assert task_service.list_tasks(b["id"])[0]["title"] == "Bob任务B"
    with pytest.raises(ValueError):
        user_service.create_user("alice")  # 大小写不敏感唯一
    switched = user_service.switch_or_create("Bob")
    assert switched["id"] == b["id"]


def test_notes_and_memory(fresh_db):
    from services import user_service, note_service

    u = user_service.create_user("Carol")
    note_service.add_note(u["id"], "标题", "正文番茄工作法")
    hits = note_service.search_notes(u["id"], "番茄")
    assert len(hits) == 1
    note_service.add_memory(u["id"], "preference", "默认城市=上海")
    mems = note_service.list_memories(u["id"])
    assert mems[0]["content"].startswith("默认城市")


def test_thread_id_format():
    from agent.react_agent import ReactAgent

    agent = object.__new__(ReactAgent)
    assert agent._thread_id("9", "conv") == "9:conv"
