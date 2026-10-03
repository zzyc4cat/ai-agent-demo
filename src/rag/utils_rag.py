"""RAG 公共工具：分词、规范化、配置读取。"""
from __future__ import annotations

import hashlib
import re
from typing import Any

from utils.config_handler import chroma_config, load_rag_runtime_config

_CJK_OR_WORD = re.compile(r"[\u4e00-\u9fff]|[a-zA-Z0-9]+")


def get_runtime() -> dict[str, Any]:
    return load_rag_runtime_config()


def personal_corpus_path(user_id: int) -> str:
    """个人语料目录：{personal_data_path}/{user_id}/，避免多用户共享同一文件夹。"""
    rt = get_runtime().get("ingest") or {}
    base = str(rt.get("personal_data_path") or "data/personal").rstrip("/\\")
    return f"{base}/{int(user_id)}"


def normalize_query(q: str) -> str:
    s = (q or "").strip()
    s = re.sub(r"\s+", " ", s)
    # 英文小写；中文保持原样
    parts = []
    for ch in s:
        parts.append(ch.lower() if "A" <= ch <= "Z" or "a" <= ch <= "z" else ch)
    return "".join(parts)


def tokenize(text: str) -> list[str]:
    if not text:
        return []
    return _CJK_OR_WORD.findall(text.lower())


def stable_chunk_id(source_path: str, chunk_index: int) -> str:
    raw = f"{source_path}::{chunk_index}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def content_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_content_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def merged_chunk_config() -> dict[str, Any]:
    rt = get_runtime()
    chunking = rt.get("chunking") or {}
    return {
        "chunk_size": int(chunking.get("size") or chroma_config.get("chunk_size") or 800),
        "chunk_overlap": int(chunking.get("overlap") or chroma_config.get("chunk_overlap") or 100),
        "separators": chroma_config.get("separators")
        or ["\n\n", "\n", ".", "。", ",", "，", "!", "！", "?", "？", " ", ""],
    }
