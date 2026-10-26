"""会话置顶 / 重命名 / 删除。"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, ROOT)
sys.path.insert(0, SRC)


def test_pin_rename_delete_no_overlap(tmp_path, monkeypatch):
    """验证置顶/重命名/删除不会把会话列重复。"""
    import services.storage as storage
    from services import user_service, chat_service

    monkeypatch.setattr(storage, "DB_PATH", str(tmp_path / "pin.db"))
    storage.ensure_db()
    u = user_service.create_user("PinUser")
    a = chat_service.new_conversation_id()
    b = chat_service.new_conversation_id()
    chat_service.ensure_conversation(u["id"], a, "会话A")
    chat_service.ensure_conversation(u["id"], b, "会话B")
    chat_service.set_pinned(u["id"], a, True)

    pinned = chat_service.list_conversations(u["id"], pinned=True)
    recent = chat_service.list_conversations(u["id"], pinned=False)
    pinned_ids = {c["id"] for c in pinned}
    recent_ids = {c["id"] for c in recent}
    assert a in pinned_ids and a not in recent_ids
    assert b in recent_ids and b not in pinned_ids
    assert pinned_ids.isdisjoint(recent_ids)

    chat_service.rename_conversation(u["id"], a, "置顶改名")
    assert chat_service.list_conversations(u["id"], pinned=True)[0]["title"] == "置顶改名"

    chat_service.set_pinned(u["id"], a, False)
    pinned2 = {c["id"] for c in chat_service.list_conversations(u["id"], pinned=True)}
    recent2 = {c["id"] for c in chat_service.list_conversations(u["id"], pinned=False)}
    assert a not in pinned2 and a in recent2
    assert pinned2.isdisjoint(recent2)

    chat_service.append_message(u["id"], b, "user", "hi")
    assert chat_service.delete_conversation(u["id"], b)
    assert chat_service.load_messages(u["id"], b) == []
    assert b not in {c["id"] for c in chat_service.list_conversations(u["id"], pinned=None)}


def test_list_conversations_accepts_pinned_kwarg(tmp_path, monkeypatch):
    """list_conversations 必须接受 pinned 参数。"""
    import services.storage as storage
    from services import user_service, chat_service

    monkeypatch.setattr(storage, "DB_PATH", str(tmp_path / "kw.db"))
    storage.ensure_db()
    u = user_service.create_user("KwUser")
    cid = chat_service.new_conversation_id()
    chat_service.ensure_conversation(u["id"], cid, "x")
    assert isinstance(chat_service.list_conversations(u["id"], pinned=True), list)
    assert isinstance(chat_service.list_conversations(u["id"], pinned=False), list)


def test_ui_menu_closes_after_action_pattern():
    """检查 app.py 在菜单操作后关闭 popover。"""
    text = open(os.path.join(ROOT, "app.py"), encoding="utf-8").read()
    assert "_close_conv_menu" in text
    assert "open_conv_menu" in text
    assert "menu_epoch" in text
    assert "会话操作" in text
    assert "重命名" in text
    assert "置顶此对话" in text
    assert "取消置顶" in text
    assert "删除此对话" in text
    assert 'st.subheader("置顶")' in text
    assert 'st.subheader("最近")' in text
