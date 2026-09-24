"""
日志工具：轮转文件 + contextvars 关联字段 + 统一事件名
"""
from __future__ import annotations

import json
import logging
import os
import re
from contextvars import ContextVar
from logging.handlers import TimedRotatingFileHandler
from typing import Any

from utils.path_tool import get_abs_path

LOG_ROOT = get_abs_path("logs")
os.makedirs(LOG_ROOT, exist_ok=True)

_request_id: ContextVar[str] = ContextVar("request_id", default="-")
_user_id: ContextVar[str] = ContextVar("user_id", default="-")
_session_id: ContextVar[str] = ContextVar("session_id", default="-")
_thread_id: ContextVar[str] = ContextVar("thread_id", default="-")
_model_id: ContextVar[str] = ContextVar("model_id", default="-")


def bind_log_context(
    *,
    request_id: str | None = None,
    user_id: str | None = None,
    session_id: str | None = None,
    thread_id: str | None = None,
    model_id: str | None = None,
) -> None:
    if request_id is not None:
        _request_id.set(request_id)
    if user_id is not None:
        _user_id.set(user_id)
    if session_id is not None:
        _session_id.set(session_id)
    if thread_id is not None:
        _thread_id.set(thread_id)
    if model_id is not None:
        _model_id.set(model_id)


def clear_log_context() -> None:
    _request_id.set("-")
    _user_id.set("-")
    _session_id.set("-")
    _thread_id.set("-")
    _model_id.set("-")


def _load_logging_config() -> dict[str, Any]:
    path = get_abs_path("config/logging.yml")
    cfg: dict[str, Any] = {
        "level": "INFO",
        "json": False,
        "log_prompt": False,
        "backup_count": 14,
        "log_filename": "agent.log",
    }
    if os.path.exists(path):
        try:
            import yaml

            with open(path, "r", encoding="utf-8") as f:
                loaded = yaml.load(f, Loader=yaml.FullLoader) or {}
            cfg.update(loaded)
        except Exception:
            pass
    env_level = os.getenv("LOG_LEVEL")
    if env_level:
        cfg["level"] = env_level
    if os.getenv("LOG_JSON", "").strip() in ("1", "true", "True"):
        cfg["json"] = True
    if os.getenv("LOG_PROMPT", "").strip() in ("1", "true", "True"):
        cfg["log_prompt"] = True
    return cfg


class ContextFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        record.request_id = _request_id.get()
        record.user_id = _user_id.get()
        record.session_id = _session_id.get()
        record.thread_id = _thread_id.get()
        record.model_id = _model_id.get()
        return super().format(record)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "name": record.name,
            "msg": record.getMessage(),
            "request_id": _request_id.get(),
            "user_id": _user_id.get(),
            "session_id": _session_id.get(),
            "thread_id": _thread_id.get(),
            "model_id": _model_id.get(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def get_logger(
    name: str = "agent",
    console_level: int | None = None,
    file_level: int = logging.DEBUG,
) -> logging.Logger:
    cfg = _load_logging_config()
    level_name = str(cfg.get("level", "INFO")).upper()
    level = getattr(logging, level_name, logging.INFO)
    if console_level is None:
        console_level = level

    base_logger = logging.getLogger(name)
    base_logger.setLevel(logging.DEBUG)
    base_logger.propagate = False

    if base_logger.handlers:
        return base_logger

    use_json = bool(cfg.get("json"))
    text_fmt = ContextFormatter(
        "%(asctime)s %(levelname)-8s [%(name)s] "
        "req=%(request_id)s user=%(user_id)s session=%(session_id)s "
        "thread=%(thread_id)s model=%(model_id)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    formatter: logging.Formatter = JsonFormatter() if use_json else text_fmt

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    base_logger.addHandler(console_handler)

    log_file = os.path.join(LOG_ROOT, str(cfg.get("log_filename", "agent.log")))
    file_handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=1,
        backupCount=int(cfg.get("backup_count", 14)),
        encoding="utf-8",
    )
    file_handler.setLevel(file_level)
    file_handler.setFormatter(formatter)
    base_logger.addHandler(file_handler)

    return base_logger


logger = get_logger()


def log_event(event: str, level: int = logging.INFO, **fields: Any) -> None:
    """统一事件日志，便于 DEBUG.md 按事件名检索。"""
    safe = {k: _truncate(v) for k, v in fields.items()}
    logger.log(level, "event=%s %s", event, safe)


def _truncate(value: Any, limit: int = 200) -> Any:
    text = str(value)
    if len(text) <= limit:
        return value if not isinstance(value, str) else text
    return text[:limit] + f"...(+{len(text) - limit})"


_SECRET_KEYS = re.compile(r"(password|secret|api[_-]?key|token|authorization)", re.I)


def redact_mapping(data: dict[str, Any] | None) -> dict[str, Any]:
    if not data:
        return {}
    out: dict[str, Any] = {}
    for k, v in data.items():
        if _SECRET_KEYS.search(str(k)):
            out[k] = "***"
        else:
            out[k] = _truncate(v, 120)
    return out


def should_log_prompt() -> bool:
    return bool(_load_logging_config().get("log_prompt"))
