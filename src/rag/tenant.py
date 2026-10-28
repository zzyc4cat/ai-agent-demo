# -*- coding: utf-8 -*-
"""租户配置：tenants/<id>.yaml 的读取与列举。"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

TENANTS_DIR = Path(__file__).resolve().parents[2] / "tenants"


def tenant_path(tenant_id: str) -> Path:
    """返回租户配置文件路径。"""
    return TENANTS_DIR / f"{tenant_id}.yaml"


def load_tenant(tenant_id: str) -> dict[str, Any]:
    """读取租户配置；不存在时抛 KeyError。"""
    path = tenant_path(tenant_id)
    if not path.is_file():
        raise KeyError(f"租户不存在: {tenant_id}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    data.setdefault("id", tenant_id)
    data.setdefault("name", tenant_id)
    data.setdefault("collection", f"agent_tenant_{tenant_id}")
    data.setdefault("corpus", f"data/tenants/{tenant_id}")
    return data


def list_tenants() -> list[dict[str, Any]]:
    """列出所有租户配置。"""
    out: list[dict[str, Any]] = []
    if not TENANTS_DIR.is_dir():
        return out
    for path in sorted(TENANTS_DIR.glob("*.yaml")):
        try:
            out.append(load_tenant(path.stem))
        except Exception:
            continue
    return out
