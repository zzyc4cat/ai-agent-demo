# -*- coding: utf-8 -*-
"""同一上下文下对比 qwen3.8-flash 与 deepseek-flash 的回答质量、token 与耗时。"""
from __future__ import annotations

import csv
import os
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import httpx  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

from rag.kb_meta import ensure_kb_tables  # noqa: E402
from rag.rag_service import RagSummarizeService  # noqa: E402
from services.storage import ensure_db  # noqa: E402

DASHSCOPE_KEY = os.getenv("DASHSCOPE_API_KEY", "")
DASHSCOPE_BASE = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1").rstrip("/")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", "")

MODELS = [
    ("dashscope", "qwen3.8-flash", DASHSCOPE_BASE + "/chat/completions", DASHSCOPE_KEY, {"enable_thinking": False}),
    ("deepseek", "deepseek-flash", "https://api.deepseek.com/chat/completions", DEEPSEEK_KEY, {}),
]


def call(base: str, key: str, model: str, prompt: str, extra: dict) -> dict:
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 900,
        **extra,
    }
    t0 = time.perf_counter()
    r = httpx.post(base, headers={"Authorization": f"Bearer {key}"}, json=body, timeout=120)
    ms = int((time.perf_counter() - t0) * 1000)
    r.raise_for_status()
    data = r.json()
    usage = data.get("usage") or {}
    return {
        "answer": data["choices"][0]["message"].get("content") or "",
        "in": usage.get("prompt_tokens", 0),
        "out": usage.get("completion_tokens", 0),
        "ms": ms,
    }


def main() -> int:
    rows = list(csv.DictReader(open(ROOT / "eval" / "eval_set_v1.csv", encoding="utf-8-sig")))
    rows = [r for r in rows if r["id"] in {f"s{i:02d}" for i in range(1, 11)}]

    ensure_db()
    ensure_kb_tables()
    svc = RagSummarizeService()

    out = []
    for r in rows:
        docs = svc.retrieve_docs(r["question"])
        parts = [f"[参考资料{i}] 来源:{(d.metadata or {}).get('source_path','')}\n{d.page_content}"
                 for i, d in enumerate(docs, start=1)]
        prompt = svc.prompt_template.format(input=r["question"], context="\n\n".join(parts))
        for provider, model, base, key, extra in MODELS:
            try:
                res = call(base, key, model, prompt, extra)
            except Exception as e:  # noqa: BLE001
                res = {"answer": f"[ERROR] {e}", "in": 0, "out": 0, "ms": 0}
            out.append({
                "id": r["id"], "provider": provider, "model": model,
                "question": r["question"], "answer_key": r["answer_key"],
                "tokens_in": res["in"], "tokens_out": res["out"], "ms": res["ms"],
                "answer": res["answer"][:500].replace("\n", " "),
            })
            print(f"{r['id']} {provider:<10} in={res['in']:<5} out={res['out']:<4} {res['ms']:>5}ms")

    path = ROOT / "eval" / "ab_results.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    print("saved:", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
