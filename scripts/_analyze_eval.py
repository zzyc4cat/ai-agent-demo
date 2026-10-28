# -*- coding: utf-8 -*-
"""汇总评测：命中、拒答、可疑回答。"""
import csv
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
rows = list(csv.DictReader(open(ROOT / "eval" / "results_full.csv", encoding="utf-8-sig")))

ABSTAIN_MARK = ("不知道", "无法回答", "没有找到", "未提供", "未收录", "没有相关", "无法确定", "无法从")

abstain = [r for r in rows if r["id"].startswith("n")]
answerable = [r for r in rows if not r["id"].startswith("n")]

ok_abstain = [r for r in abstain if any(m in r["answer"] for m in ABSTAIN_MARK)]
print(f"库外题：{len(ok_abstain)}/{len(abstain)} 正确拒答")
for r in abstain:
    if r not in ok_abstain:
        print(f"  [硬编?] {r['id']} {r['question']} -> {r['answer'][:120]}")

def score(r):
    key = r["answer_key"]
    parts = [p for p in re.split(r"[、，,；;（）() ]+", key) if len(p) >= 2]
    if not parts:
        return 1.0
    hit = sum(1 for p in parts if p[:6] in r["answer"] or p in r["answer"])
    return hit / len(parts)

scored = sorted(answerable, key=score)
print(f"\n可答题关键词覆盖率：平均 {sum(score(r) for r in answerable)/len(answerable):.2f}")
print("\n最可疑的 8 条：")
for r in scored[:8]:
    print("=" * 70)
    print(f"{r['id']} 覆盖 {score(r):.2f}  {r['question']}")
    print("期望:", r["answer_key"][:100])
    print("回答:", r["answer"][:220].replace("\n", " "))

ms = [int(r["ms"]) for r in rows]
print(f"\n延迟：平均 {sum(ms)/len(ms):.0f} ms，最大 {max(ms)} ms")
print("provider:", {r["provider"] for r in rows})
