# -*- coding: utf-8 -*-
"""打印指定查询的召回块，定位“答不出”的原因。"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

from rag.rag_service import RagSummarizeService  # noqa: E402

QUERIES = [
    "X1 报 HMS 0300-0100-0001-0003，说明文档列出的常见原因有哪些？",
    "喷嘴温度传感器可能开路时，文档建议先检查什么？",
    "打印机检测不到 AMS 时，操作指导分哪几步？",
]

svc = RagSummarizeService()
for q in QUERIES:
    print("=" * 80)
    print("Q:", q)
    for i, d in enumerate(svc.retrieve_docs(q), start=1):
        meta = d.metadata or {}
        src = Path(str(meta.get("source_path", ""))).name
        text = (d.page_content or "").replace("\n", " ")
        print(f"{i}. [{src}] len={len(text)}")
        print("   ", text[:110])
