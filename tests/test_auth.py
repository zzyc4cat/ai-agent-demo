# -*- coding: utf-8 -*-
"""账号与会话归属测试：密码哈希、token 生命周期、会话隔离。"""
from __future__ import annotations

import uuid

from services import auth_service, kb_store
from services.storage import ensure_db, get_conn


def _name() -> str:
    return "t_" + uuid.uuid4().hex[:8]


def _new_user(password: str = "testpass123") -> dict:
    ensure_db()
    return auth_service.create_user(_name(), password)


def test_password_is_hashed() -> None:
    user = _new_user("plaincheck123")
    with get_conn() as conn:
        row = conn.execute(
            "SELECT password_hash FROM users WHERE id = ?", (user["id"],)
        ).fetchone()
    stored = row["password_hash"]
    assert stored and stored != "plaincheck123"
    assert stored.startswith("scrypt$")
    assert auth_service.verify_password("plaincheck123", stored)
    assert not auth_service.verify_password("wrongpass", stored)


def test_login_and_session_lifecycle() -> None:
    name = _name()
    password = "sessionpass123"
    ensure_db()
    auth_service.create_user(name, password)

    assert auth_service.authenticate(name, "bad-password") is None
    user = auth_service.authenticate(name, password)
    assert user and user["username"] == name

    token = auth_service.create_session(int(user["id"]))
    assert auth_service.user_from_token(token)["username"] == name

    auth_service.revoke_session(token)
    assert auth_service.user_from_token(token) is None


def test_conversation_belongs_to_owner() -> None:
    alice = _new_user()
    bob = _new_user()
    cid = kb_store.ensure_conversation(None, "demo", "隔离测试", user_id=alice["id"])
    kb_store.add_message(
        message_id=uuid.uuid4().hex,
        conversation_id=cid,
        tenant_id="demo",
        role="user",
        content="只有 alice 能看到",
    )

    assert kb_store.get_messages(cid, user_id=bob["id"]) == []
    assert len(kb_store.get_messages(cid, user_id=alice["id"])) == 1

    bob_ids = {c["id"] for c in kb_store.list_conversations("demo", user_id=bob["id"])}
    alice_ids = {c["id"] for c in kb_store.list_conversations("demo", user_id=alice["id"])}
    assert cid not in bob_ids and cid in alice_ids

    assert kb_store.delete_conversation(cid, user_id=bob["id"]) is False
    assert kb_store.delete_conversation(cid, user_id=alice["id"]) is True
