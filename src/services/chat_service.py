"""
会话列表与消息落库（Streamlit 历史）。与 LangGraph Checkpointer 互补：
这里给人看的对话菜单；Checkpointer 存 Agent 图状态。
"""
from __future__ import annotations

import uuid

from services.storage import ensure_db, get_conn


def _ensure_chat_tables() -> None:
    """确保会话与消息表存在，并补 pinned/updated_at 列。"""
    ensure_db()
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                title TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                PRIMARY KEY (user_id, id)
            )
            """
        )
        cols = {r[1] for r in conn.execute("PRAGMA table_info(conversations)").fetchall()}
        if "updated_at" not in cols:
            conn.execute(
                "ALTER TABLE conversations ADD COLUMN updated_at TEXT NOT NULL DEFAULT (datetime('now'))"
            )
        if "pinned" not in cols:
            conn.execute(
                "ALTER TABLE conversations ADD COLUMN pinned INTEGER NOT NULL DEFAULT 0"
            )


def new_conversation_id() -> str:
    """生成短会话 id。"""
    return uuid.uuid4().hex[:12]


def ensure_conversation(user_id: int, conversation_id: str, title: str | None = None) -> None:
    """没有则插入会话行，有则刷新 updated_at。"""
    _ensure_chat_tables()
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id FROM conversations WHERE user_id=? AND id=?",
            (user_id, conversation_id),
        ).fetchone()
        if row:
            conn.execute(
                "UPDATE conversations SET updated_at=datetime('now') WHERE user_id=? AND id=?",
                (user_id, conversation_id),
            )
        else:
            conn.execute(
                "INSERT INTO conversations(id, user_id, title, updated_at, created_at, pinned) "
                "VALUES (?,?,?,datetime('now'),datetime('now'),0)",
                (conversation_id, user_id, title or "新对话"),
            )


def list_conversations(
    user_id: int,
    pinned: bool | None = None,
    limit: int = 50,
) -> list[dict]:
    """pinned=True 仅置顶；False 仅非置顶；None 全部。两类互斥无重复。"""
    _ensure_chat_tables()
    with get_conn() as conn:
        if pinned is True:
            rows = conn.execute(
                "SELECT id, title, updated_at, created_at, IFNULL(pinned,0) AS pinned FROM conversations "
                "WHERE user_id=? AND IFNULL(pinned,0)=1 ORDER BY updated_at DESC LIMIT ?",
                (user_id, limit),
            ).fetchall()
        elif pinned is False:
            rows = conn.execute(
                "SELECT id, title, updated_at, created_at, IFNULL(pinned,0) AS pinned FROM conversations "
                "WHERE user_id=? AND IFNULL(pinned,0)=0 ORDER BY updated_at DESC LIMIT ?",
                (user_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, title, updated_at, created_at, IFNULL(pinned,0) AS pinned FROM conversations "
                "WHERE user_id=? ORDER BY IFNULL(pinned,0) DESC, updated_at DESC LIMIT ?",
                (user_id, limit),
            ).fetchall()
        return [dict(r) for r in rows]


def rename_conversation(user_id: int, conversation_id: str, title: str) -> bool:
    """重命名属于该用户的会话。"""
    title = (title or "").strip()
    if not title:
        raise ValueError("标题不能为空")
    if len(title) > 60:
        title = title[:60]
    _ensure_chat_tables()
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE conversations SET title=?, updated_at=datetime('now') WHERE user_id=? AND id=?",
            (title, user_id, conversation_id),
        )
        return cur.rowcount > 0


def set_pinned(user_id: int, conversation_id: str, pinned: bool) -> bool:
    """设置会话置顶标志。"""
    _ensure_chat_tables()
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE conversations SET pinned=?, updated_at=datetime('now') WHERE user_id=? AND id=?",
            (1 if pinned else 0, user_id, conversation_id),
        )
        return cur.rowcount > 0


def delete_conversation(user_id: int, conversation_id: str) -> bool:
    """删除会话及其消息。"""
    _ensure_chat_tables()
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM chat_messages WHERE user_id=? AND conversation_id=?",
            (user_id, conversation_id),
        )
        cur = conn.execute(
            "DELETE FROM conversations WHERE user_id=? AND id=?",
            (user_id, conversation_id),
        )
        return cur.rowcount > 0


def load_messages(user_id: int, conversation_id: str) -> list[dict]:
    """按时间顺序加载某会话消息。"""
    _ensure_chat_tables()
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT role, content FROM chat_messages "
            "WHERE user_id=? AND conversation_id=? ORDER BY id ASC",
            (user_id, conversation_id),
        ).fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in rows]


def append_message(user_id: int, conversation_id: str, role: str, content: str) -> None:
    """追加一条消息；首条用户消息可自动当标题。"""
    _ensure_chat_tables()
    ensure_conversation(user_id, conversation_id)
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO chat_messages(user_id, conversation_id, role, content) VALUES (?,?,?,?)",
            (user_id, conversation_id, role, content),
        )
        if role == "user":
            row = conn.execute(
                "SELECT title FROM conversations WHERE user_id=? AND id=?",
                (user_id, conversation_id),
            ).fetchone()
            if row and (not row["title"] or row["title"] == "新对话"):
                title = (content or "").strip().replace("\n", " ")[:40] or "新对话"
                conn.execute(
                    "UPDATE conversations SET title=?, updated_at=datetime('now') WHERE user_id=? AND id=?",
                    (title, user_id, conversation_id),
                )
            else:
                conn.execute(
                    "UPDATE conversations SET updated_at=datetime('now') WHERE user_id=? AND id=?",
                    (user_id, conversation_id),
                )
        else:
            conn.execute(
                "UPDATE conversations SET updated_at=datetime('now') WHERE user_id=? AND id=?",
                (user_id, conversation_id),
            )


def get_latest_conversation_id(user_id: int) -> str | None:
    # 优先最近更新的会话（含置顶与非置顶）
    """返回该用户最近更新的会话 id。"""
    rows = list_conversations(user_id, pinned=None, limit=1)
    return rows[0]["id"] if rows else None
