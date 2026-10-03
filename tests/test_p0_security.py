"""P0 安全与正确性：API 鉴权、SSRF、个人语料路径、技能白名单。"""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, ROOT)
sys.path.insert(0, SRC)


def test_ssrf_blocks_localhost_and_metadata():
    from agent.tools.ssrf_guard import unsafe_url_reason

    assert unsafe_url_reason("http://127.0.0.1/secret")
    assert unsafe_url_reason("http://localhost/x")
    assert unsafe_url_reason("http://169.254.169.254/latest/meta-data/")
    assert unsafe_url_reason("ftp://example.com") is not None
    # 公网主机名：仅检查解析结果；example.com 解析到公网则通过
    reason = unsafe_url_reason("https://example.com/")
    assert reason is None or "无法解析" in reason


def test_fetch_webpage_blocks_ssrf():
    from agent.tools.agent_tools import fetch_webpage

    out = fetch_webpage.invoke({"url": "http://127.0.0.1:8080/admin"})
    assert "不知道" in out
    assert "禁止" in out or "内网" in out or "环回" in out or "本机" in out


def test_api_requires_key(monkeypatch):
    from fastapi.testclient import TestClient
    import api_server

    monkeypatch.delenv("AGENT_API_KEY", raising=False)
    client = TestClient(api_server.app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("api_key_configured") is False

    denied = client.post("/chat", json={"message": "hi", "username": "alice"})
    assert denied.status_code == 503

    monkeypatch.setenv("AGENT_API_KEY", "test-secret-key-p0")
    # 无密钥
    r2 = client.post("/chat", json={"message": "hi", "username": "alice"})
    assert r2.status_code == 401
    # 错误密钥
    r3 = client.post(
        "/chat",
        json={"message": "hi", "username": "alice"},
        headers={"X-API-Key": "wrong"},
    )
    assert r3.status_code == 401
    # 非法 skill
    r4 = client.post(
        "/chat",
        json={"message": "hi", "skill": "hack_system"},
        headers={"Authorization": "Bearer test-secret-key-p0"},
    )
    assert r4.status_code == 400


def test_personal_corpus_path_isolated():
    from rag.utils_rag import personal_corpus_path

    p1 = personal_corpus_path(1)
    p2 = personal_corpus_path(2)
    assert p1 != p2
    assert p1.endswith("/1") or p1.endswith("\\1") or p1.endswith("1")
    assert "2" in p2


def test_skill_whitelist_matches_files():
    from pathlib import Path
    from agent.tools.middleware import SKILL_WHITELIST

    skills_dir = Path(ROOT) / "prompts" / "skills"
    for name in SKILL_WHITELIST:
        if name == "default":
            continue
        assert (skills_dir / f"{name}.txt").is_file(), name


def test_calculator_rejects_huge_pow():
    from agent.tools.tools_b import calculator

    out = calculator.invoke({"expression": "9**9**9**9"})
    assert "不知道" in out
