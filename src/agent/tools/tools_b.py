"""简易计算与闪卡（Tools-B 子集）。"""
from __future__ import annotations

import ast
import operator
from datetime import datetime, timedelta

from langchain_core.tools import tool

from agent.tools.agent_tools import get_current_user_id
from agent.tools.prompt_guard import wrap_untrusted
from services.storage import get_conn, ensure_db

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _eval(node):
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("仅支持加减乘除与幂运算的数值表达式")


@tool(description="精确计算数学表达式，如 2+3*4。禁止函数调用。")
def calculator(expression: str) -> str:
    try:
        expr = (expression or "").strip()
        if not expr or len(expr) > 200:
            return wrap_untrusted("tool:calculator", "不知道：表达式过长或为空（上限 200 字符）")
        tree = ast.parse(expr, mode="eval")
        # 限制幂运算深度，避免 9**9**9 类资源耗尽
        pow_count = sum(isinstance(n, ast.Pow) for n in ast.walk(tree))
        if pow_count > 2:
            return wrap_untrusted("tool:calculator", "不知道：幂运算嵌套过多")
        value = _eval(tree)
        if isinstance(value, (int, float)) and abs(value) > 1e100:
            return wrap_untrusted("tool:calculator", "不知道：结果数值过大")
        return wrap_untrusted("tool:calculator", str(value))
    except Exception as e:
        return wrap_untrusted("tool:calculator", f"不知道：无法计算（{type(e).__name__}）")


def _ensure_flashcards():
    ensure_db()
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                front TEXT NOT NULL,
                back TEXT NOT NULL,
                due_at TEXT NOT NULL,
                interval_days INTEGER NOT NULL DEFAULT 1
            )
            """
        )


@tool(description="添加闪卡。入参 front 正面问题，back 背面答案。")
def flashcard_add(front: str, back: str) -> str:
    _ensure_flashcards()
    uid = get_current_user_id()
    due = datetime.now().strftime("%Y-%m-%d")
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO flashcards(user_id, front, back, due_at, interval_days) VALUES (?,?,?,?,1)",
            (uid, front.strip(), back.strip(), due),
        )
        return wrap_untrusted("tool:flashcard_add", f"id={cur.lastrowid}")


@tool(description="列出当前用户到期闪卡。")
def flashcard_due() -> str:
    _ensure_flashcards()
    uid = get_current_user_id()
    today = datetime.now().strftime("%Y-%m-%d")
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, front, back, due_at FROM flashcards WHERE user_id=? AND due_at<=? ORDER BY id",
            (uid, today),
        ).fetchall()
        if not rows:
            return wrap_untrusted("tool:flashcard_due", "无到期闪卡")
        return wrap_untrusted("tool:flashcard_due", str([dict(r) for r in rows]))


@tool(description="复习反馈。入参 card_id；correct 为 true/false。")
def flashcard_answer(card_id: int, correct: bool) -> str:
    _ensure_flashcards()
    uid = get_current_user_id()
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM flashcards WHERE id=? AND user_id=?",
            (int(card_id), uid),
        ).fetchone()
        if not row:
            return wrap_untrusted("tool:flashcard_answer", "不知道：闪卡不存在")
        interval = 1 if not correct else max(1, int(row["interval_days"]) * 2)
        due = (datetime.now() + timedelta(days=interval)).strftime("%Y-%m-%d")
        conn.execute(
            "UPDATE flashcards SET interval_days=?, due_at=? WHERE id=? AND user_id=?",
            (interval, due, int(card_id), uid),
        )
        return wrap_untrusted(
            "tool:flashcard_answer",
            f"updated interval_days={interval} due_at={due}",
        )


TOOLS_B = [calculator, flashcard_add, flashcard_due, flashcard_answer]
