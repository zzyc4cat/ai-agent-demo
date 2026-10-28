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
    """SSRF 检查应拦截本机与云元数据地址。"""
    from agent.tools.ssrf_guard import unsafe_url_reason

    assert unsafe_url_reason("http://127.0.0.1/secret")
    assert unsafe_url_reason("http://localhost/x")
    assert unsafe_url_reason("http://169.254.169.254/latest/meta-data/")
    assert unsafe_url_reason("ftp://example.com") is not None
    # 公网主机名：仅检查解析结果；example.com 解析到公网则通过
    reason = unsafe_url_reason("https://example.com/")
    assert reason is None or "无法解析" in reason


def test_fetch_webpage_blocks_ssrf():
    """fetch_webpage 对危险 URL 应拒抓。"""
    from agent.tools.agent_tools import fetch_webpage

    out = fetch_webpage.invoke({"url": "http://127.0.0.1:8080/admin"})
    assert "不知道" in out
    assert "禁止" in out or "内网" in out or "环回" in out or "本机" in out


def test_api_auth_flow():
    """受保护接口需登录 token；普通用户不得访问管理接口。"""
    import uuid

    from fastapi.testclient import TestClient

    import api_server
    from services.storage import get_conn

    client = TestClient(api_server.app)
    assert client.get("/health").status_code == 200

    # 未登录：用户侧接口一律 401
    assert client.post("/kb/ask", json={"question": "hi"}).status_code == 401
    assert client.get("/kb/conversations").status_code == 401

    # 注册即登录
    name = "t_api_" + uuid.uuid4().hex[:8]
    r = client.post("/auth/register", json={"username": name, "password": "apipass12345"})
    assert r.status_code == 200
    token = r.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/auth/me", headers=headers).json()["username"] == name

    # 普通用户不能碰管理接口
    assert client.get("/admin/docs", headers=headers).status_code == 403

    # 退出后 token 立即失效
    assert client.post("/auth/logout", headers=headers).status_code == 200
    assert client.get("/auth/me", headers=headers).status_code == 401

    # 清理测试账号
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM auth_sessions WHERE user_id = (SELECT id FROM users WHERE username = ?)",
            (name,),
        )
        conn.execute("DELETE FROM users WHERE username = ?", (name,))


def test_personal_corpus_path_isolated():
    """个人语料路径必须按 user_id 分子目录。"""
    from rag.utils_rag import personal_corpus_path

    p1 = personal_corpus_path(1)
    p2 = personal_corpus_path(2)
    assert p1 != p2
    assert p1.endswith("/1") or p1.endswith("\\1") or p1.endswith("1")
    assert "2" in p2


def test_skill_whitelist_matches_files():
    """白名单与 prompts/skills 文件一致。"""
    from pathlib import Path
    from agent.tools.middleware import SKILL_WHITELIST

    skills_dir = Path(ROOT) / "prompts" / "skills"
    for name in SKILL_WHITELIST:
        if name == "default":
            continue
        assert (skills_dir / f"{name}.txt").is_file(), name


def test_calculator_rejects_huge_pow():
    """计算器应拒绝过深幂运算。"""
    from agent.tools.tools_b import calculator

    out = calculator.invoke({"expression": "9**9**9**9"})
    assert "不知道" in out
