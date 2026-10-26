# -*- coding: utf-8 -*-
"""校验 corpus.csv：字段完整、类型合法、文件存在、无重复。

用法：
    python scripts/validate_corpus.py
    python scripts/validate_corpus.py --csv corpus.csv --root .
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
REQUIRED = ["file", "title", "model_no", "doc_type", "version",
            "effective", "source_url", "license"]


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="corpus.csv")
    ap.add_argument("--root", default=".")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    path = (root / args.csv).resolve()
    if not path.is_file():
        print(f"[ERROR] 找不到 {path}")
        return 2

    errors: list[str] = []
    warnings: list[str] = []
    seen: dict[str, int] = {}
    rows = 0

    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != COLUMNS:
            print("[ERROR] 表头不符")
            print(f"  期望: {','.join(COLUMNS)}")
            print(f"  实际: {','.join(reader.fieldnames or [])}")
            return 2

        for line_no, row in enumerate(reader, start=2):
            if not any((v or "").strip() for v in row.values()):
                continue
            rows += 1
            where = f"第 {line_no} 行"

            for key in REQUIRED:
                if not (row.get(key) or "").strip():
                    errors.append(f"{where}: 缺少 {key}")

            doc_type = (row.get("doc_type") or "").strip()
            if doc_type and doc_type not in DOC_TYPES:
                errors.append(f"{where}: doc_type={doc_type} 不在 {sorted(DOC_TYPES)}")

            effective = (row.get("effective") or "").strip()
            if effective and effective not in {"0", "1"}:
                errors.append(f"{where}: effective 只能是 0/1，当前 {effective}")

            pages = (row.get("pages") or "").strip()
            if pages and not pages.isdigit():
                errors.append(f"{where}: pages 必须是整数，当前 {pages}")

            url = (row.get("source_url") or "").strip()
            if url and not url.startswith(("http://", "https://")):
                errors.append(f"{where}: source_url 必须以 http(s):// 开头")

            license_ = (row.get("license") or "").strip()
            if license_ in {"待核对", "unknown", "?"}:
                warnings.append(f"{where}: 许可待核对（{row.get('file')}）")

            rel = (row.get("file") or "").strip()
            if rel:
                if rel in seen:
                    errors.append(f"{where}: 文件重复，首次出现在第 {seen[rel]} 行")
                else:
                    seen[rel] = line_no
                if not (root / rel).is_file():
                    errors.append(f"{where}: 文件不存在 {rel}")

    print(f"检查 {path}")
    print(f"行数: {rows}  错误: {len(errors)}  警告: {len(warnings)}")
    for item in errors:
        print(f"  [ERROR] {item}")
    for item in warnings:
        print(f"  [WARN]  {item}")
    if rows == 0:
        print("  [WARN]  还没有数据行")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
