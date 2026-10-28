# -*- coding: utf-8 -*-
"""账号与会话：密码哈希、登录校验、token 会话、登录限流。

密码只以 scrypt 哈希形式存 users 表；明文不落库、不入日志、不写脚本。
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import re
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Any

from services.storage import get_conn, ensure_db

USERNAME_RE = re.compile(r"^[A-Za-z0-9_\u4e00-\u9fff]{3,32}$")
MIN_PASSWORD_LEN = 8
SESSION_DAYS = 7

# 登录失败限流：同一用户名 5 次失败锁 5 分钟
_MAX_FAILS = 5
_LOCK_SECONDS = 300
_fails: dict[str, list[float]] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def hash_password(password: str) -> str:
    """scrypt 哈希，格式 scrypt$salt$hash（base64）。"""
    salt = os.urandom(16)
    dk = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return "scrypt${}${}".format(
        base64.b64encode(salt).decode(), base64.b64encode(dk).decode()
    )


def verify_password(password: str, stored: str | None) -> bool:
    """常数时间校验密码。"""
    if not stored or not stored.startswith("scrypt$"):
        return False
    try:
        _, salt_b64, hash_b64 = stored.split("$", 2)
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
        dk = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=32)
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False


def _public(row: Any) -> dict[str, Any]:
    """对外返回的用户信息，绝不包含 password_hash。"""
    return {
        "id": int(row["id"]),
        "username": row["username"],
        "role": row["role"],
        "tenant_id": row["tenant_id"],
        "created_at": row["created_at"],
    }


def create_user(
    username: str,
    password: str,
    *,
    role: str = "user",
    tenant_id: str = "demo",
) -> dict[str, Any]:
    """创建账号；用户名重复或格式不合法时抛 ValueError。"""
    ensure_db()
    name = (username or "").strip()
    if not USERNAME_RE.match(name):
        raise ValueError("用户名需 3–32 位，仅限字母、数字、下划线或中文")
    if len(password or "") < MIN_PASSWORD_LEN:
        raise ValueError(f"密码至少 {MIN_PASSWORD_LEN} 位")
    if role not in {"user", "admin"}:
        raise ValueError("角色只能是 user 或 admin")
    with get_conn() as conn:
        try:
            cur = conn.execute(
                "INSERT INTO users(username, password_hash, role, tenant_id) VALUES(?,?,?,?)",
                (name, hash_password(password), role, tenant_id),
            )
        except Exception as e:  # UNIQUE 冲突
            raise ValueError("用户名已存在") from e
        row = conn.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
    return _public(row)


def _record_failure(username: str) -> None:
    now = time.time()
    bucket = [t for t in _fails.get(username, []) if now - t < _LOCK_SECONDS]
    bucket.append(now)
    _fails[username] = bucket


def _is_locked(username: str) -> bool:
    now = time.time()
    bucket = [t for t in _fails.get(username, []) if now - t < _LOCK_SECONDS]
    _fails[username] = bucket
    return len(bucket) >= _MAX_FAILS


def authenticate(username: str, password: str) -> dict[str, Any] | None:
    """校验账号密码；失败返回 None，连续失败会被锁定。"""
    ensure_db()
    name = (username or "").strip()
    if not name or _is_locked(name):
        return None
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (name,)).fetchone()
    if not row or not verify_password(password, row["password_hash"]):
        _record_failure(name)
        return None
    _fails.pop(name, None)
    return _public(row)


def create_session(user_id: int) -> str:
    """签发会话 token（只存哈希），返回明文 token。"""
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    expires = (_now() + timedelta(days=SESSION_DAYS)).strftime("%Y-%m-%d %H:%M:%S")
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO auth_sessions(token_hash, user_id, expires_at) VALUES(?,?,?)",
            (token_hash, user_id, expires),
        )
    return token


def user_from_token(token: str | None) -> dict[str, Any] | None:
    """按 token 取用户；过期或不存在返回 None。"""
    if not token:
        return None
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    with get_conn() as conn:
        row = conn.execute(
            """SELECT u.* FROM auth_sessions s
               JOIN users u ON u.id = s.user_id
               WHERE s.token_hash = ? AND s.expires_at > datetime('now')""",
            (token_hash,),
        ).fetchone()
    return _public(row) if row else None


def revoke_session(token: str | None) -> None:
    """退出登录：删除该 token。"""
    if not token:
        return
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    with get_conn() as conn:
        conn.execute("DELETE FROM auth_sessions WHERE token_hash = ?", (token_hash,))
