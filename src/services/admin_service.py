# -*- coding: utf-8 -*-
"""管理端：文档列表、软删除/恢复、审计日志。"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import threading
import uuid
from pathlib import Path
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


def _purge_expired(tenant_id: str) -> int:
    """彻底删除软删除超过 30 天的文档（含原文件）。"""
    ensure_kb_tables()
    scope = scope_for(tenant_id)
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT path FROM kb_files
               WHERE scope = ? AND deleted_at IS NOT NULL
                 AND deleted_at <= datetime('now', ?)""",
            (scope, f"-{PURGE_DAYS} days"),
        ).fetchall()
    if not rows:
        return 0
    cfg = load_tenant(tenant_id)
    store = VectorStoreService(str(cfg["collection"]))
    for r in rows:
        path = r["path"]
        store.delete_by_source(path)
        abs_path = get_abs_path(path)
        if os.path.isfile(abs_path):
            try:
                os.remove(abs_path)
            except OSError:
                pass
        with get_conn() as conn:
            conn.execute("DELETE FROM kb_files WHERE scope = ? AND path = ?", (scope, path))
        _audit(tenant_id, "system", "purge_doc", path, f"超过 {PURGE_DAYS} 天，彻底删除")
    bump_kb_version(scope)
    return len(rows)


def list_docs(tenant_id: str) -> list[dict[str, Any]]:
    """列出某租户的文档（含已软删除）；顺带清理过期的软删除。"""
    ensure_db()
    ensure_kb_tables()
    _purge_expired(tenant_id)
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


# ---------------------------------------------------------------- 异步入库

NODE_BIN = os.getenv("NODE_BIN") or shutil.which("node") or "node"
CONVERTER = Path(__file__).resolve().parents[2] / "tools" / "wiki2md" / "convert.mjs"
UPLOAD_LIMIT = 20 * 1024 * 1024
ALLOWED_SUFFIX = (".md", ".markdown", ".txt", ".pdf", ".docx")
PURGE_DAYS = 30


def _safe_name(name: str) -> str:
    base = os.path.basename(name or "upload.md")
    base = re.sub(r"[^\w.\-\u4e00-\u9fff]", "_", base)[:80]
    return base or "upload.md"


def _update_task(task_id: str, status: str, message: str = "", chunks: int = 0) -> None:
    with get_conn() as conn:
        conn.execute(
            """UPDATE kb_tasks SET status=?, message=?, chunks=?, updated_at=datetime('now')
               WHERE id=?""",
            (status, message[:300], chunks, task_id),
        )


def _new_task(tenant_id: str, kind: str, target: str, operator: str) -> str:
    task_id = uuid.uuid4().hex
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO kb_tasks(id, tenant_id, kind, target, status, operator)
               VALUES(?,?,?,?,'pending',?)""",
            (task_id, tenant_id, kind, target[:300], operator),
        )
    return task_id


def get_task(task_id: str) -> dict[str, Any] | None:
    ensure_db()
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM kb_tasks WHERE id = ?", (task_id,)).fetchone()
    return dict(row) if row else None


def list_tasks(tenant_id: str, limit: int = 20) -> list[dict[str, Any]]:
    ensure_db()
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM kb_tasks WHERE tenant_id = ? ORDER BY created_at DESC LIMIT ?",
            (tenant_id, limit),
        ).fetchall()
    return [dict(r) for r in rows]


def recover_stale_tasks() -> int:
    """启动时把上次进程遗留的 pending/processing 任务标记为失败。"""
    ensure_db()
    with get_conn() as conn:
        cur = conn.execute(
            """UPDATE kb_tasks
               SET status='failed', message='服务重启，任务中断，请重新提交',
                   updated_at=datetime('now')
               WHERE status IN ('pending','processing')"""
        )
        return cur.rowcount


def _run_ingest(task_id: str, tenant_id: str, rel_path: str, operator: str, action: str) -> None:
    """后台线程：入库单个文件并更新任务状态。"""
    _update_task(task_id, "processing", "解析并入库中")
    try:
        cfg = load_tenant(tenant_id)
        store = VectorStoreService(str(cfg["collection"]))
        stats = store.ingest_file(
            get_abs_path(rel_path), corpus="tenant", scope=scope_for(tenant_id), force=True
        )
        if stats["ingested"]:
            _update_task(task_id, "done", "入库完成", int(stats["chunks"]))
            _audit(tenant_id, operator, action, rel_path, f"{stats['chunks']} 块")
        else:
            _update_task(task_id, "failed", "解析或切分结果为空，未入库")
    except Exception as e:  # noqa: BLE001
        _update_task(task_id, "failed", f"入库失败：{e}")


def _run_url(task_id: str, tenant_id: str, url: str, operator: str) -> None:
    """后台线程：Node 渲染网页 → Markdown → 入库。"""
    _update_task(task_id, "processing", "抓取并转换网页")
    out_dir = get_abs_path(f"data/tenants/{tenant_id}/uploads")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"url_{uuid.uuid4().hex[:8]}.md")
    try:
        proc = subprocess.run(
            [NODE_BIN, str(CONVERTER), url, out_path],
            cwd=str(CONVERTER.parent),
            capture_output=True,
            text=True,
            timeout=180,
        )
        if proc.returncode != 0 or not os.path.isfile(out_path):
            raise RuntimeError((proc.stderr or "网页转换失败")[:300])
        rel = os.path.relpath(out_path, get_abs_path(".")).replace("\\", "/")
        _run_ingest(task_id, tenant_id, rel, operator, "import_url")
    except Exception as e:  # noqa: BLE001
        _update_task(task_id, "failed", f"导入失败：{e}")


def submit_file(tenant_id: str, filename: str, content: bytes, operator: str) -> str:
    """保存上传文件并启动后台入库，返回任务 id。"""
    ensure_db()
    if len(content) > UPLOAD_LIMIT:
        raise ValueError("文件超过 20MB 限制")
    safe = _safe_name(filename)
    if not safe.lower().endswith(ALLOWED_SUFFIX):
        raise ValueError("仅支持 .md / .markdown / .txt / .pdf")
    upload_dir = get_abs_path(f"data/tenants/{tenant_id}/uploads")
    os.makedirs(upload_dir, exist_ok=True)
    stored = f"{uuid.uuid4().hex[:8]}_{safe}"
    abs_path = os.path.join(upload_dir, stored)
    with open(abs_path, "wb") as f:
        f.write(content)
    rel = os.path.relpath(abs_path, get_abs_path(".")).replace("\\", "/")
    task_id = _new_task(tenant_id, "upload", rel, operator)
    threading.Thread(
        target=_run_ingest, args=(task_id, tenant_id, rel, operator, "upload_doc"), daemon=True
    ).start()
    return task_id


def submit_url(tenant_id: str, url: str, operator: str) -> str:
    """抓取网页并启动后台入库，返回任务 id。"""
    ensure_db()
    if not re.match(r"^https?://", url or ""):
        raise ValueError("网址必须以 http:// 或 https:// 开头")
    task_id = _new_task(tenant_id, "url", url, operator)
    threading.Thread(
        target=_run_url, args=(task_id, tenant_id, url, operator), daemon=True
    ).start()
    return task_id
