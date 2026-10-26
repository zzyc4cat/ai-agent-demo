"""待办 CRUD。所有 SQL 带 user_id，complete_task 防止改他人任务。"""
from __future__ import annotations

from services.storage import get_conn, ensure_db


def add_task(user_id: int, title: str, due_at: str | None = None, priority: str | None = None) -> dict:
    """新增待办。"""
    title = (title or "").strip()
    if not title:
        raise ValueError("待办标题不能为空")
    ensure_db()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO tasks(user_id, title, due_at, priority) VALUES (?, ?, ?, ?)",
            (user_id, title, due_at, priority),
        )
        return {
            "id": cur.lastrowid,
            "user_id": user_id,
            "title": title,
            "status": "open",
            "due_at": due_at,
            "priority": priority,
        }


def list_tasks(user_id: int, status: str = "open") -> list[dict]:
    """按状态列出当前用户待办。"""
    ensure_db()
    with get_conn() as conn:
        if status == "all":
            rows = conn.execute(
                "SELECT * FROM tasks WHERE user_id = ? ORDER BY id DESC",
                (user_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE user_id = ? AND status = ? ORDER BY id DESC",
                (user_id, status),
            ).fetchall()
        return [dict(r) for r in rows]


def complete_task(user_id: int, task_id: int) -> bool:
    """仅当任务属于该用户时标为完成。"""
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE tasks SET status = 'done' WHERE id = ? AND user_id = ?",
            (task_id, user_id),
        )
        return cur.rowcount > 0
