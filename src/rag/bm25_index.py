"""
BM25 倒排（rank_bm25），按 collection 序列化到 storage/bm25_index/{name}.pkl。

pkl 视为本机可信文件。极少文档时 Okapi 分全 0 则回退词重叠计数。
"""
from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

from langchain_core.documents import Document

from rag.utils_rag import get_runtime, tokenize
from utils.path_tool import get_abs_path

try:
    from rank_bm25 import BM25Okapi
except ImportError:  # pragma: no cover
    BM25Okapi = None  # type: ignore


class Bm25Index:
    def __init__(self, collection: str) -> None:
        """为指定 collection 加载或创建磁盘 BM25 索引。"""
        self.collection = collection
        self.docs: list[Document] = []
        self._tokens: list[list[str]] = []
        self._bm25: Any = None
        self.path = Path(get_abs_path(f"storage/bm25_index/{collection}.pkl"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.load()

    def load(self) -> None:
        """从 pkl 恢复文档与词表并重建 Okapi。"""
        if not self.path.exists():
            return
        try:
            data = pickle.loads(self.path.read_bytes())
            self.docs = data.get("docs") or []
            self._tokens = data.get("tokens") or []
            self._rebuild()
        except Exception:
            self.docs = []
            self._tokens = []
            self._bm25 = None

    def save(self) -> None:
        """把文档与分词结果序列化到磁盘。"""
        payload = {"docs": self.docs, "tokens": self._tokens}
        self.path.write_bytes(pickle.dumps(payload, protocol=pickle.HIGHEST_PROTOCOL))

    def _rebuild(self) -> None:
        """用当前词表重建 BM25Okapi 对象。"""
        if BM25Okapi is None or not self._tokens:
            self._bm25 = None
            return
        self._bm25 = BM25Okapi(self._tokens)

    def clear(self) -> None:
        """清空内存索引并删除 pkl 文件。"""
        self.docs = []
        self._tokens = []
        self._bm25 = None
        if self.path.exists():
            self.path.unlink()

    def remove_by_source(self, source_path: str) -> None:
        """删除指定 source_path 的全部分块。"""
        keep_docs = []
        keep_tok = []
        for d, t in zip(self.docs, self._tokens):
            if (d.metadata or {}).get("source_path") != source_path:
                keep_docs.append(d)
                keep_tok.append(t)
        self.docs = keep_docs
        self._tokens = keep_tok
        self._rebuild()

    def add_documents(self, documents: list[Document]) -> None:
        """追加文档、分词、重建并落盘。"""
        for d in documents:
            self.docs.append(d)
            self._tokens.append(tokenize(d.page_content or ""))
        self._rebuild()
        self.save()

    def search(self, query: str, k: int = 20) -> list[tuple[Document, float]]:
        """按查询返回 Top-k (文档, 分数)；无正分则词重叠回退。"""
        if not self.docs:
            return []
        q = tokenize(query)
        if not q:
            return []
        scores: list[float]
        if self._bm25 is not None:
            scores = [float(x) for x in self._bm25.get_scores(q)]
        else:
            scores = [0.0] * len(self.docs)
        # 极少文档时 Okapi IDF 可能全为 0，回退到词重叠计数
        if not any(s > 0 for s in scores):
            qset = set(q)
            scores = []
            for toks in self._tokens:
                overlap = len(qset.intersection(toks))
                scores.append(float(overlap))
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:k]
        out: list[tuple[Document, float]] = []
        for idx, sc in ranked:
            if sc <= 0:
                continue
            out.append((self.docs[idx], float(sc)))
        return out
