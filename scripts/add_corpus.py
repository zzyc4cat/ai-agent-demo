# -*- coding: utf-8 -*-
"""向 corpus.csv 追加一行，自动处理逗号/引号转义。

用法：
    python scripts/add_corpus.py ^
      --file data/tenants/demo/fault_codes/X1_fault_code_v1.0_xxx.md ^
      --title "X1/P1 打印机堵塞排查" ^
      --model "X1|P1" --doc-type fault_code --version 2026-10-26 ^
      --effective 1 ^
      --source-url https://wiki.bambulab.com/... ^
      --license "可转载·禁止商用" ^
      --notes "含视频 4 个"
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

COLUMNS = [
    "file", "title", "model_no", "doc_type",
    "version", "effective", "source_url", "license", "pages", "notes",
]
DOC_TYPES = {"manual", "fault_code", "process", "standard", "policy", "other"}


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="corpus.csv")
    ap.add_argument("--root", default=".")
    ap.add_argument("--file", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--model", required=True, help="多个型号用 | 分隔，例如 X1|P1")
    ap.add_argument("--doc-type", required=True, choices=sorted(DOC_TYPES))
    ap.add_argument("--version", required=True)
    ap.add_argument("--effective", default="1", choices=["0", "1"])
    ap.add_argument("--source-url", required=True)
    ap.add_argument("--license", required=True)
    ap.add_argument("--pages", default="")
    ap.add_argument("--notes", default="")
    ap.add_argument("--force", action="store_true", help="允许重复 file")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    path = (root / args.csv).resolve()
    if not path.is_file():
        print(f"[ERROR] 找不到 {path}")
        return 2

    rel = args.file.replace("\\", "/")
    if not (root / rel).is_file():
        print(f"[ERROR] 文件不存在：{rel}")
        return 2

    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))

    if not args.force and any((r.get("file") or "") == rel for r in rows):
        print(f"[ERROR] 已存在：{rel}（加 --force 可重复）")
        return 1

    with path.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS, quoting=csv.QUOTE_MINIMAL)
        writer.writerow({
            "file": rel,
            "title": args.title,
            "model_no": args.model,
            "doc_type": args.doc_type,
            "version": args.version,
            "effective": args.effective,
            "source_url": args.source_url,
            "license": args.license,
            "pages": args.pages,
            "notes": args.notes,
        })

    print(f"[OK] 已追加：{rel}")
    print("下一步：python scripts/validate_corpus.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
