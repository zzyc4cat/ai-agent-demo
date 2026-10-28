# -*- coding: utf-8 -*-
"""创建账号（密码不从命令行参数读，避免进入 shell 历史与仓库）。

用法：
    $env:USER_PASSWORD = "***"; python scripts/create_user.py --username zzy --role admin
    python scripts/create_user.py --username zzy --role admin   # 交互输入密码
"""
from __future__ import annotations

import argparse
import getpass
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

from services.auth_service import create_user  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--username", required=True)
    ap.add_argument("--role", default="user", choices=["user", "admin"])
    ap.add_argument("--tenant", default="demo")
    args = ap.parse_args()

    password = os.getenv("USER_PASSWORD") or ""
    if not password:
        password = getpass.getpass("密码（输入不回显）：")
        if password != getpass.getpass("再输一次："):
            print("[ERROR] 两次输入不一致")
            return 2

    try:
        user = create_user(args.username, password, role=args.role, tenant_id=args.tenant)
    except ValueError as e:
        print(f"[ERROR] {e}")
        return 1
    print(f"[OK] 已创建 {user['username']}（角色 {user['role']}，租户 {user['tenant_id']}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
