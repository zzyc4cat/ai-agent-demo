# -*- coding: utf-8 -*-
"""启动脚本存在性。"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_start_scripts_exist() -> None:
    """后端与隧道启动脚本必须存在。"""
    assert (ROOT / "start-api.ps1").is_file()
    assert (ROOT / "start-tunnel.ps1").is_file()
