"""
RAG 总结服务：L2 答案缓存 → L1 文档缓存 → 混合检索 → 填 Prompt 调聊天模型。

无命中返回「不知道」。登录用户会同时检索 sample + personal collection。
L2 cache key 含当前 Auto 聊天模型 id，避免换模串答案。
"""
from __future__ import annotations

import hashlib
import re
from typing import Any

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from agent.tools.prompt_guard import wrap_untrusted
from model.factory import get_chat_model, get_model_router
from rag.bm25_index import Bm25Index
from rag.kb_meta import get_kb_version
from rag.query_cache import QueryCache, get_query_cache
from rag.retriever import HybridRetriever
from rag.tenant import load_tenant
from rag.utils_rag import get_runtime
from rag.vector_store import (
    VectorStoreService,
    collection_name_for_personal,
    collection_name_for_sample,
    legacy_sample_collection,
)
from utils.logger_handler import log_event, should_log_prompt
from utils.prompt_loader import load_rag_prompts


def _prompt_version(text: str) -> str:
    """对 RAG Prompt 文本做短哈希，纳入 L2 缓存键。"""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def _serialize_docs(docs: list[Document]) -> list[dict[str, Any]]:
    """把 Document 列表转成可 JSON 缓存的字典。"""
    return [
        {"page_content": d.page_content, "metadata": dict(d.metadata or {})}
        for d in docs
    ]


def _deserialize_docs(rows: list[dict[str, Any]]) -> list[Document]:
    """把缓存字典还原为 Document。"""
    return [Document(page_content=r["page_content"], metadata=r.get("metadata") or {}) for r in rows]


_CODE_RE = re.compile(r"\b\d{4}-\d{4}-\d{4}-\d{4}\b")


