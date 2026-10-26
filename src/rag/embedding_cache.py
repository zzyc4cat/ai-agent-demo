"""
Embedding 磁盘 JSON 缓存：key = sha256(model_tag + 文本)。

目录默认 storage/embedding_cache/。model_tag 应使用 embedding 模型 id。
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from langchain_core.embeddings import Embeddings

from rag.utils_rag import get_runtime
from utils.path_tool import get_abs_path


class CachedEmbeddings(Embeddings):
    """包装底层 Embeddings，缓存 embed_documents / embed_query。"""

    def __init__(self, inner: Embeddings, model_tag: str = "default") -> None:
        """包装底层 Embeddings 并配置磁盘缓存目录。"""
        self.inner = inner
        self.model_tag = model_tag
        cfg = get_runtime().get("embedding_cache") or {}
        self.enabled = bool(cfg.get("enabled", True))
        self.root = Path(get_abs_path(cfg.get("directory") or "storage/embedding_cache"))
        if self.enabled:
            self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, text: str) -> Path:
        """计算某段文本对应的缓存 JSON 路径。"""
        h = hashlib.sha256(f"{self.model_tag}:{text}".encode("utf-8")).hexdigest()
        return self.root / f"{h}.json"

    def _get(self, text: str) -> list[float] | None:
        """读磁盘缓存向量，未命中返回 None。"""
        if not self.enabled:
            return None
        p = self._path(text)
        if not p.exists():
            return None
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _set(self, text: str, vec: list[float]) -> None:
        """把向量写入磁盘 JSON。"""
        if not self.enabled:
            return
        try:
            self._path(text).write_text(json.dumps(vec), encoding="utf-8")
        except Exception:
            pass

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """批量向量化，仅对缓存未命中的文本调底层。"""
        out: list[list[float] | None] = [self._get(t) for t in texts]
        missing_idx = [i for i, v in enumerate(out) if v is None]
        if missing_idx:
            to_embed = [texts[i] for i in missing_idx]
            fresh = self.inner.embed_documents(to_embed)
            for i, vec in zip(missing_idx, fresh):
                out[i] = vec
                self._set(texts[i], vec)
        return [v if v is not None else [] for v in out]

    def embed_query(self, text: str) -> list[float]:
        """查询向量化，优先读缓存。"""
        cached = self._get(text)
        if cached is not None:
            return cached
        vec = self.inner.embed_query(text)
        self._set(text, vec)
        return vec
