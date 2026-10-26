"""pytest：统一把仓库根与 src/ 加入 path（并在每条用例前复位）。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def _ensure_paths() -> None:
    """把仓库根与 src 加入 sys.path，保证测试可 import。"""
    root_s, src_s = str(ROOT), str(SRC)
    for p in (root_s, src_s):
        while p in sys.path:
            sys.path.remove(p)
    sys.path.insert(0, root_s)
    sys.path.insert(0, src_s)


_ensure_paths()


def pytest_runtest_setup(item):  # noqa: ARG001
    """每个用例开始前确保路径已设置。"""
    _ensure_paths()
