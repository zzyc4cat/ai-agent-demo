"""Phase0 bootstrap / 启动脚本存在性与幂等。"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_start_scripts_exist():
    assert (ROOT / "start.bat").is_file()
    assert (ROOT / "start.ps1").is_file()
    assert (ROOT / "scripts" / "bootstrap.py").is_file()


def test_bootstrap_check_only_round():
    py = ROOT / ".venv" / "Scripts" / "python.exe"
    if not py.is_file():
        py = Path(sys.executable)
    r = subprocess.run(
        [str(py), str(ROOT / "scripts" / "bootstrap.py"), "--check-only"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert "bootstrap" in (r.stdout + r.stderr).lower() or "venv" in (r.stdout + r.stderr).lower()


def test_bootstrap_idempotent_three_rounds():
    """连续 3 轮 bootstrap（不强制重装依赖）均应成功。"""
    py = ROOT / ".venv" / "Scripts" / "python.exe"
    cmd = [str(py if py.is_file() else sys.executable), str(ROOT / "scripts" / "bootstrap.py")]
    for i in range(3):
        r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace")
        assert r.returncode == 0, f"round {i+1} failed: {r.stdout}\n{r.stderr}"


def test_api_server_importable():
    import api_server

    assert api_server.app.title


def test_dockerfile_exists():
    assert (ROOT / "deploy" / "Dockerfile").is_file()
    assert (ROOT / "deploy" / "docker-compose.yml").is_file()
