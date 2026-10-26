"""
双通道日志：

1. logs/agent.log — TimedRotatingFileHandler，带 request_id/user/session/thread/model
2. 根目录 DEBUG_LOG.md — 人读阶段记录，超体积裁剪「运行时记录」区

log_event() 是业务埋点入口；敏感字段名会走 redact_mapping。
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
    """把请求/用户/会话/线程/模型写入日志 ContextVar。"""
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
    """清空日志上下文为占位符。"""
    _request_id.set("-")
    _user_id.set("-")
    _session_id.set("-")
    _thread_id.set("-")
    _model_id.set("-")


def _load_logging_config() -> dict[str, Any]:
    """读 logging.yml 并叠加环境变量覆盖。"""
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
                loaded = yaml.load(f, Loader=yaml.SafeLoader) or {}
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
        """在文本日志行中注入请求上下文。"""
        record.request_id = _request_id.get()
        record.user_id = _user_id.get()
        record.session_id = _session_id.get()
        record.thread_id = _thread_id.get()
        record.model_id = _model_id.get()
        return super().format(record)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        """把日志格式化为含上下文的 JSON。"""
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
    """配置控制台与按日轮转的文件日志。"""
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


def _truncate(value: Any, limit: int = 200) -> Any:
    """把过长字段截断以免日志膨胀。"""
    text = str(value)
    if len(text) <= limit:
        return value if not isinstance(value, str) else text
    return text[:limit] + f"...(+{len(text) - limit})"


_SECRET_KEYS = re.compile(r"(password|secret|api[_-]?key|token|authorization)", re.I)


def redact_mapping(data: dict[str, Any] | None) -> dict[str, Any]:
    """把密钥类字段名替换为 ***。"""
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
    """是否允许把 Prompt 正文写入日志。"""
    return bool(_load_logging_config().get("log_prompt"))


# —— DEBUG_LOG.md：人读阶段日志 + 体积清理 ——
_RUNTIME_ANCHOR = "## 运行时记录（自动追加）"
_RUNTIME_MARKER = "<!-- RUNTIME_LOG_START -->"
_debug_log_lock = __import__("threading").Lock()


def _debug_log_path() -> str:
    """返回根目录 DEBUG_LOG.md 路径。"""
    return get_abs_path("DEBUG_LOG.md")


def append_debug_log(stage: str, **fields: Any) -> None:
    """向 DEBUG_LOG.md 追加一条阶段记录；超限则裁剪运行时区。"""
    cfg = _load_logging_config()
    if not bool(cfg.get("debug_log_enabled", True)):
        return
    from datetime import datetime

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    safe = {k: _truncate(v, 180) for k, v in fields.items()}
    safe = redact_mapping({str(k): v for k, v in safe.items()})
    line_fields = " ".join(f"{k}={v}" for k, v in safe.items())
    block = (
        f"\n### [{ts}] stage={stage} "
        f"req={_request_id.get()} user={_user_id.get()} model={_model_id.get()}\n"
        f"- {line_fields}\n"
    )
    path = _debug_log_path()
    with _debug_log_lock:
        try:
            if not os.path.isfile(path):
                with open(path, "w", encoding="utf-8") as f:
                    f.write(
                        "# DEBUG_LOG\n\n"
                        f"{_RUNTIME_ANCHOR}\n\n{_RUNTIME_MARKER}\n"
                    )
            with open(path, "a", encoding="utf-8") as f:
                f.write(block)
            _maybe_trim_debug_log(path, cfg)
        except Exception:
            pass


def _maybe_trim_debug_log(path: str, cfg: dict[str, Any]) -> None:
    """超体积时只裁剪运行时记录区。"""
    max_chars = int(cfg.get("debug_log_max_chars", 400000))
    keep_chars = int(cfg.get("debug_log_keep_chars", 240000))
    try:
        text = open(path, encoding="utf-8").read()
    except Exception:
        return
    if len(text) <= max_chars:
        return
    idx_marker = text.find(_RUNTIME_MARKER)
    if idx_marker >= 0:
        marker_end = idx_marker + len(_RUNTIME_MARKER)
        head = text[:marker_end]
        runtime = text[marker_end:]
    else:
        idx = text.find(_RUNTIME_ANCHOR)
        if idx < 0:
            open(path, "w", encoding="utf-8").write(
                "# DEBUG_LOG（已自动清理，无锚点故截断尾部）\n\n" + text[-keep_chars:]
            )
            return
        marker_end = idx + len(_RUNTIME_ANCHOR)
        head = text[:marker_end] + f"\n\n{_RUNTIME_MARKER}"
        runtime = text[marker_end:]
    if len(runtime) > keep_chars:
        runtime = "\n\n> （系统自动清理：仅保留最近运行记录）\n" + runtime[-keep_chars:]
    open(path, "w", encoding="utf-8").write(head + runtime)


def log_event(event: str, level: int = logging.INFO, **fields: Any) -> None:
    """统一事件日志；阶段事件同步写入 DEBUG_LOG.md。"""
    safe = {k: _truncate(v) for k, v in fields.items()}
    logger.log(level, "event=%s %s", event, safe)
    if event.startswith(
        (
            "chat.",
            "rag.",
            "model.",
            "tool.",
            "guard.",
            "user.",
            "kb.",
            "app.",
            "bootstrap.",
            "checkpointer",
            "eval.",
        )
    ):
        append_debug_log(event, **fields)
