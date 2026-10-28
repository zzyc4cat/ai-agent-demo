# -*- coding: utf-8 -*-
"""按 token 用量估算成本（人民币）。价格见 config/pricing.yml。"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from utils.path_tool import get_abs_path

PRICING_PATH = Path(get_abs_path("config/pricing.yml"))


@lru_cache(maxsize=1)
def _pricing() -> dict[str, Any]:
    try:
        data = yaml.safe_load(PRICING_PATH.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def estimate_cost(
    prompt_tokens: int,
    completion_tokens: int,
    model: str | None = None,
) -> float | None:
    """返回估算成本（元）；未知模型返回 None，不瞎猜。"""
    cfg = _pricing()
    models = cfg.get("models") or {}
    key = model or cfg.get("default")
    spec = models.get(key) or {}
    if not spec:
        return None
    return round(
        prompt_tokens / 1_000_000 * float(spec.get("input_per_million", 0))
        + completion_tokens / 1_000_000 * float(spec.get("output_per_million", 0)),
        6,
    )


def default_model() -> str | None:
    """默认计价模型。"""
    return _pricing().get("default")
