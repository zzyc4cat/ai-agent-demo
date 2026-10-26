"""
出站 URL 安全检查，供 fetch_webpage 调用。

拦截非 http(s)、本机名、环回、私网、链路本地、组播、保留地址及云 metadata。
解析 DNS 后检查所有 A/AAAA；调用方可配合「不跟随危险 Location」使用。
"""
from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

_BLOCKED_HOSTNAMES = frozenset(
    {
        "localhost",
        "localhost.localdomain",
        "metadata",
        "metadata.google.internal",
        "metadata.goog",
    }
)


def unsafe_url_reason(url: str) -> str | None:
    """若 URL 不安全则返回原因，否则返回 None。"""
    u = (url or "").strip()
    if not u.startswith(("http://", "https://")):
        return "URL 必须以 http/https 开头"
    parsed = urlparse(u)
    host = (parsed.hostname or "").strip().lower()
    if not host:
        return "无效主机名"
    if host in _BLOCKED_HOSTNAMES or host.endswith(".localhost"):
        return "禁止访问本机或元数据主机"
    if host.startswith("127.") or host == "::1" or host == "0.0.0.0":
        return "禁止访问环回地址"

    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return "无法解析主机名"

    if not infos:
        return "无法解析主机名"

    for info in infos:
        addr = info[4][0]
        try:
            ip = ipaddress.ip_address(addr)
        except ValueError:
            continue
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            return f"禁止访问内网/保留地址（{ip}）"
        if str(ip) == "169.254.169.254":
            return "禁止访问云元数据地址"
    return None
