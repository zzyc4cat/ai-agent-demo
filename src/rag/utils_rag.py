"""
RAG 公共函数：读 rag_runtime.yml、个人语料路径、查询规范化、中英分词、chunk id、切分合并配置。

tokenize 为逐汉字 + 英文词，供 BM25 使用（非 jieba）。
"""
from __future__ import annotations

import hashlib
import re
from typing import Any

from utils.config_handler import chroma_config, load_rag_runtime_config

_CJK_OR_WORD = re.compile(r"[\u4e00-\u9fff]|[a-zA-Z0-9]+")


def get_runtime() -> dict[str, Any]:
    """返回 rag_runtime.yml 解析结果。"""
    return load_rag_runtime_config()


def personal_corpus_path(user_id: int) -> str:
    """个人语料目录：{personal_data_path}/{user_id}/，避免多用户共享同一文件夹。"""
    rt = get_runtime().get("ingest") or {}
    base = str(rt.get("personal_data_path") or "data/personal").rstrip("/\\")
    return f"{base}/{int(user_id)}"


def normalize_query(q: str) -> str:
    """压缩空白并把英文字母小写，供缓存键使用。"""
    s = (q or "").strip()
    s = re.sub(r"\s+", " ", s)
    # 英文小写；中文保持原样
    parts = []
    for ch in s:
        parts.append(ch.lower() if "A" <= ch <= "Z" or "a" <= ch <= "z" else ch)
    return "".join(parts)


def tokenize(text: str) -> list[str]:
    """中英混合分词：单汉字 + 英文数字串。"""
    if not text:
        return []
    return _CJK_OR_WORD.findall(text.lower())


def stable_chunk_id(source_path: str, chunk_index: int) -> str:
    """由源路径与分块序号生成稳定 chunk_id。"""
    raw = f"{source_path}::{chunk_index}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def content_sha256(data: bytes) -> str:
    """对字节计算 SHA-256。"""
    return hashlib.sha256(data).hexdigest()


def file_content_hash(path: str) -> str:
    """流式计算文件 SHA-256，用于增量入库去重。"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def merged_chunk_config() -> dict[str, Any]:
    """合并 runtime 与 chroma.yml 的切分参数。"""
    rt = get_runtime()
    chunking = rt.get("chunking") or {}
    return {
        "chunk_size": int(chunking.get("size") or chroma_config.get("chunk_size") or 800),
        "chunk_overlap": int(chunking.get("overlap") or chroma_config.get("chunk_overlap") or 100),
        "min_chars": int(chunking.get("min_chars") or 200),
        "separators": chroma_config.get("separators")
        or ["\n\n", "\n", ".", "。", ",", "，", "!", "！", "?", "？", " ", ""],
    }
