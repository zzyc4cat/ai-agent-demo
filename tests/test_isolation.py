# -*- coding: utf-8 -*-
"""多租户隔离测试：demo 与 demo2 的数据互不可见。"""
from __future__ import annotations

import os

import pytest

from rag.rag_service import RagSummarizeService
from rag.tenant import load_tenant

HAS_KEY = bool(os.getenv("DASHSCOPE_API_KEY", "").strip())


def test_unknown_tenant_raises() -> None:
    """不存在的租户必须直接报错，不能静默回退。"""
    with pytest.raises(KeyError):
        load_tenant("no_such_tenant")


def test_tenants_have_distinct_collections() -> None:
    """两个租户必须指向不同 collection。"""
    demo = load_tenant("demo")
    demo2 = load_tenant("demo2")
    assert demo["collection"] != demo2["collection"]


@pytest.mark.skipif(not HAS_KEY, reason="需要 DASHSCOPE_API_KEY")
def test_demo2_doc_not_visible_in_demo() -> None:
    """demo2 的专属文档不能出现在 demo 的召回结果里。"""
    svc = RagSummarizeService(tenant_id="demo")
    docs = svc.retrieve_docs("Z9 机型使用什么冷却液？")
    sources = [str((d.metadata or {}).get("source_path", "")) for d in docs]
    assert all("secret.md" not in s for s in sources)


@pytest.mark.skipif(not HAS_KEY, reason="需要 DASHSCOPE_API_KEY")
def test_demo2_sees_own_doc() -> None:
    """demo2 能召回自己的文档。"""
    svc = RagSummarizeService(tenant_id="demo2")
    docs = svc.retrieve_docs("Z9 机型使用什么冷却液？")
    sources = [str((d.metadata or {}).get("source_path", "")) for d in docs]
    assert any("secret.md" in s for s in sources)
