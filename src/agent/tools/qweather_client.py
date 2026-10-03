"""和风天气（QWeather）客户端：城市查询 + 实时天气。"""
from __future__ import annotations

import os
from typing import Any

import httpx

# 确保应用启动路径已加载 .env（不在此处再次 load，以免测试 monkeypatch 被覆盖）
try:
    import utils.config_handler  # noqa: F401
except Exception:
    pass


def _api_key() -> str:
    return (os.getenv("QWEATHER_API_KEY") or os.getenv("HEWEATHER_API_KEY") or "").strip()


def _api_host() -> str:
    raw = (os.getenv("QWEATHER_API_HOST") or os.getenv("HEWEATHER_API_HOST") or "").strip()
    raw = raw.removeprefix("https://").removeprefix("http://").strip().strip("/")
    return raw


def _headers(key: str) -> dict[str, str]:
    return {"X-QW-Api-Key": key, "Accept-Encoding": "gzip"}


def _get_json(url: str, *, key: str, params: dict[str, Any], timeout: float = 15.0) -> dict[str, Any]:
    with httpx.Client(timeout=timeout) as client:
        # 同时带 header 与 query key，兼容新旧凭据
        q = dict(params)
        q.setdefault("key", key)
        resp = client.get(url, params=q, headers=_headers(key))
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, dict):
            raise RuntimeError("天气接口返回非 JSON 对象")
        return data


def lookup_city(city: str, *, key: str, host: str) -> dict[str, str] | None:
    """返回首个匹配城市：name/id/adm1/adm2；无结果则 None。"""
    url = f"https://{host}/geo/v2/city/lookup"
    data = _get_json(url, key=key, params={"location": city, "range": "cn", "number": 1, "lang": "zh"})
    code = str(data.get("code", ""))
    if code == "204":
        return None
    if code and code != "200":
        raise RuntimeError(f"城市查询失败 code={code}")
    locs = data.get("location") or []
    if not locs:
        return None
    loc = locs[0]
    return {
        "name": str(loc.get("name") or city),
        "id": str(loc.get("id") or ""),
        "adm1": str(loc.get("adm1") or ""),
        "adm2": str(loc.get("adm2") or ""),
        "lat": str(loc.get("lat") or ""),
        "lon": str(loc.get("lon") or ""),
    }


def weather_now(location_id: str, *, key: str, host: str) -> dict[str, Any]:
    url = f"https://{host}/v7/weather/now"
    data = _get_json(url, key=key, params={"location": location_id, "lang": "zh"})
    code = str(data.get("code", ""))
    if code and code != "200":
        raise RuntimeError(f"实时天气失败 code={code}")
    now = data.get("now")
    if not isinstance(now, dict):
        raise RuntimeError("实时天气无 now 字段")
    return now


def format_now(city_info: dict[str, str], now: dict[str, Any]) -> str:
    region = " / ".join(x for x in (city_info.get("adm1"), city_info.get("adm2"), city_info.get("name")) if x)
    return (
        f"{region} 实时天气：{now.get('text', '?')}，"
        f"气温 {now.get('temp', '?')}℃（体感 {now.get('feelsLike', '?')}℃），"
        f"湿度 {now.get('humidity', '?')}%，"
        f"{now.get('windDir', '')}{now.get('windScale', '')}级，"
        f"能见度 {now.get('vis', '?')} km，"
        f"观测时间 {now.get('obsTime', '?')}。"
        f"数据来源：和风天气。"
    )


def query_city_weather(city: str) -> str:
    """
    查询城市实时天气。
    成功返回可读中文；配置缺失或请求失败返回以「不知道」开头的说明（由调用方 wrap）。
    """
    city = (city or "").strip()
    if not city:
        return "不知道：未提供城市名。"

    key = _api_key()
    host = _api_host()
    if not key:
        return (
            f"不知道：「{city}」的真实天气。"
            "未配置 QWEATHER_API_KEY（和风天气），请在 .env 中设置后重试。"
        )
    if not host:
        return (
            f"不知道：「{city}」的真实天气。"
            "已检测到 QWEATHER_API_KEY，但缺少 QWEATHER_API_HOST。"
            "请打开和风控制台 → 设置，复制 API Host（形如 xxx.qweatherapi.com）写入 .env。"
        )

    try:
        info = lookup_city(city, key=key, host=host)
        if not info or not info.get("id"):
            return f"不知道：未找到城市「{city}」。请换用更完整的地名（如「上海」或「海淀」）。"
        now = weather_now(info["id"], key=key, host=host)
        return format_now(info, now)
    except httpx.HTTPStatusError as e:
        status = e.response.status_code if e.response is not None else "?"
        body = ""
        try:
            body = (e.response.text or "")[:200]
        except Exception:
            pass
        return f"不知道：和风天气 HTTP {status}。{body}".strip()
    except Exception as e:
        return f"不知道：和风天气查询失败（{e}）"
