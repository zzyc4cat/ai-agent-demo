"""
模型注册与路由（config/models.yml）。

- Auto：按 priority 选第一个「已 enabled 且环境变量 Key 有效」的聊天模型
- 手动：必须指定 id，额度不足由 ReactAgent 提示、不换模
- 额度：错误信息匹配 quota_error_markers 正则
- Embedding：defaults.embedding_model_id 优先
- chat_model / embedding_model：懒代理，兼容旧 import 时立刻连网的写法
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any, Optional

from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel

from utils.config_handler import models_config, rag_config
from utils.logger_handler import bind_log_context, log_event, logger


@dataclass
class ModelSpec:
    """一条可路由模型：id、云厂商、真实 model_name、Auto 优先级、环境变量名。"""
    id: str
    provider: str
    model_name: str
    priority: int = 100
    enabled: bool = True
    api_key_env: str = "DASHSCOPE_API_KEY"
    base_url_env: str = ""
    note: str = ""


@dataclass
class RouterState:
    mode: str = "auto"  # auto | manual
    manual_model_id: str | None = None
    exhausted_ids: set[str] = field(default_factory=set)
    active_model_id: str | None = None


class ModelRouter:
    """按用户偏好选择聊天模型；Auto 模式下额度类错误触发切换。"""

    def __init__(self, config: dict[str, Any] | None = None):
        """解析 models.yml 并编译额度错误正则。"""
        self.config = config or models_config
        self._chat_specs = self._parse_chat_specs()
        self._embedding_specs = self._parse_embedding_specs()
        self._chat_cache: dict[str, BaseChatModel] = {}
        self._embedding_cache: dict[str, Embeddings] = {}
        markers = self.config.get("quota_error_markers") or []
        self._quota_re = re.compile("|".join(f"(?:{m})" for m in markers), re.I) if markers else None

    def _parse_chat_specs(self) -> list[ModelSpec]:
        """把配置中的聊天模型列表转为 ModelSpec。"""
        specs: list[ModelSpec] = []
        for item in self.config.get("chat_models") or []:
            specs.append(
                ModelSpec(
                    id=item["id"],
                    provider=item.get("provider", "dashscope"),
                    model_name=item["model_name"],
                    priority=int(item.get("priority", 100)),
                    enabled=bool(item.get("enabled", True)),
                    api_key_env=item.get("api_key_env", "DASHSCOPE_API_KEY"),
                    base_url_env=item.get("base_url_env", ""),
                    note=item.get("note", ""),
                )
            )
        # 兼容旧 rag.yml
        if not specs and rag_config.get("chat_model_name"):
            specs.append(
                ModelSpec(
                    id="legacy_chat",
                    provider="dashscope",
                    model_name=rag_config["chat_model_name"],
                    priority=10,
                )
            )
        return sorted(specs, key=lambda s: s.priority)

    def _parse_embedding_specs(self) -> list[ModelSpec]:
        """把配置中的向量模型列表转为 ModelSpec。"""
        specs: list[ModelSpec] = []
        for item in self.config.get("embedding_models") or []:
            specs.append(
                ModelSpec(
                    id=item["id"],
                    provider=item.get("provider", "dashscope"),
                    model_name=item["model_name"],
                    enabled=bool(item.get("enabled", True)),
                    api_key_env=item.get("api_key_env", "DASHSCOPE_API_KEY"),
                )
            )
        if not specs and rag_config.get("embedding_model_name"):
            specs.append(
                ModelSpec(
                    id="legacy_embedding",
                    provider="dashscope",
                    model_name=rag_config["embedding_model_name"],
                )
            )
        return specs

    def list_chat_models(self) -> list[dict[str, Any]]:
        """列出聊天模型及是否当前可用，供 UI 下拉框。"""
        rows = []
        for s in self._chat_specs:
            rows.append(
                {
                    "id": s.id,
                    "model_name": s.model_name,
                    "priority": s.priority,
                    "enabled": s.enabled,
                    "available": self.is_available(s),
                    "note": s.note,
                }
            )
        return rows

    def is_available(self, spec: ModelSpec) -> bool:
        """enabled 且 API Key 非空、非 .env.example 占位符。"""
        if not spec.enabled:
            return False
        key = os.getenv(spec.api_key_env, "").strip()
        return bool(key) and key not in ("your_dashscope_api_key_here",)

    def is_quota_error(self, error: BaseException | str) -> bool:
        """判断异常文本是否像额度/限流错误。"""
        text = str(error)
        if self._quota_re and self._quota_re.search(text):
            return True
        return False

    def _create_chat(self, spec: ModelSpec) -> BaseChatModel:
        """实例化聊天模型：原生 DashScope 或 OpenAI 兼容端点。"""
        if spec.provider == "dashscope_compat":
            from langchain_openai import ChatOpenAI

            base_url = os.getenv(spec.base_url_env or "DASHSCOPE_BASE_URL", "").strip()
            api_key = os.getenv(spec.api_key_env, "").strip()
            if not base_url:
                raise ValueError("dashscope_compat 需要配置 DASHSCOPE_BASE_URL")
            extra: dict[str, Any] = {}
            # qwen3 系列默认可能开启思考模式，问答场景关闭以降低延迟与 token
            if spec.model_name.startswith("qwen3"):
                extra["extra_body"] = {"enable_thinking": False}
            return ChatOpenAI(
                model=spec.model_name,
                api_key=api_key,
                base_url=base_url,
                streaming=True,
                temperature=0,
                timeout=45,
                max_retries=1,
                **extra,
            )
        if spec.provider != "dashscope":
            raise ValueError(f"暂不支持的 provider: {spec.provider}")
        return ChatTongyi(model=spec.model_name, streaming=True)

    def _create_embedding(self, spec: ModelSpec) -> Embeddings:
        """实例化 DashScope Embeddings。"""
        if spec.provider != "dashscope":
            raise ValueError(f"暂不支持的 provider: {spec.provider}")
        return DashScopeEmbeddings(model=spec.model_name)

    def get_chat_model(
        self,
        *,
        mode: str = "auto",
        manual_model_id: str | None = None,
        exhausted_ids: set[str] | None = None,
    ) -> tuple[BaseChatModel, ModelSpec]:
        """按 Auto 或手动 id 选出可用聊天模型。"""
        exhausted = exhausted_ids or set()
        candidates = [s for s in self._chat_specs if self.is_available(s) and s.id not in exhausted]
        if not candidates:
            raise RuntimeError(
                "没有可用的聊天模型：请在 .env 配置 DASHSCOPE_API_KEY，并检查 config/models.yml"
            )

        if mode == "manual":
            if not manual_model_id:
                raise ValueError("手动模式必须指定 manual_model_id")
            chosen = next((s for s in candidates if s.id == manual_model_id), None)
            if chosen is None:
                raise RuntimeError(f"手动指定的模型不可用或不存在: {manual_model_id}")
        else:
            chosen = candidates[0]

        if chosen.id not in self._chat_cache:
            self._chat_cache[chosen.id] = self._create_chat(chosen)
        bind_log_context(model_id=chosen.id)
        log_event("model.select", mode=mode, model_id=chosen.id, model_name=chosen.model_name)
        return self._chat_cache[chosen.id], chosen

    def next_auto_model(
        self,
        current_id: str,
        exhausted_ids: set[str],
    ) -> tuple[BaseChatModel, ModelSpec] | None:
        """Auto 模式把当前模型标为耗尽并切到下一档。"""
        exhausted_ids.add(current_id)
        remaining = [s for s in self._chat_specs if self.is_available(s) and s.id not in exhausted_ids]
        if not remaining:
            log_event("model.switch", level=40, status="exhausted", from_id=current_id)
            return None
        nxt = remaining[0]
        log_event("model.switch", from_id=current_id, to_id=nxt.id, reason="quota_or_rate_limit")
        return self.get_chat_model(mode="auto", exhausted_ids=exhausted_ids)

    def get_embedding_model(self) -> Embeddings:
        """选出可用 Embedding，优先 defaults 中的 id。"""
        defaults = self.config.get("defaults") or {}
        prefer = defaults.get("embedding_model_id")
        specs = self._embedding_specs
        if prefer:
            specs = sorted(specs, key=lambda s: 0 if s.id == prefer else 1)
        for spec in specs:
            if self.is_available(spec):
                if spec.id not in self._embedding_cache:
                    self._embedding_cache[spec.id] = self._create_embedding(spec)
                return self._embedding_cache[spec.id]
        raise RuntimeError("没有可用的 Embedding 模型：请配置 DASHSCOPE_API_KEY")


_router: ModelRouter | None = None


def get_model_router() -> ModelRouter:
    """返回进程内 ModelRouter 单例。"""
    global _router
    if _router is None:
        _router = ModelRouter()
    return _router


def get_chat_model(**kwargs) -> BaseChatModel:
    """快捷获取当前 Auto/手动聊天模型实例。"""
    model, _ = get_model_router().get_chat_model(**kwargs)
    return model


def get_embedding_model() -> Embeddings:
    """快捷获取当前 Embedding 模型。"""
    return get_model_router().get_embedding_model()


# 兼容旧代码：不再在 import 时强制连网创建模型
class _LazyChatProxy:
    def __getattr__(self, item):
        """把属性访问转发到真实聊天模型。"""
        return getattr(get_chat_model(), item)

    def __call__(self, *args, **kwargs):
        """把调用转发到真实聊天模型。"""
        return get_chat_model()(*args, **kwargs)


class _LazyEmbeddingProxy:
    def __getattr__(self, item):
        """把属性访问转发到真实 Embedding。"""
        return getattr(get_embedding_model(), item)


chat_model = _LazyChatProxy()
embedding_model = _LazyEmbeddingProxy()
