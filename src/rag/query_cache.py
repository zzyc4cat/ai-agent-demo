"""查询结果缓存：L1=检索文档，L2=最终答案；精确 normalize 命中。"""
from __future__ import annotations

import json
import sqlite3
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any

from rag.utils_rag import get_runtime, normalize_query
from services import storage
from services.storage import ensure_db
from utils.logger_handler import log_event
from utils.path_tool import get_abs_path

_LOCK = threading.RLock()


@dataclass
class CacheEntry:
    kind: str  # docs | answer | empty
    payload: Any
    expire_at: float


class QueryCache:
    def __init__(self) -> None:
        cfg = (get_runtime().get("query_cache") or {})
        self.enabled = bool(cfg.get("enabled", True))
        self.max_entries = int(cfg.get("max_entries_per_user", 200))
        self.l1_ttl = float(cfg.get("l1_ttl_seconds", 3600))
        self.l2_ttl = float(cfg.get("l2_ttl_seconds", 900))
        self.empty_ttl = float(cfg.get("empty_result_ttl_seconds", 300))
        self.persist = bool(cfg.get("persist_sqlite", True))
        # user_scope -> OrderedDict[key, CacheEntry]
        self._mem: dict[str, OrderedDict[str, CacheEntry]] = {}
        if self.persist:
            ensure_db()
            self._ensure_table()

    def _ensure_table(self) -> None:
        with sqlite3.connect(storage.DB_PATH) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS rag_query_cache (
                    cache_key TEXT PRIMARY KEY,
                    user_scope TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    expire_at REAL NOT NULL
                )
                """
            )
            conn.commit()

    @staticmethod
    def make_key(
        query: str,
        *,
        user_id: int | None,
        kb_version: str,
        corpus_scope: str,
        prompt_version: str = "",
        model_id: str = "",
        layer: str = "l1",
    ) -> str:
        nq = normalize_query(query)
        uid = str(user_id) if user_id is not None else "anon"
        base = f"{layer}|{uid}|{corpus_scope}|{kb_version}|{nq}"
        if layer == "l2":
            base += f"|{prompt_version}|{model_id}"
        return base

    def _bucket(self, user_scope: str) -> OrderedDict[str, CacheEntry]:
        if user_scope not in self._mem:
            self._mem[user_scope] = OrderedDict()
        return self._mem[user_scope]

    def _purge(self, bucket: OrderedDict[str, CacheEntry]) -> None:
        now = time.time()
        dead = [k for k, v in bucket.items() if v.expire_at <= now]
        for k in dead:
            bucket.pop(k, None)
        while len(bucket) > self.max_entries:
            bucket.popitem(last=False)

    def get(self, key: str, user_scope: str) -> CacheEntry | None:
        if not self.enabled:
            return None
        with _LOCK:
            bucket = self._bucket(user_scope)
            self._purge(bucket)
            ent = bucket.get(key)
            if ent and ent.expire_at > time.time():
                bucket.move_to_end(key)
                log_event("rag.cache", cache_hit=ent.kind, user_scope=user_scope)
                return ent
            if self.persist:
                row = self._db_get(key)
                if row and row.expire_at > time.time():
                    bucket[key] = row
                    bucket.move_to_end(key)
                    log_event("rag.cache", cache_hit=row.kind, user_scope=user_scope, source="sqlite")
                    return row
            log_event("rag.cache", cache_hit="miss", user_scope=user_scope)
            return None

    def set(self, key: str, user_scope: str, kind: str, payload: Any, ttl: float) -> None:
        if not self.enabled:
            return
        ent = CacheEntry(kind=kind, payload=payload, expire_at=time.time() + ttl)
        with _LOCK:
            bucket = self._bucket(user_scope)
            bucket[key] = ent
            bucket.move_to_end(key)
            self._purge(bucket)
            if self.persist:
                self._db_set(key, user_scope, ent)

    def invalidate_user(self, user_id: int | None) -> None:
        scope = f"u:{user_id}" if user_id is not None else "u:anon"
        with _LOCK:
            self._mem.pop(scope, None)
            if self.persist:
                with sqlite3.connect(storage.DB_PATH) as conn:
                    conn.execute("DELETE FROM rag_query_cache WHERE user_scope = ?", (scope,))
                    conn.commit()
        log_event("rag.cache", action="invalidate", user_scope=scope)

    def _db_get(self, key: str) -> CacheEntry | None:
        with sqlite3.connect(storage.DB_PATH) as conn:
            row = conn.execute(
                "SELECT kind, payload, expire_at FROM rag_query_cache WHERE cache_key = ?",
                (key,),
            ).fetchone()
        if not row:
            return None
        kind, payload_s, expire_at = row
        try:
            payload = json.loads(payload_s)
        except json.JSONDecodeError:
            payload = payload_s
        return CacheEntry(kind=kind, payload=payload, expire_at=float(expire_at))

    def _db_set(self, key: str, user_scope: str, ent: CacheEntry) -> None:
        payload_s = json.dumps(ent.payload, ensure_ascii=False)
        with sqlite3.connect(storage.DB_PATH) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO rag_query_cache(cache_key, user_scope, kind, payload, expire_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (key, user_scope, ent.kind, payload_s, ent.expire_at),
            )
            conn.commit()


_cache: QueryCache | None = None


def get_query_cache() -> QueryCache:
    global _cache
    if _cache is None:
        _cache = QueryCache()
    return _cache
