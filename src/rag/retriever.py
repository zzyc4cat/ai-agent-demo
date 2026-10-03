"""混合检索：向量 + BM25 → RRF → 可选 DashScope 重排 → 门控。"""
from __future__ import annotations

import os
from typing import Any

from langchain_core.documents import Document

from rag.bm25_index import Bm25Index
from rag.utils_rag import get_runtime
from utils.logger_handler import log_event


def rrf_fuse(
    ranked_lists: list[list[tuple[str, Document]]],
    *,
    k: int = 60,
) -> list[tuple[Document, float]]:
    """ranked_lists: 每路为 [(doc_id, doc), ...] 已按相关性从高到低。"""
    scores: dict[str, float] = {}
    docs: dict[str, Document] = {}
    for lst in ranked_lists:
        for rank, (did, doc) in enumerate(lst, start=1):
            scores[did] = scores.get(did, 0.0) + 1.0 / (k + rank)
            docs[did] = doc
    ordered = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [(docs[i], s) for i, s in ordered]


def _doc_id(doc: Document) -> str:
    meta = doc.metadata or {}
    if meta.get("chunk_id"):
        return str(meta["chunk_id"])
    return str(hash((doc.page_content, meta.get("source_path"), meta.get("chunk_index"))))


def dashscope_rerank(query: str, docs: list[Document], top_n: int) -> list[tuple[Document, float]] | None:
    """调用通义文本重排；失败返回 None。"""
    cfg = get_runtime().get("rerank") or {}
    if (cfg.get("provider") or "dashscope") != "dashscope":
        return None
    api_key = os.getenv("DASHSCOPE_API_KEY", "").strip()
    if not api_key or not docs:
        return None
    try:
        import httpx

        model = cfg.get("model") or "gte-rerank"
        documents = [d.page_content for d in docs]
        resp = httpx.post(
            "https://dashscope.aliyuncs.com/api/v1/services/rerank/text-rerank/text-rerank",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "input": {"query": query, "documents": documents},
                "parameters": {"top_n": top_n, "return_documents": False},
            },
            timeout=30.0,
        )
        if resp.status_code >= 400:
            return None
        data = resp.json()
        results = (data.get("output") or {}).get("results") or []
        out: list[tuple[Document, float]] = []
        for item in results:
            idx = int(item.get("index", -1))
            score = float(item.get("relevance_score", 0.0))
            if 0 <= idx < len(docs):
                out.append((docs[idx], score))
        return out or None
    except Exception as e:
        log_event("rag.rerank", level=30, status="fail", error=str(e)[:200])
        return None


class HybridRetriever:
    def __init__(
        self,
        *,
        vector_search_fn,
        bm25_indexes: list[Bm25Index],
    ) -> None:
        """
        vector_search_fn(query, k) -> list[tuple[Document, float]]
        分数越大越相关（若传入距离需调用方先转换）。
        """
        self.vector_search_fn = vector_search_fn
        self.bm25_indexes = bm25_indexes
        rt = get_runtime().get("retrieve") or {}
        self.vector_k = int(rt.get("vector_k", 20))
        self.bm25_k = int(rt.get("bm25_k", 20))
        self.top_n = int(rt.get("rerank_top_n", 5))
        self.score_threshold = float(rt.get("score_threshold", 0.01))
        self.min_similarity = float(rt.get("min_similarity", 0.55))
        # BM25 分数尺度与向量不同；默认 1.0 对应至少一词级重叠/弱 Okapi
        self.bm25_min_score = float(rt.get("bm25_min_score", 1.0))

    def retrieve(self, query: str) -> tuple[list[Document], dict[str, Any]]:
        v_hits = self.vector_search_fn(query, self.vector_k)
        b_hits: list[tuple[Document, float]] = []
        for idx in self.bm25_indexes:
            b_hits.extend(idx.search(query, k=self.bm25_k))
        # 各路 BM25 合并后再截断
        b_hits = sorted(b_hits, key=lambda x: x[1], reverse=True)[: self.bm25_k]

        best_v = v_hits[0][1] if v_hits else 0.0
        best_b = b_hits[0][1] if b_hits else 0.0
        # 向量弱且 BM25 也弱才拒答（与 rag_runtime 注释一致；避免关键词强命中被误杀）
        vector_weak = best_v < self.min_similarity
        bm25_weak = best_b < self.bm25_min_score
        if vector_weak and bm25_weak:
            meta = {
                "vector_hits": len(v_hits),
                "bm25_hits": len(b_hits),
                "fused": 0,
                "rerank": "skipped",
                "rerank_top": 0,
                "gated": 0,
                "top_score": 0.0,
                "best_vector": best_v,
                "best_bm25": best_b,
                "weak_gate": True,
                "vector_weak": vector_weak,
                "bm25_weak": bm25_weak,
            }
            log_event("rag.retrieve", **meta, query_preview=str(query)[:120])
            return [], meta

        v_list = [(_doc_id(d), d) for d, _ in v_hits]
        b_list = [(_doc_id(d), d) for d, _ in b_hits]
        fused = rrf_fuse([v_list, b_list])

        meta = {
            "vector_hits": len(v_hits),
            "bm25_hits": len(b_hits),
            "fused": len(fused),
        }

        # 重排
        candidates = [d for d, _ in fused[: max(self.top_n * 4, 20)]]
        reranked = dashscope_rerank(query, candidates, self.top_n)
        if reranked is not None:
            meta["rerank"] = "dashscope"
            scored = reranked
            # DashScope 相关度通常 0~1
            threshold = 0.2
        else:
            meta["rerank"] = "rrf"
            scored = fused[: self.top_n]
            threshold = self.score_threshold

        gated = [(d, s) for d, s in scored if s >= threshold][: self.top_n]
        meta["rerank_top"] = len(scored)
        meta["gated"] = len(gated)
        meta["top_score"] = gated[0][1] if gated else 0.0

        log_event("rag.retrieve", **meta, query_preview=str(query)[:120])
        return [d for d, _ in gated], meta
