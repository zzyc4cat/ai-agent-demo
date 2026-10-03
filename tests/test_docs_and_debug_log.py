"""DEBUG_LOG 追加与裁剪。"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, ROOT)
sys.path.insert(0, SRC)


def test_append_debug_log_writes(tmp_path, monkeypatch):
    import utils.logger_handler as lh

    path = tmp_path / "DEBUG_LOG.md"
    path.write_text(
        "# DEBUG_LOG\n\n## 运行时记录（自动追加）\n\n<!-- RUNTIME_LOG_START -->\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(lh, "_debug_log_path", lambda: str(path))
    monkeypatch.setattr(
        lh,
        "_load_logging_config",
        lambda: {
            "debug_log_enabled": True,
            "debug_log_max_chars": 500,
            "debug_log_keep_chars": 200,
        },
    )
    lh.append_debug_log("unit.test", foo="bar")
    text = path.read_text(encoding="utf-8")
    assert "stage=unit.test" in text
    assert "foo=bar" in text


def test_trim_debug_log_keeps_anchor(tmp_path, monkeypatch):
    import utils.logger_handler as lh

    path = tmp_path / "DEBUG_LOG.md"
    runtime = "x" * 1000
    path.write_text(
        "# H\n\n## 运行时记录（自动追加）\n\n<!-- RUNTIME_LOG_START -->\n" + runtime,
        encoding="utf-8",
    )
    monkeypatch.setattr(lh, "_debug_log_path", lambda: str(path))
    cfg = {"debug_log_max_chars": 100, "debug_log_keep_chars": 50}
    lh._maybe_trim_debug_log(str(path), cfg)
    text = path.read_text(encoding="utf-8")
    assert "<!-- RUNTIME_LOG_START -->" in text
    assert "系统自动清理" in text
    assert len(text) < 1000


def test_root_docs_only_three_guides():
    root_mds = {
        f
        for f in os.listdir(ROOT)
        if f.lower().endswith(".md") and os.path.isfile(os.path.join(ROOT, f))
    }
    assert "README.md" in root_mds
    assert "DEBUG.md" in root_mds
    assert "DEBUG_LOG.md" in root_mds
    # 旧日志类文档应已移除
    for old in (
        "UPGRADE_LOG.md",
        "UPGRADE_ROADMAP.md",
        "RAG_TEST_LOG.md",
        "PHASE_UPGRADE_TEST_LOG.md",
        "Study.md",
    ):
        assert old not in root_mds
