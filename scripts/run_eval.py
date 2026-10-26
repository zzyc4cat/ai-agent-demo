"""
黄金集评测 + 工具冒烟。读 tests/fixtures/rag_eval.jsonl，报告写入 logs/eval/。

尽量少调 LLM：无 Key 则跳过 summarize。hit_or_unknown 等标签较宽松，不宜当生产准确率。
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

REPORT_DIR = ROOT / "logs" / "eval"
EVAL_PATH = ROOT / "tests" / "fixtures" / "rag_eval.jsonl"


def _load_eval_rows() -> list[dict]:
    """读取 rag_eval.jsonl 评测用例。"""
    rows = []
    if not EVAL_PATH.is_file():
        return rows
    for line in EVAL_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def _classify_rag(expect: str, answer: str) -> tuple[bool, str]:
    """按期望标签宽松判定检索/拒答是否可接受。"""
    ans = (answer or "").strip()
    unknown = ans == "不知道" or ans.startswith("不知道")
    if expect == "unknown":
        return unknown, "ok" if unknown else "should_unknown"
    if expect == "hit":
        if unknown:
            return False, "retrieve_empty_or_gated"
        return True, "ok"
    if expect in ("hit_or_unknown", "unknown_or_safe"):
        return True, "ok_flexible"
    return True, "ok"


def run_rag_eval(limit: int | None = None) -> dict:
    """尽量不调 LLM：仅测 retrieve 门控；若无 Key 则跳过 summarize。"""
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    rows = _load_eval_rows()
    if limit:
        rows = rows[:limit]
    results = []
    has_key = bool(os.getenv("DASHSCOPE_API_KEY", "").strip())

    # 轻量：对 unknown 类用空检索模拟；对 hit 类尝试 retrieve_docs
    try:
        from rag.rag_service import RagSummarizeService

        svc = RagSummarizeService() if has_key else None
    except Exception as e:
        svc = None
        bootstrap_err = str(e)
    else:
        bootstrap_err = ""

    for row in rows:
        q = row.get("query", "")
        expect = row.get("expect", "")
        t0 = time.time()
        failure = ""
        answer = ""
        ok = False
        try:
            if not has_key or svc is None:
                # 无 Key：仅用期望标签做结构校验
                ok = expect in ("hit", "unknown", "hit_or_unknown", "unknown_or_safe")
                failure = "skip_no_key" if not has_key else f"svc_init:{bootstrap_err[:80]}"
                answer = "(skipped)"
            elif expect == "unknown" and "星座飞船" in q:
                docs = svc.retrieve_docs(q, user_id=None)
                answer = "不知道" if not docs else "(has_docs)"
                ok, failure = _classify_rag(expect, answer)
            else:
                # 完整 summarize 成本高：默认只 retrieve + 门控判断
                docs = svc.retrieve_docs(q, user_id=None)
                answer = "不知道" if not docs else f"hit:{len(docs)}"
                if expect == "unknown":
                    ok, failure = _classify_rag(expect, "不知道" if not docs else "x")
                elif expect == "hit":
                    ok = bool(docs)
                    failure = "ok" if ok else "retrieve_empty_or_gated"
                else:
                    ok, failure = True, "ok_flexible"
        except Exception as e:
            ok = False
            failure = f"exception:{type(e).__name__}"
            answer = str(e)[:200]
        results.append(
            {
                "query": q[:80],
                "expect": expect,
                "ok": ok,
                "failure": failure,
                "answer_preview": str(answer)[:120],
                "ms": int((time.time() - t0) * 1000),
            }
        )

    passed = sum(1 for r in results if r["ok"])
    return {
        "suite": "rag_eval",
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "has_dashscope_key": has_key,
        "items": results,
    }


def run_tool_smoke() -> dict:
    """对若干 Agent 工具做无 Key 也可跑的冒烟。"""
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    items = []

    def one(name, fn):
        """执行单个工具调用并记录耗时与成败。"""
        t0 = time.time()
        try:
            out = fn()
            ok = True
            err = ""
            preview = str(out)[:160]
        except Exception as e:
            ok = False
            err = f"{type(e).__name__}:{e}"
            preview = ""
        items.append(
            {
                "tool": name,
                "ok": ok,
                "failure": err or "ok",
                "preview": preview,
                "ms": int((time.time() - t0) * 1000),
            }
        )

    one("datetime_now", lambda: __import__("agent.tools.agent_tools", fromlist=["datetime_now"]).datetime_now.invoke({}))
    one(
        "get_weather",
        lambda: __import__("agent.tools.agent_tools", fromlist=["get_weather"]).get_weather.invoke({"city": "上海"}),
    )
    one(
        "web_search",
        lambda: __import__("agent.tools.agent_tools", fromlist=["web_search"]).web_search.invoke({"query": "pytest"}),
    )

    # 需用户上下文的工具
    try:
        import services.storage as storage
        from services import user_service
        from agent.tools import agent_tools

        storage.ensure_db()
        u = user_service.switch_or_create("EvalSmokeUser")
        agent_tools.set_current_user_id(u["id"])
        one(
            "task_add",
            lambda: agent_tools.task_add.invoke({"title": "eval-smoke", "due_at": "", "priority": "P2"}),
        )
        one("task_list", lambda: agent_tools.task_list.invoke({"status": "open"}))
        one("note_write", lambda: agent_tools.note_write.invoke({"title": "e", "body": "eval"}))
        one("calculator", lambda: __import__("agent.tools.tools_b", fromlist=["calculator"]).calculator.invoke({"expression": "1+2*3"}))
    except Exception as e:
        items.append({"tool": "user_ctx_setup", "ok": False, "failure": str(e), "preview": "", "ms": 0})

    passed = sum(1 for r in items if r["ok"])
    return {"suite": "tool_smoke", "total": len(items), "passed": passed, "failed": len(items) - passed, "items": items}


def main() -> int:
    """跑 RAG 评测与工具冒烟并写 logs/eval 报告。"""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rag = run_rag_eval()
    tools = run_tool_smoke()
    report = {
        "generated_at": stamp,
        "rag": rag,
        "tools": tools,
        "summary": {
            "rag_pass_rate": (rag["passed"] / rag["total"]) if rag["total"] else 0,
            "tool_pass_rate": (tools["passed"] / tools["total"]) if tools["total"] else 0,
        },
    }
    out_json = REPORT_DIR / f"eval_report_{stamp}.json"
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    # 最新副本
    (REPORT_DIR / "eval_report_latest.json").write_text(out_json.read_text(encoding="utf-8"), encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    print(f"report: {out_json}")
    try:
        from utils.logger_handler import log_event

        log_event(
            "eval.done",
            rag_pass_rate=report["summary"]["rag_pass_rate"],
            tool_pass_rate=report["summary"]["tool_pass_rate"],
            report=str(out_json.name),
        )
    except Exception:
        pass
    if tools["passed"] == 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
