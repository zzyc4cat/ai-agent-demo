# -*- coding: utf-8 -*-
"""P0 安全与正确性：登录鉴权、个人语料路径隔离。"""
from __future__ import annotations

import os
import sys
import uuid

from fastapi.testclient import TestClient

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, ROOT)
sys.path.insert(0, SRC)


def test_api_auth_flow():
    """受保护接口需登录 token；普通用户不得访问管理接口。"""
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
