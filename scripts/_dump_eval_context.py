# -*- coding: utf-8 -*-
"""为出评测题生成语料摘要：每篇的标题、章节、首段。"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1] / "data" / "tenants" / "demo"
FILES = sorted(ROOT.rglob("*.md"))

for p in FILES:
    if p.name == "NOTICE.md":
        continue
    text = p.read_text(encoding="utf-8", errors="ignore")
    title = ""
    m = re.search(r"^title:\s*(.+)$", text, re.M)
    if m:
        title = m.group(1).strip()
    heads = [h.strip() for h in re.findall(r"^#{1,3}\s+(.+)$", text, re.M)]
    # 首个正文段落（跳过 front-matter、引用行、标题）
    body = re.sub(r"^---.*?---", "", text, flags=re.S)
    paras = [
        ln.strip() for ln in body.splitlines()
        if ln.strip() and not ln.startswith(("#", ">", "|", "-", "*", "!"))
    ]
    first = paras[0][:120] if paras else ""
    rel = p.relative_to(ROOT).as_posix()
    print(f"### {rel}")
    print(f"T: {title}")
    print(f"H: {' / '.join(heads[:6])}")
    print(f"P: {first}")
    print()
