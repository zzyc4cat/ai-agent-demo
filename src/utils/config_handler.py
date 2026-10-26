"""
YAML 配置加载器。模块 import 时读取仓库根 `.env`（若安装了 python-dotenv），
并把 config/*.yml 解析为模块级字典，供 ModelRouter、RAG、护栏等使用。

使用 yaml.SafeLoader，避免任意对象反序列化。
"""
from __future__ import annotations

from typing import Any

import yaml
from utils.path_tool import get_abs_path

# 启动即加载密钥到 os.environ；未安装 dotenv 时静默跳过
try:
    from dotenv import load_dotenv

    load_dotenv(get_abs_path(".env"))
except ImportError:
    pass


def _load_yaml(config_path: str, encoding: str = "utf-8") -> dict[str, Any]:
    """读取单个 YAML 文件；空文件视为 {}。"""
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.SafeLoader) or {}


def load_rag_config(config_path: str = get_abs_path("config/rag.yml")) -> dict[str, Any]:
    """旧版 RAG 摘要配置（兼容 ModelRouter 回退字段）。"""
    return _load_yaml(config_path)


def load_chroma_config(config_path: str = get_abs_path("config/chroma.yml")) -> dict[str, Any]:
    """Chroma 持久化目录、sample 语料路径、允许的文件后缀。"""
    return _load_yaml(config_path)


def load_prompts_config(config_path: str = get_abs_path("config/prompts.yml")) -> dict[str, Any]:
    """主 Prompt / RAG 总结 Prompt / skills 目录的相对路径。"""
    return _load_yaml(config_path)


def load_agent_config(config_path: str = get_abs_path("config/agent.yml")) -> dict[str, Any]:
    """Agent 杂项（遗留字段，当前主流程很少读取）。"""
    return _load_yaml(config_path)


def load_models_config(config_path: str = get_abs_path("config/models.yml")) -> dict[str, Any]:
    """聊天/向量模型注册表、Auto 优先级、额度错误关键词。"""
    return _load_yaml(config_path)


def load_logging_config(config_path: str = get_abs_path("config/logging.yml")) -> dict[str, Any]:
    """日志级别、轮转、DEBUG_LOG 裁剪参数。"""
    return _load_yaml(config_path)


def load_prompt_guard_config(config_path: str = get_abs_path("config/prompt_guard.yml")) -> dict[str, Any]:
    """泄露系统提示 / 忽略规则 的正则与回复文案。"""
    return _load_yaml(config_path)


def load_rag_runtime_config(config_path: str = get_abs_path("config/rag_runtime.yml")) -> dict[str, Any]:
    """混合检索 k、弱门控、缓存、collection 名、个人语料根路径。文件缺失则 {}。"""
    try:
        return _load_yaml(config_path)
    except FileNotFoundError:
        return {}


# 进程内单次加载；改 YAML 后需重启进程（护栏 check 会重新 load）
rag_config = load_rag_config()
chroma_config = load_chroma_config()
prompts_config = load_prompts_config()
agent_config = load_agent_config()
models_config = load_models_config()
prompt_guard_config = load_prompt_guard_config()
rag_runtime_config = load_rag_runtime_config()
