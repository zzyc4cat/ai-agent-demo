# -*- coding: utf-8 -*-
"""初始化租户：生成配置、建 collection、入库语料。

用法：
    python scripts/init_tenant.py --id demo2
    python scripts/init_tenant.py --id demo2 --corpus data/tenants/demo2 --force
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import yaml  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

from rag.kb_meta import ensure_kb_tables  # noqa: E402
from rag.tenant import load_tenant, tenant_path  # noqa: E402
from rag.vector_store import VectorStoreService  # noqa: E402
from services.storage import ensure_db  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--name", default=None)
    ap.add_argument("--corpus", default=None)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    tid = args.id.strip()
    path = tenant_path(tid)
    if not path.is_file():
        cfg = {
            "id": tid,
            "name": args.name or tid,
            "collection": f"agent_tenant_{tid}",
            "corpus": args.corpus or f"data/tenants/{tid}",
            "welcome": "",
            "model": "",
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False), encoding="utf-8")
        print(f"[OK] 新建配置 {path}")

    cfg = load_tenant(tid)
    ensure_db()
    ensure_kb_tables()

    store = VectorStoreService(str(cfg["collection"]))
    corpus = args.corpus or str(cfg.get("corpus") or f"data/tenants/{tid}")
    stats = store.ingest_path(
        corpus,
        corpus="tenant",
        scope=f"tenant:{tid}",
        user_id=None,
        force=args.force,
    )
    print(json.dumps({"tenant": tid, "collection": cfg["collection"], **stats}, ensure_ascii=False, indent=2))
    if stats.get("scanned", 0) == 0:
        print(f"[WARN] 语料目录为空或不存在：{corpus}")
    return 0 if stats.get("errors", 0) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
