"""阶段 A：混合检索 / RRF / 查询缓存 / 规范化。"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, ROOT)
sys.path.insert(0, SRC)


def test_normalize_and_tokenize():
    from rag.utils_rag import normalize_query, tokenize

    assert normalize_query("  Hello   WORLD  ") == "hello world"
    toks = tokenize("番茄工作法 Pomodoro 25分钟")
    assert "番" in toks or "番茄工作法".startswith(toks[0])
    assert "pomodoro" in toks
    assert "25" in toks


def test_rrf_fuse_orders_overlap_higher():
    from langchain_core.documents import Document
    from rag.retriever import rrf_fuse

    d1 = Document(page_content="a", metadata={"chunk_id": "1"})
    d2 = Document(page_content="b", metadata={"chunk_id": "2"})
    d3 = Document(page_content="c", metadata={"chunk_id": "3"})
    # d1 在两路都靠前
    fused = rrf_fuse(
        [
            [("1", d1), ("2", d2)],
            [("1", d1), ("3", d3)],
        ]
    )
    assert fused[0][0].metadata["chunk_id"] == "1"
    assert fused[0][1] > fused[1][1]


def test_query_cache_l1_l2(tmp_path, monkeypatch):
    import services.storage as storage
    from rag.query_cache import QueryCache

    monkeypatch.setattr(storage, "DB_PATH", str(tmp_path / "c.db"))
    storage.ensure_db()
    # 重新实例化缓存
    import rag.query_cache as qc

    qc._cache = None
    monkeypatch.setenv("QWEATHER_API_KEY", "")  # 无关
    cache = QueryCache()
    cache.persist = True
    cache._ensure_table()

    key = QueryCache.make_key("上海天气吗", user_id=1, kb_version="1", corpus_scope="sample", layer="l2")
    scope = "u:1"
    cache.set(key, scope, "answer", "阴 26℃", ttl=60)
    hit = cache.get(key, scope)
    assert hit is not None
    assert hit.payload == "阴 26℃"

    cache.invalidate_user(1)
    assert cache.get(key, scope) is None


def test_bm25_index_roundtrip(tmp_path, monkeypatch):
    from langchain_core.documents import Document
    from rag.bm25_index import Bm25Index
    import rag.bm25_index as bi

    monkeypatch.setattr(
        bi,
        "get_abs_path",
        lambda p: str(tmp_path / p.replace("\\", "/").split("/")[-1])
        if "bm25" not in p
        else str(tmp_path / "bm25_index" / p.split("/")[-1]),
    )
    # 更稳妥：直接改 path
    idx = Bm25Index("test_col")
    idx.path = tmp_path / "t.pkl"
    idx.path.parent.mkdir(parents=True, exist_ok=True)
    idx.docs = []
    idx._tokens = []
    docs = [
        Document(page_content="经典番茄工作法专注时长是二十五分钟", metadata={"chunk_id": "a", "source_path": "x"}),
        Document(page_content="无关的天气预报内容", metadata={"chunk_id": "b", "source_path": "y"}),
    ]
    idx.add_documents(docs)
    hits = idx.search("番茄工作法 专注", k=5)
    assert hits
    assert "番茄" in hits[0][0].page_content


def test_hybrid_retriever_gate(monkeypatch):
    from langchain_core.documents import Document
    from rag.retriever import HybridRetriever

    docs = [
        Document(page_content="番茄工作法", metadata={"chunk_id": "1"}),
        Document(page_content="其他", metadata={"chunk_id": "2"}),
    ]

    def vsearch(q, k):
        return [(docs[0], 0.9), (docs[1], 0.1)]

    class FakeBm25:
        def search(self, query, k=20):
            return [(docs[0], 5.0)]

    monkeypatch.setattr("rag.retriever.dashscope_rerank", lambda *a, **k: None)
    rt = HybridRetriever(vector_search_fn=vsearch, bm25_indexes=[FakeBm25()])
    rt.score_threshold = 0.001
    out, meta = rt.retrieve("番茄")
    assert out
    assert meta["rerank"] == "rrf"
    assert meta["vector_hits"] >= 1


def test_hybrid_weak_vector_strong_bm25_passes(monkeypatch):
    """向量弱但 BM25 强时不应被弱门控误杀。"""
    from langchain_core.documents import Document
    from rag.retriever import HybridRetriever

    docs = [Document(page_content="会议纪要模板", metadata={"chunk_id": "m1"})]

    def vsearch(q, k):
        return [(docs[0], 0.2)]  # 低于 min_similarity

    class FakeBm25:
        def search(self, query, k=20):
            return [(docs[0], 4.0)]

    monkeypatch.setattr("rag.retriever.dashscope_rerank", lambda *a, **k: None)
    rt = HybridRetriever(vector_search_fn=vsearch, bm25_indexes=[FakeBm25()])
    rt.min_similarity = 0.55
    rt.bm25_min_score = 1.0
    rt.score_threshold = 0.001
    out, meta = rt.retrieve("会议纪要")
    assert out, meta
    assert not meta.get("weak_gate")


def test_hybrid_both_weak_gates(monkeypatch):
    from langchain_core.documents import Document
    from rag.retriever import HybridRetriever

    docs = [Document(page_content="无关内容", metadata={"chunk_id": "x"})]

    def vsearch(q, k):
        return [(docs[0], 0.1)]

    class FakeBm25:
        def search(self, query, k=20):
            return [(docs[0], 0.2)]

    monkeypatch.setattr("rag.retriever.dashscope_rerank", lambda *a, **k: None)
    rt = HybridRetriever(vector_search_fn=vsearch, bm25_indexes=[FakeBm25()])
    rt.min_similarity = 0.55
    rt.bm25_min_score = 1.0
    out, meta = rt.retrieve("星座飞船")
    assert out == []
    assert meta.get("weak_gate") is True
