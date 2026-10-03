"""API /health 冒烟（不启动长驻服务：用 TestClient）。"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, ROOT)
sys.path.insert(0, SRC)


def test_health_three_rounds():
    from fastapi.testclient import TestClient
    import api_server

    client = TestClient(api_server.app)
    for i in range(3):
        r = client.get("/health")
        assert r.status_code == 200, f"round {i+1}"
        assert r.json().get("status") == "ok"
