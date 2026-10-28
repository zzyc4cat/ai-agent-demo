# -*- coding: utf-8 -*-
"""管理端：文档列表、软删除/恢复、审计日志。"""
from __future__ import annotations

import os
from typing import Any

from rag.kb_meta import bump_kb_version, ensure_kb_tables
from rag.tenant import load_tenant
from rag.vector_store import VectorStoreService
from services.storage import get_conn, ensure_db
from utils.path_tool import get_abs_path


def scope_for(tenant_id: str) -> str:
    """租户对应的 kb_files.scope（demo 兼容旧 sample）。"""
    cfg = load_tenant(tenant_id)
    return str(cfg.get("scope") or f"tenant:{tenant_id}")


def _audit(
    tenant_id: str,
    operator: str,
    action: str,
    target: str,
    detail: str = "",
) -> None:
    """写一条审计日志（失败不影响主流程）。"""
    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO kb_audit(tenant_id, operator, action, target, detail) VALUES(?,?,?,?,?)",
                (tenant_id, operator, action, target, detail[:500]),
            )
    except Exception:
        pass


def list_docs(tenant_id: str) -> list[dict[str, Any]]:
    """列出某租户的文档（含已软删除）。"""
    ensure_db()
    ensure_kb_tables()
    scope = scope_for(tenant_id)
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT path, content_hash, chunk_count, updated_at, deleted_at
               FROM kb_files WHERE scope = ? ORDER BY updated_at DESC""",
            (scope,),
        ).fetchall()
    out: list[dict[str, Any]] = []
    for r in rows:
        item = dict(r)
        item["exists"] = os.path.isfile(get_abs_path(item["path"]))
        item["status"] = "deleted" if item.get("deleted_at") else "active"
        out.append(item)
    return out


def delete_doc(tenant_id: str, source: str, operator: str) -> dict[str, Any]:
    """软删除：移出向量库与 BM25，保留原文件与元数据，可恢复。"""
    ensure_db()
    ensure_kb_tables()
    scope = scope_for(tenant_id)
    with get_conn() as conn:
        row = conn.execute(
            "SELECT deleted_at FROM kb_files WHERE scope = ? AND path = ?",
            (scope, source),
        ).fetchone()
    if not row:
        raise KeyError("文档不存在")
    if row["deleted_at"]:
        return {"ok": True, "already": True}

    cfg = load_tenant(tenant_id)
    store = VectorStoreService(str(cfg["collection"]))
    store.delete_by_source(source)
    with get_conn() as conn:
        conn.execute(
            "UPDATE kb_files SET deleted_at = datetime('now') WHERE scope = ? AND path = ?",
            (scope, source),
        )
    bump_kb_version(scope)
    _audit(tenant_id, operator, "delete_doc", source, "软删除")
    return {"ok": True, "already": False}


def restore_doc(tenant_id: str, source: str, operator: str) -> dict[str, Any]:
    """恢复软删除：重新入库该文件。"""
    ensure_db()
    ensure_kb_tables()
    scope = scope_for(tenant_id)
    with get_conn() as conn:
        row = conn.execute(
            "SELECT deleted_at FROM kb_files WHERE scope = ? AND path = ?",
            (scope, source),
        ).fetchone()
    if not row:
        raise KeyError("文档不存在")
    if not row["deleted_at"]:
        return {"ok": True, "already": True}

    abs_path = get_abs_path(source)
    if not os.path.isfile(abs_path):
        raise FileNotFoundError(f"原文件已不存在：{source}")

    cfg = load_tenant(tenant_id)
    store = VectorStoreService(str(cfg["collection"]))
    stats = store.ingest_file(abs_path, corpus="tenant", scope=scope, force=True)
    if stats["ingested"] == 0:
        raise RuntimeError("重新入库失败，请查看服务端日志")

    with get_conn() as conn:
        conn.execute(
            "UPDATE kb_files SET deleted_at = NULL WHERE scope = ? AND path = ?",
            (scope, source),
        )
    bump_kb_version(scope)
    _audit(tenant_id, operator, "restore_doc", source, f"恢复 {stats['chunks']} 块")
    return {"ok": True, "already": False, "chunks": stats["chunks"]}


def list_audit(tenant_id: str, limit: int = 100) -> list[dict[str, Any]]:
    """最近审计记录。"""
    ensure_db()
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT id, operator, action, target, detail, created_at
               FROM kb_audit WHERE tenant_id = ?
               ORDER BY id DESC LIMIT ?""",
            (tenant_id, limit),
        ).fetchall()
    return [dict(r) for r in rows]
