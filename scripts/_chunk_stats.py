# -*- coding: utf-8 -*-
"""统计 chunk 长度分布，定位“命中文档但答不出”的原因。"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

from rag.vector_store import VectorStoreService  # noqa: E402

svc = VectorStoreService("agent_sample")
data = svc.vector_store.get(include=["documents", "metadatas"])
docs = data.get("documents") or []
metas = data.get("metadatas") or []
lens = sorted(len(d or "") for d in docs)
print("chunks:", len(lens))
if lens:
    def pct(p):
        return lens[min(len(lens) - 1, int(len(lens) * p))]
    print("min:", lens[0], "p25:", pct(.25), "median:", pct(.5), "p75:", pct(.75), "max:", lens[-1])
    print("短于 100 字:", sum(1 for x in lens if x < 100))
    print("短于 200 字:", sum(1 for x in lens if x < 200))

tiny = [(m.get("source_path", ""), len(d or "")) for d, m in zip(docs, metas) if len(d or "") < 100]
print("\n示例（<100 字）:")
for src, n in tiny[:8]:
    print(f"  {n:>4}  {Path(src).name}")
