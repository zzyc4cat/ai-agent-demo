# -*- coding: utf-8 -*-
"""知识库会话与消息的持久化（按租户隔离）。"""
from __future__ import annotations

import json
import uuid
from typing import Any

from services.storage import get_conn


def ensure_conversation(
    conversation_id: str | None,
    tenant_id: str,
    title: str,
    user_id: int | None = None,
) -> str:
    """保证会话存在；不存在则创建，返回会话 id。"""
    cid = conversation_id or uuid.uuid4().hex
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO kb_conversations(id, tenant_id, user_id, title) VALUES(?,?,?,?)",
            (cid, tenant_id, user_id, title[:60]),
        )
    return cid


def add_message(
    *,
    message_id: str,
    conversation_id: str,
    tenant_id: str,
    role: str,
    content: str,
    citations: list[dict[str, Any]] | None = None,
    latency_ms: int | None = None,
    refused: bool = False,
) -> None:
    """写入一条消息；同一 id 只写一次。"""
    with get_conn() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO kb_messages
               (id, conversation_id, tenant_id, role, content, citations_json, latency_ms, refused)
               VALUES(?,?,?,?,?,?,?,?)""",
            (
                message_id,
                conversation_id,
                tenant_id,
                role,
                content,
                json.dumps(citations or [], ensure_ascii=False),
                latency_ms,
                1 if refused else 0,
            ),
        )


def list_conversations(
    tenant_id: str,
    limit: int = 50,
    user_id: int | None = None,
) -> list[dict[str, Any]]:
    """按租户列出会话；给定 user_id 时只返回该用户的。"""
    sql = """SELECT c.id, c.title, c.pinned, c.created_at, c.user_id,
                    (SELECT COUNT(*) FROM kb_messages m WHERE m.conversation_id = c.id) AS messages
             FROM kb_conversations c
             WHERE c.tenant_id = ?"""
    args: list[Any] = [tenant_id]
    if user_id is not None:
        sql += " AND c.user_id = ?"
        args.append(user_id)
    sql += " ORDER BY c.pinned DESC, c.created_at DESC LIMIT ?"
    args.append(limit)
    with get_conn() as conn:
        rows = conn.execute(sql, args).fetchall()
    return [dict(r) for r in rows]


def update_conversation(
    conversation_id: str,
    *,
    title: str | None = None,
    pinned: bool | None = None,
    user_id: int | None = None,
) -> bool:
    """重命名或置顶/取消置顶；返回是否命中。"""
    sets: list[str] = []
    args: list[Any] = []
    if title is not None:
        sets.append("title = ?")
        args.append(title[:60])
    if pinned is not None:
        sets.append("pinned = ?")
        args.append(1 if pinned else 0)
    if not sets:
        return False
    sql = f"UPDATE kb_conversations SET {', '.join(sets)} WHERE id = ?"
    args.append(conversation_id)
    if user_id is not None:
        sql += " AND user_id = ?"
        args.append(user_id)
    with get_conn() as conn:
        cur = conn.execute(sql, args)
        return cur.rowcount > 0


def delete_conversation(conversation_id: str, user_id: int | None = None) -> bool:
    """删除会话及其消息；返回是否命中。"""
    with get_conn() as conn:
        if user_id is not None:
            owned = conn.execute(
                "SELECT 1 FROM kb_conversations WHERE id = ? AND user_id = ?",
                (conversation_id, user_id),
            ).fetchone()
            if not owned:
                return False
        conn.execute("DELETE FROM kb_messages WHERE conversation_id = ?", (conversation_id,))
        cur = conn.execute("DELETE FROM kb_conversations WHERE id = ?", (conversation_id,))
        return cur.rowcount > 0


def get_messages(conversation_id: str, user_id: int | None = None) -> list[dict[str, Any]]:
    """读取某会话的全部消息；给定 user_id 时校验归属。"""
    with get_conn() as conn:
        if user_id is not None:
            owned = conn.execute(
                "SELECT 1 FROM kb_conversations WHERE id = ? AND user_id = ?",
                (conversation_id, user_id),
            ).fetchone()
            if not owned:
                return []
        rows = conn.execute(
            """SELECT id, role, content, citations_json, latency_ms, refused, created_at
               FROM kb_messages WHERE conversation_id = ?
               ORDER BY created_at ASC""",
            (conversation_id,),
        ).fetchall()
    out: list[dict[str, Any]] = []
    for r in rows:
        item = dict(r)
        try:
            item["citations"] = json.loads(item.pop("citations_json") or "[]")
        except Exception:
            item["citations"] = []
        out.append(item)
    return out
