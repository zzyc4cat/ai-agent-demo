"""阶段 C：embedding 缓存、评测夹具、配置完备性。"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, ROOT)
sys.path.insert(0, SRC)


class _FakeEmb:
    def __init__(self):
        self.calls = 0

    def embed_documents(self, texts):
        self.calls += len(texts)
        return [[float(len(t)), 0.1] for t in texts]

    def embed_query(self, text):
        self.calls += 1
        return [float(len(text)), 0.2]


def test_embedding_cache_hits(tmp_path, monkeypatch):
    from rag.embedding_cache import CachedEmbeddings
    import rag.embedding_cache as ec

    monkeypatch.setattr(
        ec,
        "get_runtime",
        lambda: {"embedding_cache": {"enabled": True, "directory": str(tmp_path / "ecache")}},
    )
    # patch get_abs_path used inside CachedEmbeddings via utils — directory already absolute in cfg
    monkeypatch.setattr(ec, "get_abs_path", lambda p: p if os.path.isabs(p) else str(tmp_path / p))

    fake = _FakeEmb()
    wrapped = CachedEmbeddings(fake, model_tag="t")
    wrapped.root = tmp_path / "ecache"
    wrapped.root.mkdir(parents=True, exist_ok=True)
    wrapped.enabled = True

    a = wrapped.embed_documents(["hello", "world"])
    assert fake.calls == 2
    b = wrapped.embed_documents(["hello", "world"])
    assert fake.calls == 2  # 全命中
    assert a == b
    q1 = wrapped.embed_query("unique-query-xyz")
    q2 = wrapped.embed_query("unique-query-xyz")
    assert q1 == q2
    assert fake.calls == 3  # query 只算一次


def test_rag_eval_fixture_exists():
    path = os.path.join(ROOT, "tests", "fixtures", "rag_eval.jsonl")
    assert os.path.isfile(path)
    lines = open(path, encoding="utf-8").readlines()
    assert len(lines) >= 5
    row = json.loads(lines[0])
    assert "query" in row and "expect" in row


def test_rag_runtime_config_loaded():
    from utils.config_handler import load_rag_runtime_config

    cfg = load_rag_runtime_config()
    assert "retrieve" in cfg
    assert "query_cache" in cfg
    assert cfg["query_cache"].get("enabled") is True
    assert cfg.get("query_cache", {}).get("semantic_l1") is False
