# -*- coding: utf-8 -*-
"""成本估算与入库任务兜底。"""
from __future__ import annotations

import uuid

from services import admin_service
from services.cost import estimate_cost
from services.storage import ensure_db, get_conn


def test_estimate_cost_known_model() -> None:
    """qwen3.8-flash：输入 0.8 / 输出 2.7 元每百万。"""
    assert estimate_cost(1_000_000, 0) == 0.8
    assert estimate_cost(0, 1_000_000) == 2.7
    assert estimate_cost(500_000, 500_000) == 1.75


def test_estimate_cost_unknown_model_is_none() -> None:
    assert estimate_cost(1000, 1000, model="no_such_model") is None


def test_recover_stale_tasks() -> None:
    """启动兜底：遗留 pending/processing 任务应被标记失败。"""
    ensure_db()
    task_id = uuid.uuid4().hex
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO kb_tasks(id, tenant_id, kind, target, status) VALUES(?,?,?,?,?)",
            (task_id, "demo", "upload", "tmp/x.md", "processing"),
        )
    admin_service.recover_stale_tasks()
    task = admin_service.get_task(task_id)
    assert task is not None
    assert task["status"] == "failed"
    assert "重启" in (task["message"] or "")
    with get_conn() as conn:
        conn.execute("DELETE FROM kb_tasks WHERE id = ?", (task_id,))
