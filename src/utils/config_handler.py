"""
配置加载：YAML + 可选 dotenv
"""
from __future__ import annotations

import os
from typing import Any

import yaml
from utils.path_tool import get_abs_path

try:
    from dotenv import load_dotenv

    load_dotenv(get_abs_path(".env"))
except ImportError:
    pass


def _load_yaml(config_path: str, encoding: str = "utf-8") -> dict[str, Any]:
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.SafeLoader) or {}


def load_rag_config(config_path: str = get_abs_path("config/rag.yml")) -> dict[str, Any]:
    return _load_yaml(config_path)


def load_chroma_config(config_path: str = get_abs_path("config/chroma.yml")) -> dict[str, Any]:
    return _load_yaml(config_path)


def load_prompts_config(config_path: str = get_abs_path("config/prompts.yml")) -> dict[str, Any]:
    return _load_yaml(config_path)


def load_agent_config(config_path: str = get_abs_path("config/agent.yml")) -> dict[str, Any]:
    return _load_yaml(config_path)


def load_models_config(config_path: str = get_abs_path("config/models.yml")) -> dict[str, Any]:
    return _load_yaml(config_path)


def load_logging_config(config_path: str = get_abs_path("config/logging.yml")) -> dict[str, Any]:
    return _load_yaml(config_path)


def load_prompt_guard_config(config_path: str = get_abs_path("config/prompt_guard.yml")) -> dict[str, Any]:
    return _load_yaml(config_path)


def load_rag_runtime_config(config_path: str = get_abs_path("config/rag_runtime.yml")) -> dict[str, Any]:
    try:
        return _load_yaml(config_path)
    except FileNotFoundError:
        return {}


rag_config = load_rag_config()
chroma_config = load_chroma_config()
prompts_config = load_prompts_config()
agent_config = load_agent_config()
models_config = load_models_config()
prompt_guard_config = load_prompt_guard_config()
rag_runtime_config = load_rag_runtime_config()
