"""
为整个工程提供统一的绝对路径（支持代码位于 src/ 下）。
"""
from __future__ import annotations

import os
from pathlib import Path


def get_project_root() -> str:
    """定位含 config/ 与 README.md 的仓库根目录。"""
    p = Path(__file__).resolve().parent
    for _ in range(8):
        if (p / "config").is_dir() and (p / "README.md").is_file():
            return str(p)
        if p.parent == p:
            break
        p = p.parent
    # 回退：src/utils → 上两级为根
    return str(Path(__file__).resolve().parents[2])


def get_abs_path(relative_path: str) -> str:
    """相对仓库根的路径 → 绝对路径。"""
    return os.path.join(get_project_root(), relative_path)


def ensure_src_on_path() -> str:
    """将 src/ 加入 sys.path，返回 src 绝对路径。"""
    import sys

    root = Path(get_project_root())
    src = root / "src"
    s = str(src)
    if s not in sys.path:
        sys.path.insert(0, s)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return s
