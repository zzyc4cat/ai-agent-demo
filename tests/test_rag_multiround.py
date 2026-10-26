"""多轮回归：缓存命中、检索链路、配置与入库 CLI 联通性（尽量不依赖外网 LLM）。"""
from __future__ import annotations

import os
import sys
from unittest.mock import patch

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, ROOT)
sys.path.insert(0, SRC)


def test_round_cache_then_retrieve_flow(tmp_path, monkeypatch):
    """L2 命中跳过检索；失效后应重新检索。"""
    import services.storage as storage
    from langchain_core.documents import Document
    import rag.query_cache as qc
    from rag.query_cache import QueryCache

    monkeypatch.setattr(storage, "DB_PATH", str(tmp_path / "m.db"))
    storage.ensure_db()
    qc._cache = None

    from rag.rag_service import RagSummarizeService

    svc = RagSummarizeService.__new__(RagSummarizeService)
    svc.prompt_text = "q:{input}\nc:{context}"
    svc.prompt_ver = "p1"
    svc.cache = QueryCache()
    svc.cache.persist = False

    calls = {"n": 0}

    def fake_retrieve(query, user_id=None):
        """测试替身：伪造检索结果。"""
        calls["n"] += 1
        return [Document(page_content="番茄二十五分钟", metadata={"source_path": "g.txt", "chunk_id": "1"})]

    def fake_chain():
        """测试替身：伪造 LLM 链。"""
        class C:
            def invoke(self, d):
                """测试替身：返回固定字符串。"""
                return "专注时长约二十五分钟（资料1）"

        return C()

    svc.retrieve_docs = fake_retrieve  # type: ignore
    svc._chain = fake_chain  # type: ignore
    svc._kb_version_token = lambda user_id=None: "1"  # type: ignore

    a1 = svc.rag_summarize("番茄多久", user_id=9)
    a2 = svc.rag_summarize("番茄多久", user_id=9)
    assert a1 == a2
    assert calls["n"] == 1  # 第二次 L2 命中

    svc.cache.invalidate_user(9)
    a3 = svc.rag_summarize("番茄多久", user_id=9)
    assert "二十五" in a3 or "资料" in a3
    assert calls["n"] == 2


def test_round_empty_docs_returns_unknown(tmp_path, monkeypatch):
    """检索为空时应得到不知道。"""
    import services.storage as storage
    import rag.query_cache as qc
    from rag.query_cache import QueryCache
    from rag.rag_service import RagSummarizeService

    monkeypatch.setattr(storage, "DB_PATH", str(tmp_path / "e.db"))
    storage.ensure_db()
    qc._cache = None

    svc = RagSummarizeService.__new__(RagSummarizeService)
    svc.prompt_text = "x"
    svc.prompt_ver = "p"
    svc.cache = QueryCache()
    svc.cache.persist = False
    svc.retrieve_docs = lambda q, user_id=None: []  # type: ignore
    svc._kb_version_token = lambda user_id=None: "0"  # type: ignore
    assert svc.rag_summarize("无关问题", user_id=1) == "不知道"


def test_eval_fixture_schema():
    """评测 jsonl 字段符合约定。"""
    import json

    path = os.path.join(ROOT, "tests", "fixtures", "rag_eval.jsonl")
    allowed = {"hit", "unknown", "hit_or_unknown", "unknown_or_safe"}
    for line in open(path, encoding="utf-8"):
        row = json.loads(line)
        assert row["expect"] in allowed
