"""
SQLite 连接与 schema。

库文件：storage/app.db。ensure_db 创建用户/偏好/会话/待办/笔记/记忆/meta。
会话的 pinned、updated_at 与 chat_messages 由 chat_service 在首次使用时 ALTER。
闪卡表由 tools_b 懒创建。连接开启 PRAGMA foreign_keys=ON。
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from utils.path_tool import get_abs_path

DB_PATH = get_abs_path("storage/app.db")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL COLLATE NOCASE UNIQUE,
    password_hash TEXT,
    role TEXT NOT NULL DEFAULT 'user',
    tenant_id TEXT NOT NULL DEFAULT 'demo',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS auth_sessions (
    token_hash TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS preferences (
    user_id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    PRIMARY KEY (user_id, key),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS conversations (
    id TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    title TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (user_id, id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    due_at TEXT,
    priority TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    kind TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    message_id TEXT NOT NULL,
    rating TEXT NOT NULL,
    reason TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS kb_conversations (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    user_id INTEGER,
    title TEXT,
    pinned INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS kb_messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    citations_json TEXT,
    latency_ms INTEGER,
    prompt_tokens INTEGER NOT NULL DEFAULT 0,
    completion_tokens INTEGER NOT NULL DEFAULT 0,
    refused INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (conversation_id) REFERENCES kb_conversations(id)
);

CREATE TABLE IF NOT EXISTS kb_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    operator TEXT NOT NULL,
    action TEXT NOT NULL,
    target TEXT NOT NULL,
    detail TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS kb_tasks (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    target TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    message TEXT,
    chunks INTEGER NOT NULL DEFAULT 0,
    operator TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def ensure_db() -> None:
    """创建 storage 目录并执行建表脚本。"""
    Path(get_abs_path("storage")).mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys=ON")
        conn.executescript(_SCHEMA)
        # 轻量迁移：旧库补列
        user_cols = {row[1] for row in conn.execute("PRAGMA table_info(users)")}
        for col, ddl in (
            ("password_hash", "ALTER TABLE users ADD COLUMN password_hash TEXT"),
            ("role", "ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'"),
            ("tenant_id", "ALTER TABLE users ADD COLUMN tenant_id TEXT NOT NULL DEFAULT 'demo'"),
        ):
            if col not in user_cols:
                conn.execute(ddl)

        conv_cols = {row[1] for row in conn.execute("PRAGMA table_info(kb_conversations)")}
        if "pinned" not in conv_cols:
            conn.execute(
                "ALTER TABLE kb_conversations ADD COLUMN pinned INTEGER NOT NULL DEFAULT 0"
            )
        if "user_id" not in conv_cols:
            conn.execute("ALTER TABLE kb_conversations ADD COLUMN user_id INTEGER")

        msg_cols = {row[1] for row in conn.execute("PRAGMA table_info(kb_messages)")}
        for col in ("prompt_tokens", "completion_tokens"):
            if col not in msg_cols:
                conn.execute(
                    f"ALTER TABLE kb_messages ADD COLUMN {col} INTEGER NOT NULL DEFAULT 0"
                )
        conn.commit()


@contextmanager
def get_conn():
    """上下文管理器：打开启用外键的 SQLite 连接并提交。"""
    ensure_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