class RagSummarizeService:
    """对外 rag_summarize / retrieve_docs；工具 rag_summarize 与 API /rag/summarize 共用。"""

    tenant_id: str | None = None

    def __init__(self, tenant_id: str | None = None) -> None:
        """加载 Prompt 并打开对应租户的向量库（缺省为 sample）。"""
        self.tenant_id = tenant_id
        self._tenant_cfg = load_tenant(tenant_id) if tenant_id else {}
        self.prompt_text = load_rag_prompts()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.prompt_ver = _prompt_version(self.prompt_text)
        collection = (
            str(self._tenant_cfg.get("collection"))
            if tenant_id
            else collection_name_for_sample()
        )
        self.sample_store = VectorStoreService(collection)
        self._legacy_name = None if tenant_id else legacy_sample_collection()
        self.cache = get_query_cache()

    def _chain(self):
        """组装 Prompt → 可选日志 → 聊天模型 → 字符串。"""
        model = get_chat_model()

        def maybe_log_prompt(prompt):
            """DEBUG 时记录即将发给模型的 Prompt 预览。"""
            if should_log_prompt():
                log_event("rag.prompt", preview=str(prompt)[:500])
            return prompt

        return self.prompt_template | maybe_log_prompt | model | StrOutputParser()

    def _stores_for_user(self, user_id: int | None) -> list[VectorStoreService]:
        """返回当前租户的 collection；非租户模式兼容 sample/legacy/个人库。"""
        stores = [self.sample_store]
        if self._legacy_name and self._legacy_name != self.sample_store.collection_name:
            try:
                stores.append(VectorStoreService(self._legacy_name))
            except Exception:
                pass
        if user_id is not None and not self.tenant_id:
            stores.append(VectorStoreService(collection_name_for_personal(int(user_id))))
        return stores

    def _kb_version_token(self, user_id: int | None) -> str:
        """拼接当前租户/用户相关知识库版本，作缓存失效依据。"""
        if self.tenant_id:
            return get_kb_version(f"tenant:{self.tenant_id}")
        parts = [get_kb_version("sample")]
        if user_id is not None:
            parts.append(get_kb_version(f"personal:{user_id}"))
        return "|".join(parts)

    def retrieve_docs(self, query: str, user_id: int | None = None) -> list[Document]:
        """对用户可见语料做混合检索，返回入选文档。"""
        stores = self._stores_for_user(user_id)

        def vector_search(q: str, k: int) -> list[tuple[Document, float]]:
            """合并多 collection 向量命中并按相关度截断。"""
            merged: list[tuple[Document, float]] = []
            for st in stores:
                merged.extend(st.similarity_search_with_score(q, k=k))
            merged.sort(key=lambda x: x[1], reverse=True)
            return merged[:k]

        bm25s = [st.bm25 for st in stores]
        retriever = HybridRetriever(vector_search_fn=vector_search, bm25_indexes=bm25s)
        docs, meta = retriever.retrieve(query)

        # 精确代码查询：HMS 代码在向量空间里区分度低，用原文包含匹配补一条通道
        code_match = _CODE_RE.search(query)
        if code_match:
            exact: list[Document] = []
            for st in stores:
                exact.extend(st.get_by_text_contains(code_match.group(0), limit=3))
            if exact:
                seen = {str((d.metadata or {}).get("chunk_id")) for d in docs}
                head = []
                for d in exact:
                    cid = str((d.metadata or {}).get("chunk_id"))
                    if cid and cid not in seen:
                        head.append(d)
                        seen.add(cid)
                if head:
                    docs = (head + docs)[: max(len(docs), 1)]
                    log_event("rag.exact_code", code=code_match.group(0), hits=len(head))

        if not docs:
            log_event("rag.retrieve", level=30, status="empty", query_preview=str(query)[:120], **meta)
        return docs

    def rag_summarize(self, query: str, user_id: int | None = None) -> str:
        """走 L2/L1 缓存或检索后生成总结；无命中返回不知道。"""
        scope = (
            f"t:{self.tenant_id}:u:{user_id}"
            if self.tenant_id
            else (f"u:{user_id}" if user_id is not None else "u:anon")
        )
        kb_ver = self._kb_version_token(user_id)
        corpus_scope = (
            f"tenant:{self.tenant_id}"
            if self.tenant_id
            else ("sample+personal" if user_id is not None else "sample")
        )
        cache = self.cache

        try:
            _, chat_spec = get_model_router().get_chat_model(mode="auto")
            chat_model_id = chat_spec.id
        except Exception:
            chat_model_id = "chat"
        l2_key = QueryCache.make_key(
            query,
            user_id=user_id,
            kb_version=kb_ver,
            corpus_scope=corpus_scope,
            prompt_version=self.prompt_ver,
            model_id=chat_model_id,
            layer="l2",
        )
        hit = cache.get(l2_key, scope)
        if hit and hit.kind in ("answer", "empty"):
            return str(hit.payload)

        l1_key = QueryCache.make_key(
            query,
            user_id=user_id,
            kb_version=kb_ver,
            corpus_scope=corpus_scope,
            layer="l1",
        )
        docs: list[Document] | None = None
        hit1 = cache.get(l1_key, scope)
        if hit1 and hit1.kind == "docs":
            docs = _deserialize_docs(hit1.payload)
        elif hit1 and hit1.kind == "empty":
            docs = []

        if docs is None:
            docs = self.retrieve_docs(query, user_id=user_id)
            cfg = cache
            if not docs:
                cfg.set(l1_key, scope, "empty", [], cfg.empty_ttl)
            else:
                cfg.set(l1_key, scope, "docs", _serialize_docs(docs), cfg.l1_ttl)

        if not docs:
            cache.set(l2_key, scope, "empty", "不知道", cache.empty_ttl)
            return "不知道"

        parts = []
        for i, doc in enumerate(docs, start=1):
            src = (doc.metadata or {}).get("source_path", "")
            cid = (doc.metadata or {}).get("chunk_id", "")
            raw = f"[参考资料{i}] 来源:{src} chunk:{cid}\n{doc.page_content} | 元数据：{doc.metadata}"
            parts.append(wrap_untrusted(f"rag#{i}", raw))
        context = "\n".join(parts)
        answer = self._chain().invoke({"input": query, "context": context})
        cache.set(l2_key, scope, "answer", answer, cache.l2_ttl)
        return answer
