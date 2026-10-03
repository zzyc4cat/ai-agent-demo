"""和风天气 get_weather / qweather_client 测试。"""
from __future__ import annotations

import os
import sys
from unittest.mock import patch

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, ROOT)
sys.path.insert(0, SRC)

# 先 import（会 load_dotenv），再在各用例里 monkeypatch，避免 import 把 env 写回
from agent.tools.qweather_client import query_city_weather  # noqa: E402


def test_weather_missing_key(monkeypatch):
    monkeypatch.setenv("QWEATHER_API_KEY", "")
    monkeypatch.setenv("HEWEATHER_API_KEY", "")
    out = query_city_weather("上海")
    assert "不知道" in out
    assert "QWEATHER_API_KEY" in out


def test_weather_key_without_host(monkeypatch):
    monkeypatch.setenv("QWEATHER_API_KEY", "test-key-xxxxxxxx")
    monkeypatch.setenv("QWEATHER_API_HOST", "")
    monkeypatch.setenv("HEWEATHER_API_HOST", "")
    out = query_city_weather("上海")
    assert "不知道" in out
    assert "QWEATHER_API_HOST" in out


def test_weather_empty_city(monkeypatch):
    monkeypatch.setenv("QWEATHER_API_KEY", "k")
    monkeypatch.setenv("QWEATHER_API_HOST", "example.qweatherapi.com")
    assert "未提供城市名" in query_city_weather("  ")


def test_weather_success_mocked(monkeypatch):
    monkeypatch.setenv("QWEATHER_API_KEY", "k")
    monkeypatch.setenv("QWEATHER_API_HOST", "demo.qweatherapi.com")

    geo = {
        "code": "200",
        "location": [
            {"name": "上海", "id": "101020100", "adm1": "上海市", "adm2": "上海", "lat": "31.22", "lon": "121.48"}
        ],
    }
    now = {
        "code": "200",
        "now": {
            "obsTime": "2026-09-24T20:00+08:00",
            "temp": "26",
            "feelsLike": "28",
            "text": "多云",
            "windDir": "东南风",
            "windScale": "2",
            "humidity": "70",
            "vis": "10",
        },
    }

    with patch("agent.tools.qweather_client._get_json", side_effect=[geo, now]):
        out = query_city_weather("上海")
    assert "不知道" not in out
    assert "上海" in out
    assert "26" in out
    assert "多云" in out
    assert "和风天气" in out


def test_get_weather_tool_wraps(monkeypatch):
    monkeypatch.setenv("QWEATHER_API_KEY", "k")
    monkeypatch.setenv("QWEATHER_API_HOST", "demo.qweatherapi.com")
    from agent.tools.agent_tools import get_weather

    with patch(
        "agent.tools.qweather_client.query_city_weather",
        return_value="上海市 / 上海 实时天气：晴，气温 30℃（体感 32℃），湿度 50%，南风2级，能见度 12 km，观测时间 t。数据来源：和风天气。",
    ):
        raw = get_weather.invoke({"city": "上海"})
    assert "UNTRUSTED_DATA" in raw
    assert "30℃" in raw or "30" in raw


def test_live_qweather_if_configured():
    """仅当 .env 同时有 Key 与 Host 时打真实请求；否则 skip。"""
    try:
        from dotenv import load_dotenv
        from utils.path_tool import get_abs_path

        load_dotenv(get_abs_path(".env"), override=True)
    except Exception:
        pass
    key = (os.getenv("QWEATHER_API_KEY") or "").strip()
    host = (os.getenv("QWEATHER_API_HOST") or "").strip()
    if not key or not host:
        import pytest

        pytest.skip("未配置 QWEATHER_API_HOST，跳过真实和风请求")

    out = query_city_weather("上海")
    assert "不知道" not in out, out
    assert "气温" in out or "℃" in out
    assert "和风天气" in out
