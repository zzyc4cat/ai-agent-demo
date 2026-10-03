"""本地用户：创建、切换、上次用户。"""
from __future__ import annotations

import re

from services.storage import get_conn, ensure_db
from utils.logger_handler import log_event

_USERNAME_RE = re.compile(r"^[\w\u4e00-\u9fff][\w\u4e00-\u9fff\- ]{0,31}$")


def _normalize(name: str) -> str:
    return (name or "").strip()


def validate_username(username: str) -> str:
    name = _normalize(username)
    if len(name) < 2 or len(name) > 32:
        raise ValueError("用户名长度须为 2–32 个字符")
    if not _USERNAME_RE.match(name):
        raise ValueError("用户名仅允许中英文、数字、下划线、连字符与空格")
    return name


def create_user(username: str) -> dict:
    name = validate_username(username)
    ensure_db()
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id, username FROM users WHERE username = ? COLLATE NOCASE",
            (name,),
        ).fetchone()
        if existing:
            raise ValueError(f"用户已存在：{existing['username']}，请直接切换")
        cur = conn.execute("INSERT INTO users(username) VALUES (?)", (name,))
        user_id = cur.lastrowid
        conn.execute(
            "INSERT OR REPLACE INTO meta(key, value) VALUES ('last_user_id', ?)",
            (str(user_id),),
        )
        log_event("user.create", user_id=user_id, username=name)
        return {"id": user_id, "username": name}


def list_users() -> list[dict]:
    ensure_db()
    with get_conn() as conn:
        rows = conn.execute("SELECT id, username, created_at FROM users ORDER BY id").fetchall()
        return [dict(r) for r in rows]


def get_user(user_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, username, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        return dict(row) if row else None


def find_user_by_name(username: str) -> dict | None:
    name = _normalize(username)
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, username, created_at FROM users WHERE username = ? COLLATE NOCASE",
            (name,),
        ).fetchone()
        return dict(row) if row else None


def set_last_user(user_id: int) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO meta(key, value) VALUES ('last_user_id', ?)",
            (str(user_id),),
        )


def get_last_user() -> dict | None:
    ensure_db()
    with get_conn() as conn:
        row = conn.execute("SELECT value FROM meta WHERE key = 'last_user_id'").fetchone()
        if not row:
            return None
        return get_user(int(row["value"]))


def switch_or_create(username: str) -> dict:
    """切换到已有用户，或注册新用户。"""
    found = find_user_by_name(username)
    if found:
        set_last_user(found["id"])
        log_event("user.switch", user_id=found["id"], username=found["username"])
        return found
    return create_user(username)


def set_preference(user_id: int, key: str, value: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO preferences(user_id, key, value) VALUES (?, ?, ?)",
            (user_id, key, value),
        )


def get_preference(user_id: int, key: str, default: str | None = None) -> str | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT value FROM preferences WHERE user_id = ? AND key = ?",
            (user_id, key),
        ).fetchone()
        return row["value"] if row else default
