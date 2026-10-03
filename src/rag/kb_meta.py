"""知识库元数据：kb_version、文件清单。"""
from __future__ import annotations

import sqlite3

from services import storage
from services.storage import ensure_db


def _conn():
    ensure_db()
    return sqlite3.connect(storage.DB_PATH)


def ensure_kb_tables() -> None:
    with _conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS kb_meta (
                scope TEXT PRIMARY KEY,
                kb_version TEXT NOT NULL DEFAULT '0',
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS kb_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                scope TEXT NOT NULL,
                path TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                chunk_count INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(scope, path)
            );
            """
        )
        conn.commit()


def get_kb_version(scope: str) -> str:
    ensure_kb_tables()
    with _conn() as conn:
        row = conn.execute("SELECT kb_version FROM kb_meta WHERE scope = ?", (scope,)).fetchone()
    return row[0] if row else "0"


def bump_kb_version(scope: str) -> str:
    ensure_kb_tables()
    cur = str(int(get_kb_version(scope) or "0") + 1)
    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO kb_meta(scope, kb_version, updated_at)
            VALUES (?, ?, datetime('now'))
            ON CONFLICT(scope) DO UPDATE SET
              kb_version=excluded.kb_version,
              updated_at=datetime('now')
            """,
            (scope, cur),
        )
        conn.commit()
    return cur


def upsert_kb_file(
    *,
    scope: str,
    path: str,
    content_hash: str,
    chunk_count: int,
    user_id: int | None = None,
) -> None:
    ensure_kb_tables()
    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO kb_files(user_id, scope, path, content_hash, chunk_count, updated_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(scope, path) DO UPDATE SET
              content_hash=excluded.content_hash,
              chunk_count=excluded.chunk_count,
              user_id=excluded.user_id,
              updated_at=datetime('now')
            """,
            (user_id, scope, path, content_hash, chunk_count),
        )
        conn.commit()


def get_kb_file_hash(scope: str, path: str) -> str | None:
    ensure_kb_tables()
    with _conn() as conn:
        row = conn.execute(
            "SELECT content_hash FROM kb_files WHERE scope = ? AND path = ?",
            (scope, path),
        ).fetchone()
    return row[0] if row else None


def delete_kb_file(scope: str, path: str) -> None:
    ensure_kb_tables()
    with _conn() as conn:
        conn.execute("DELETE FROM kb_files WHERE scope = ? AND path = ?", (scope, path))
        conn.commit()
