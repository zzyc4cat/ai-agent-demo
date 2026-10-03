#!/usr/bin/env python3
"""本地一键启动前置：venv / 依赖 / 目录 / .env 检查（仅本机自用，不做陌生人开箱保证）。"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
VENV_DIR = ROOT / ".venv"
REQ = ROOT / "requirements.txt"
ENV_FILE = ROOT / ".env"
ENV_EXAMPLE = ROOT / ".env.example"

# 保证可 import utils / agent
for _p in (str(SRC), str(ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def _venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def _venv_streamlit() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "streamlit.exe"
    return VENV_DIR / "bin" / "streamlit"


def ensure_venv() -> Path:
    py = _venv_python()
    if py.is_file():
        print(f"[bootstrap] venv OK: {py}")
        return py
    print("[bootstrap] 创建虚拟环境 .venv …")
    subprocess.check_call([sys.executable, "-m", "venv", str(VENV_DIR)], cwd=str(ROOT))
    if not py.is_file():
        raise SystemExit("[bootstrap] 创建 venv 失败")
    return py


def ensure_deps(py: Path, *, force: bool = False) -> None:
    marker = VENV_DIR / ".deps_installed"
    if marker.is_file() and not force:
        print("[bootstrap] 依赖已安装（删除 .venv/.deps_installed 可强制重装）")
        return
    print("[bootstrap] 安装 requirements.txt …")
    subprocess.check_call([str(py), "-m", "pip", "install", "-U", "pip"], cwd=str(ROOT))
    subprocess.check_call([str(py), "-m", "pip", "install", "-r", str(REQ)], cwd=str(ROOT))
    marker.write_text("ok\n", encoding="utf-8")
    print("[bootstrap] 依赖安装完成")


def ensure_dirs() -> None:
    for rel in ("storage", "logs", "chroma_db", "workspace", "data/personal"):
        (ROOT / rel).mkdir(parents=True, exist_ok=True)
    print("[bootstrap] 运行时目录就绪")


def ensure_env() -> bool:
    """返回 True 表示关键 Key 看起来可用。"""
    if not ENV_FILE.is_file():
        if ENV_EXAMPLE.is_file():
            ENV_FILE.write_text(ENV_EXAMPLE.read_text(encoding="utf-8"), encoding="utf-8")
            print("[bootstrap] 已从 .env.example 复制 .env，请填入 DASHSCOPE_API_KEY")
        else:
            print("[bootstrap] 警告：无 .env / .env.example")
            return False
    text = ENV_FILE.read_text(encoding="utf-8", errors="ignore")
    key = ""
    for line in text.splitlines():
        if line.strip().startswith("DASHSCOPE_API_KEY="):
            key = line.split("=", 1)[1].strip().strip('"').strip("'")
            break
    if not key or key.startswith("your_") or key == "sk-xxx":
        print("[bootstrap] 警告：DASHSCOPE_API_KEY 未配置或仍为占位符，对话可能无法初始化")
        return False
    print("[bootstrap] DASHSCOPE_API_KEY 已检测到")
    return True


def check_python_version() -> None:
    if sys.version_info < (3, 10):
        raise SystemExit(f"[bootstrap] 需要 Python>=3.10，当前 {sys.version}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="本地启动前置检查")
    parser.add_argument("--force-deps", action="store_true", help="强制重装依赖")
    parser.add_argument("--check-only", action="store_true", help="只检查不装依赖")
    args = parser.parse_args(argv)

    os.chdir(ROOT)
    check_python_version()
    ensure_dirs()
    ensure_env()
    if args.check_only:
        py = _venv_python()
        ok = py.is_file()
        print("[bootstrap] check-only:", "venv存在" if ok else "venv缺失")
        return 0 if ok else 1
    py = ensure_venv()
    ensure_deps(py, force=args.force_deps)
    st = _venv_streamlit()
    if not st.is_file():
        print("[bootstrap] 警告：未找到 streamlit 可执行文件，请检查依赖安装")
        return 1
    print("[bootstrap] 就绪。可用 start.bat / start.ps1 启动 UI")
    print(f"[bootstrap] streamlit: {st}")
    try:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        if str(SRC) not in sys.path:
            sys.path.insert(0, str(SRC))
        from utils.logger_handler import log_event

        log_event("bootstrap.ok", streamlit=str(st), venv=str(py))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
