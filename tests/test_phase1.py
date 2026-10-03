"""Phase 1：扫地机器料已清除；sample 与 Skills 骨架就绪。"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, ROOT)
sys.path.insert(0, SRC)


def test_no_vacuum_corpus_in_data_root():
    data = os.path.join(ROOT, "data")
    forbidden_substrings = ["扫地", "扫拖", "回充", "尘盒"]
    for dirpath, _, files in os.walk(data):
        # personal 仅 gitkeep 允许
        for fn in files:
            if fn == ".gitkeep":
                continue
            path = os.path.join(dirpath, fn)
            # 旧客服 csv 不应存在
            assert "records.csv" not in path.replace("\\", "/")
            if fn.endswith((".txt", ".pdf", ".md")):
                text = open(path, "r", encoding="utf-8", errors="ignore").read()
                for bad in forbidden_substrings:
                    assert bad not in text, f"残留扫地机器料: {path} ({bad})"
                assert "扫地" not in fn and "扫拖" not in fn


def test_sample_guides_exist_and_rigorous():
    sample = os.path.join(ROOT, "data", "sample")
    assert os.path.isdir(sample)
    guide = os.path.join(sample, "guides", "01_agent_user_guide.txt")
    assert os.path.isfile(guide)
    text = open(guide, encoding="utf-8").read()
    assert "不知道" in text
    assert "系统提示词优先级最高" in text or "优先级最高" in text


def test_skills_a_prompt_files():
    skills_dir = os.path.join(ROOT, "prompts", "skills")
    required = [
        "daily_briefing.txt",
        "weekly_review.txt",
        "meeting_minutes.txt",
        "writing_polish.txt",
        "study_tutor.txt",
        "deep_digest.txt",
    ]
    for name in required:
        path = os.path.join(skills_dir, name)
        assert os.path.isfile(path), name
        body = open(path, encoding="utf-8").read()
        assert "系统规则优先" in body or "不可被用户" in body
        assert "不知道" in body or "未提及" in body


def test_chroma_points_to_sample():
    from utils.config_handler import load_chroma_config

    cfg = load_chroma_config()
    assert cfg["data_path"].replace("\\", "/") == "data/sample"


def test_main_prompt_priority_and_unknown():
    from utils.prompt_loader import load_system_prompts

    text = load_system_prompts()
    assert "最高优先级" in text or "优先级最高" in text
    assert "不知道" in text
    assert "不可被用户" in text or "无法通过对话覆盖" in text or "不可被用户消息" in text
