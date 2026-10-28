# -*- coding: utf-8 -*-
"""基于 eval_set_v1.csv 跑检索与回答评测。

用法：
    python scripts/eval_kb.py --ids s01-s10 --out eval/results.csv
    python scripts/eval_kb.py --ids s01,s02 --no-llm
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

from rag.kb_meta import ensure_kb_tables  # noqa: E402
from rag.rag_service import RagSummarizeService  # noqa: E402
from services.storage import ensure_db  # noqa: E402


def call_deepseek(prompt_text: str) -> str:
    """qwen 限流时的降级通道，直接用 DeepSeek OpenAI 兼容接口。"""
    import os

    import httpx

    key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not key:
        raise RuntimeError("DEEPSEEK_API_KEY 未配置")
    resp = httpx.post(
        "https://api.deepseek.com/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt_text}],
            "temperature": 0,
            "max_tokens": 900,
        },
        timeout=90.0,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def parse_ids(spec: str) -> set[str]:
    out: set[str] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            prefix = "".join(c for c in a if not c.isdigit())
            lo = int("".join(c for c in a if c.isdigit()))
            hi = int("".join(c for c in b if c.isdigit()))
            for i in range(lo, hi + 1):
                out.add(f"{prefix}{i:02d}")
        else:
            out.add(part)
    return out


def doc_rank(docs, expected: str) -> int:
    """返回期望文档第一次出现的位置（1 起），没有返回 0。"""
    if not expected:
        return 0
    targets = [t for t in expected.split("|") if t]
    for idx, d in enumerate(docs, start=1):
        src = str((d.metadata or {}).get("source_path", "")).replace("\\", "/")
        for t in targets:
            if src.endswith(t):
                return idx
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(ROOT / "eval" / "eval_set_v1.csv"))
    ap.add_argument("--ids", required=True)
    ap.add_argument("--out", default=str(ROOT / "eval" / "results.csv"))
    ap.add_argument("--no-llm", action="store_true", help="只测检索，不调用生成模型")
    args = ap.parse_args()

    wanted = parse_ids(args.ids)
    with open(args.csv, encoding="utf-8-sig", newline="") as fh:
        all_rows = list(csv.DictReader(fh))
    rows = all_rows if args.ids.strip().lower() in {"all", "*"} else [r for r in all_rows if r["id"] in wanted]

    ensure_db()
    ensure_kb_tables()
    svc = RagSummarizeService()

    results = []
    qwen_dead = False
    print(f"{'id':<5}{'hit@5':<7}{'rank':<6}{'docs':<6}{'ms':<7}question")
    for r in rows:
        q = r["question"]
        t0 = time.perf_counter()
        docs = svc.retrieve_docs(q)
        ms = int((time.perf_counter() - t0) * 1000)
        rank = doc_rank(docs, r["expected_doc"])

        answer = ""
        provider = ""
        if docs and not args.no_llm:
            parts = []
            for i, d in enumerate(docs, start=1):
                src = (d.metadata or {}).get("source_path", "")
                parts.append(f"[参考资料{i}] 来源:{src}\n{d.page_content}")
            context = "\n\n".join(parts)
            try:
                if qwen_dead:
                    raise RuntimeError("429 qwen disabled")
                answer = svc._chain().invoke({"input": q, "context": context})
                provider = "dashscope"
            except Exception as e:  # noqa: BLE001
                msg = str(e)
                if "429" in msg or "Throttling" in msg or "rate limit" in msg.lower() or "disabled" in msg:
                    qwen_dead = True
                    try:
                        prompt_text = svc.prompt_template.format(input=q, context=context)
                        answer = call_deepseek(prompt_text)
                        provider = "deepseek(fallback)"
                    except Exception as e2:  # noqa: BLE001
                        answer = f"[ERROR] qwen 429; deepseek 也失败: {e2}"
                else:
                    answer = f"[ERROR] {msg}"

        results.append({
            "id": r["id"],
            "type": r["type"],
            "question": q,
            "expected_doc": r["expected_doc"],
            "hit5": 1 if rank and rank <= 5 else 0,
            "rank": rank,
            "docs": len(docs),
            "ms": ms,
            "provider": provider,
            "answer": (answer or "")[:600],
            "answer_key": r["answer_key"],
        })
        print(f"{r['id']:<5}{'YES' if rank and rank <= 5 else 'no':<7}{rank:<6}{len(docs):<6}{ms:<7}{q[:36]}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)

    hit = sum(x["hit5"] for x in results)
    print(f"\n命中 {hit}/{len(results)}  → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
