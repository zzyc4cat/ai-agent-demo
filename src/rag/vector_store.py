"""向量存储：多 collection、切分、与 BM25 双写。"""
from __future__ import annotations

import os
from typing import Any

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter

from model.factory import get_embedding_model, get_model_router
from rag.bm25_index import Bm25Index
from rag.embedding_cache import CachedEmbeddings
from rag.kb_meta import bump_kb_version, get_kb_file_hash, upsert_kb_file
from rag.query_cache import get_query_cache
from rag.utils_rag import file_content_hash, get_runtime, merged_chunk_config, stable_chunk_id
from utils.config_handler import chroma_config
from utils.file_handler import get_file_md5_hex, listdir_with_allowed_type, md_loader, pdf_loader, txt_loader
from utils.logger_handler import logger
from utils.path_tool import get_abs_path


def collection_name_for_sample() -> str:
    rt = get_runtime().get("collections") or {}
    return str(rt.get("sample") or "agent_sample")


def collection_name_for_personal(user_id: int) -> str:
    rt = get_runtime().get("collections") or {}
    prefix = str(rt.get("personal_prefix") or "agent_personal_")
    return f"{prefix}{user_id}"


def legacy_sample_collection() -> str:
    rt = get_runtime().get("collections") or {}
    return str(rt.get("legacy_sample") or "agent")


class VectorStoreService:
    """向量存储类（按 collection 实例化）。"""

    def __init__(self, collection_name: str | None = None):
        self.collection_name = collection_name or collection_name_for_sample()
        persist = get_abs_path(chroma_config["persist_directory"])
        try:
            emb_tag = str(
                (get_model_router().config.get("defaults") or {}).get("embedding_model_id")
                or "default"
            )
        except Exception:
            emb_tag = "default"
        emb = CachedEmbeddings(get_embedding_model(), model_tag=emb_tag)
        self.vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=emb,
            persist_directory=persist,
        )
        cfg = merged_chunk_config()
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=cfg["chunk_size"],
            chunk_overlap=cfg["chunk_overlap"],
            separators=cfg["separators"],
            length_function=len,
        )
        self.bm25 = Bm25Index(self.collection_name)

    def similarity_search_with_score(self, query: str, k: int) -> list[tuple[Document, float]]:
        """返回 (doc, relevance) 相关度越大越好。Chroma 默认距离越小越近。"""
        pairs = self.vector_store.similarity_search_with_score(query, k=k)
        out: list[tuple[Document, float]] = []
        for doc, dist in pairs:
            # 距离转相关度
            rel = 1.0 / (1.0 + float(dist))
            out.append((doc, rel))
        return out

    def delete_by_source(self, source_path: str) -> None:
        try:
            self.vector_store.delete(where={"source_path": source_path})
        except Exception as e:
            logger.warning(f"[向量删除] source={source_path} 失败: {e}")
        self.bm25.remove_by_source(source_path)
        self.bm25.save()

    def add_split_documents(self, documents: list[Document], *, source_path: str) -> int:
        for i, d in enumerate(documents):
            meta = dict(d.metadata or {})
            meta["source_path"] = source_path
            meta["chunk_index"] = i
            meta["chunk_id"] = stable_chunk_id(source_path, i)
            d.metadata = meta
        ids = [d.metadata["chunk_id"] for d in documents]
        self.vector_store.add_documents(documents, ids=ids)
        self.bm25.add_documents(documents)
        return len(documents)

    def _load_file_documents(self, path: str) -> list[Document]:
        lower = path.lower()
        if lower.endswith(".txt"):
            return txt_loader(path)
        if lower.endswith(".pdf"):
            return pdf_loader(path)
        if lower.endswith(".md") or lower.endswith(".markdown"):
            return md_loader(path)
        return []

    def _split_documents(self, documents: list[Document], path: str) -> list[Document]:
        if path.lower().endswith((".md", ".markdown")):
            try:
                headers = [("#", "h1"), ("##", "h2"), ("###", "h3")]
                md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers)
                parts: list[Document] = []
                for d in documents:
                    parts.extend(md_splitter.split_text(d.page_content))
                if parts:
                    return self.spliter.split_documents(parts)
            except Exception:
                pass
        return self.spliter.split_documents(documents)

    def ingest_path(
        self,
        data_path: str,
        *,
        corpus: str,
        scope: str,
        user_id: int | None = None,
        force: bool = False,
    ) -> dict[str, Any]:
        """增量入库目录；返回统计。"""
        allowed = tuple(chroma_config.get("allow_konwledge_file_type") or ["txt", "pdf", "md"])
        # listdir 用 endswith：补成 .ext
        allowed_suffix = tuple(a if a.startswith(".") else f".{a}" for a in allowed)
        root = get_abs_path(data_path)
        files = list(listdir_with_allowed_type(root, allowed_suffix))
        # 若旧逻辑用无点后缀，兼容再扫一遍
        if not files:
            files = list(listdir_with_allowed_type(root, allowed))

        stats = {"scanned": len(files), "ingested": 0, "skipped": 0, "chunks": 0, "errors": 0}
        for path in files:
            try:
                rel = os.path.relpath(path, get_abs_path(".")).replace("\\", "/")
                chash = file_content_hash(path)
                old = get_kb_file_hash(scope, rel)
                if not force and old == chash:
                    stats["skipped"] += 1
                    continue

                documents = self._load_file_documents(path)
                if not documents:
                    logger.warning(f"[加载知识库]{path} 无有效文本，跳过")
                    stats["skipped"] += 1
                    continue

                for d in documents:
                    d.metadata = dict(d.metadata or {})
                    d.metadata["corpus"] = corpus
                    d.metadata["source_path"] = rel

                # 变更：先删旧
                if old:
                    self.delete_by_source(rel)

                split_docs = self._split_documents(documents, path)
                if not split_docs:
                    stats["skipped"] += 1
                    continue

                n = self.add_split_documents(split_docs, source_path=rel)
                upsert_kb_file(
                    scope=scope,
                    path=rel,
                    content_hash=chash,
                    chunk_count=n,
                    user_id=user_id,
                )
                stats["ingested"] += 1
                stats["chunks"] += n
                logger.info(f"[加载知识库]{path} 加载成功 chunks={n}")
            except Exception as e:
                stats["errors"] += 1
                logger.error(f"[加载知识库]{path} 失败：{e}", exc_info=True)

        if stats["ingested"] > 0:
            bump_kb_version(scope)
            if user_id is not None:
                get_query_cache().invalidate_user(user_id)
            else:
                get_query_cache().invalidate_user(None)

        return stats

    def load_document(self) -> dict[str, Any]:
        """兼容旧接口：加载示例库 data/sample → sample collection。"""
        scope = "sample"
        return self.ingest_path(
            chroma_config.get("data_path") or "data/sample",
            corpus="sample",
            scope=scope,
            user_id=None,
        )


def get_vector_store(collection: str) -> VectorStoreService:
    return VectorStoreService(collection_name=collection)
