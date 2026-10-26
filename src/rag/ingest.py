"""
知识库增量入库 CLI。

sample：chroma.yml data_path（默认 data/sample）→ collection agent_sample
personal：必须 --user，默认 data/personal/{user_id}/ → agent_personal_{id}
--force 忽略 hash 强制重建。成功打印 JSON stats。
"""
from __future__ import annotations

import argparse
import json
import sys

from rag.kb_meta import ensure_kb_tables
from rag.vector_store import (
    VectorStoreService,
    collection_name_for_personal,
    collection_name_for_sample,
)
from services.storage import ensure_db
from utils.config_handler import chroma_config


def main(argv: list[str] | None = None) -> int:
    """解析 CLI 参数并对 sample/personal 目录执行增量入库。"""
    ensure_db()
    ensure_kb_tables()
    p = argparse.ArgumentParser(description="RAG 知识库增量入库")
    p.add_argument("--scope", choices=["sample", "personal"], required=True)
    p.add_argument("--user", type=int, default=None, help="personal 时必填 user_id")
    p.add_argument("--path", default=None, help="覆盖默认数据目录")
    p.add_argument("--force", action="store_true", help="忽略 content_hash 强制重建文件")
    args = p.parse_args(argv)

    if args.scope == "sample":
        coll = collection_name_for_sample()
        path = args.path or chroma_config.get("data_path") or "data/sample"
        store = VectorStoreService(coll)
        stats = store.ingest_path(path, corpus="sample", scope="sample", user_id=None, force=args.force)
    else:
        if args.user is None:
            print("personal 范围必须提供 --user", file=sys.stderr)
            return 2
        from rag.utils_rag import personal_corpus_path

        path = args.path or personal_corpus_path(args.user)
        coll = collection_name_for_personal(args.user)
        store = VectorStoreService(coll)
        stats = store.ingest_path(
            path,
            corpus="personal",
            scope=f"personal:{args.user}",
            user_id=args.user,
            force=args.force,
        )

    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0 if stats.get("errors", 0) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
