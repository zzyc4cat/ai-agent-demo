# AGENTS.md

> AI 代理（以及三个月后的你）进入本项目的入口。**先读这里，再读 `PRD.md`。**

## 项目是什么

制造业设备与工艺知识库（内部知识助手），带最小多租户。
代码库起源于“个人综合助手 Agent”，正在按 `PRD.md` v0.10 改造。**旧代码可用，但不代表目标架构。**

## 开始前必读（按顺序）

1. `PRD.md` — 需求、范围、指标、里程碑（唯一真源）
2. `architecture.md` — 目标架构与数据流
3. `TODO.md` — 当前任务与优先级
4. `development.md` — 命令与回归清单

## 目录（现状）

```text
app.py                 Streamlit 入口（对内后台）
src/
  api_server.py        FastAPI 入口
  agent/               Agent 主体与工具
  rag/                 入库、检索、缓存
  services/            SQLite 业务表
  model/               模型路由
  utils/               配置、日志、路径
tests/                 pytest
scripts/               bootstrap、评测
config/                YAML
prompts/               提示词
deploy/                Docker
data/                  语料（sample / personal）
```

目标态会新增 `web/`（React 对话页）与 `tenants/`（租户配置），见 `architecture.md`。

## 常用命令

```powershell
# 后端
$env:PYTHONPATH="src"; uvicorn api_server:app --app-dir src --port 8000

# 管理台
streamlit run app.py

# 测试
$env:PYTHONPATH="src"; pytest tests -q

# 评测
$env:PYTHONPATH="src"; python scripts/run_eval.py
```

## 红线

- 不改 `.env`，不把密钥写进代码、日志、提交。
- 不删除、不跳过 `tests/`。
- 不擅自升级依赖大版本。
- 不把公司内部资料放进 `data/`。
- 语料只用公开文档，且必须在 `corpus.csv` 记录来源 URL 与许可。
- 改检索、切分、提示词之后，必须跑评测（见 `development.md` 回归清单）。

## 当前阶段

- 进行中：W1（语料 + 评测 + 基线）。
- 旧功能（天气、待办、笔记等个人助手工具）保留，但**不新增**。
- 目标架构见 `architecture.md` 的「目标态」。

## 代码风格

- Python 3.12，类型注解，函数短小。
- 配置进 `config/`，不硬编码。
- 日志走 `src/utils/logger_handler.py`，不用 `print`（临时调试除外）。
- 新依赖写进 `requirements.txt`。

## 不确定时

先查 `PRD.md` 与 `architecture.md`；仍不确定，写进 `TODO.md` 的「待决问题」，**不要猜着改**。

> 核心原则：每个环节做正确的事。
