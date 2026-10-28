# -*- coding: utf-8 -*-
"""知识库会话与消息的持久化（按租户隔离）。"""
from __future__ import annotations

import json
import uuid
from typing import Any

from services.storage import get_conn


def ensure_conversation(conversation_id: str | None, tenant_id: str, title: str) -> str:
    """保证会话存在；不存在则创建，返回会话 id。"""
    cid = conversation_id or uuid.uuid4().hex
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO kb_conversations(id, tenant_id, title) VALUES(?,?,?)",
            (cid, tenant_id, title[:60]),
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


def list_conversations(tenant_id: str, limit: int = 50) -> list[dict[str, Any]]:
    """按租户列出最近会话。"""
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT c.id, c.title, c.created_at,
                      (SELECT COUNT(*) FROM kb_messages m WHERE m.conversation_id = c.id) AS messages
               FROM kb_conversations c
               WHERE c.tenant_id = ?
               ORDER BY c.created_at DESC
               LIMIT ?""",
            (tenant_id, limit),
        ).fetchall()
    return [dict(r) for r in rows]


def get_messages(conversation_id: str) -> list[dict[str, Any]]:
    """读取某会话的全部消息（按时间正序）。"""
    with get_conn() as conn:
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
