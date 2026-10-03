"""笔记与记忆（按 user_id）。"""
from __future__ import annotations

from services.storage import get_conn, ensure_db


def add_note(user_id: int, title: str, body: str) -> dict:
    title = (title or "").strip() or "未命名笔记"
    body = (body or "").strip()
    if not body:
        raise ValueError("笔记正文不能为空")
    ensure_db()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO notes(user_id, title, body) VALUES (?, ?, ?)",
            (user_id, title, body),
        )
        return {"id": cur.lastrowid, "user_id": user_id, "title": title, "body": body}


def search_notes(user_id: int, query: str, limit: int = 10) -> list[dict]:
    q = f"%{(query or '').strip()}%"
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, title, body, created_at FROM notes "
            "WHERE user_id = ? AND (title LIKE ? OR body LIKE ?) "
            "ORDER BY id DESC LIMIT ?",
            (user_id, q, q, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def add_memory(user_id: int, kind: str, content: str) -> dict:
    content = (content or "").strip()
    if not content:
        raise ValueError("记忆内容不能为空")
    ensure_db()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO memories(user_id, kind, content) VALUES (?, ?, ?)",
            (user_id, kind or "episodic", content),
        )
        return {"id": cur.lastrowid, "kind": kind, "content": content}


def list_memories(user_id: int, kind: str | None = None, limit: int = 20) -> list[dict]:
    with get_conn() as conn:
        if kind:
            rows = conn.execute(
                "SELECT * FROM memories WHERE user_id = ? AND kind = ? ORDER BY id DESC LIMIT ?",
                (user_id, kind, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM memories WHERE user_id = ? ORDER BY id DESC LIMIT ?",
                (user_id, limit),
            ).fetchall()
        return [dict(r) for r in rows]
