# -*- coding: utf-8 -*-
"""本地备份：SQLite（在线备份）+ 租户语料 + corpus.csv，可选向量库。

用法：
    python scripts/backup.py
    python scripts/backup.py --with-vectors --keep 14
"""
from __future__ import annotations

import argparse
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]


def backup_sqlite(src: Path, dst: Path) -> None:
    """用 sqlite3 backup API 拷贝，运行中也安全。"""
    con = sqlite3.connect(str(src))
    out = sqlite3.connect(str(dst))
    try:
        with out:
            con.backup(out)
    finally:
        con.close()
        out.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "backups"))
    ap.add_argument("--keep", type=int, default=7, help="保留最近几份")
    ap.add_argument("--with-vectors", action="store_true", help="同时备份 chroma_db（较大）")
    args = ap.parse_args()

    out_root = Path(args.out)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = out_root / stamp
    target.mkdir(parents=True, exist_ok=True)

    db = ROOT / "storage" / "app.db"
    if db.is_file():
        backup_sqlite(db, target / "app.db")
        print(f"[db] {db} -> {target / 'app.db'}")

    tenants = ROOT / "data" / "tenants"
    if tenants.is_dir():
        shutil.copytree(tenants, target / "tenants")
        print(f"[data] {tenants} -> {target / 'tenants'}")

    corpus = ROOT / "corpus.csv"
    if corpus.is_file():
        shutil.copy2(corpus, target / "corpus.csv")

    if args.with_vectors:
        chroma = ROOT / "chroma_db"
        if chroma.is_dir():
            shutil.copytree(chroma, target / "chroma_db")
            print(f"[vectors] {chroma} -> {target / 'chroma_db'}")

    keep = max(args.keep, 1)
    backups = sorted([p for p in out_root.iterdir() if p.is_dir()], reverse=True)
    for old in backups[keep:]:
        shutil.rmtree(old)
        print(f"[prune] {old}")

    total = sum(f.stat().st_size for f in target.rglob("*") if f.is_file())
    print(f"[ok] {target} ({total / 1024 / 1024:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
