"""
路径工具：所有相对路径都解析到「仓库根」（含 config/ 与 README.md 的目录）。

本模块被几乎所有 src 包引用。代码在 src/utils/ 下时，根目录是上溯两级；
若从其它位置导入，则向上最多 8 层查找。
"""
from __future__ import annotations

import os
from pathlib import Path


def get_project_root() -> str:
    """返回仓库根的绝对路径。找不到标记目录时回退为 src 的上一级。"""
    p = Path(__file__).resolve().parent
    for _ in range(8):
        if (p / "config").is_dir() and (p / "README.md").is_file():
            return str(p)
        if p.parent == p:
            break
        p = p.parent
    # src/utils/path_tool.py → parents[2] = 仓库根
    return str(Path(__file__).resolve().parents[2])


def get_abs_path(relative_path: str) -> str:
    """把相对仓库根的路径拼成绝对路径（如 config/models.yml、storage/app.db）。"""
    return os.path.join(get_project_root(), relative_path)


def ensure_src_on_path() -> str:
    """把仓库根与 src/ 插入 sys.path，便于脚本不以 PYTHONPATH 启动时仍能 import。"""
    import sys

    root = Path(get_project_root())
    src = root / "src"
    s = str(src)
    if s not in sys.path:
        sys.path.insert(0, s)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return s
