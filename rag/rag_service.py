"""RAG 总结：检索 + 提示词；资料不足由 Prompt 约束回答不知道。"""
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from agent.tools.prompt_guard import wrap_untrusted
from model.factory import get_chat_model
from rag.vector_store import VectorStoreService
from utils.logger_handler import log_event, should_log_prompt
from utils.prompt_loader import load_rag_prompts


class RagSummarizeService(object):
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.retriever = self.vector_store.get_retriever()
        self.prompt_text = load_rag_prompts()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)

    def _chain(self):
        model = get_chat_model()

        def maybe_log_prompt(prompt):
            if should_log_prompt():
                log_event("rag.prompt", preview=str(prompt)[:500])
            return prompt

        return self.prompt_template | maybe_log_prompt | model | StrOutputParser()

    def retriever_docs(self, query) -> list[Document]:
        docs = self.retriever.invoke(query)
        log_event("rag.retrieve", query_preview=str(query)[:120], hit_count=len(docs))
        if not docs:
            log_event("rag.retrieve", level=30, status="empty", query_preview=str(query)[:120])
        return docs

    def rag_summarize(self, query: str) -> str:
        context_docs = self.retriever_docs(query)
        if not context_docs:
            return "不知道"

        parts = []
        for i, doc in enumerate(context_docs, start=1):
            raw = f"[参考资料{i}] {doc.page_content} | 元数据：{doc.metadata}"
            parts.append(wrap_untrusted(f"rag#{i}", raw))
        context = "\n".join(parts)
        return self._chain().invoke({"input": query, "context": context})
