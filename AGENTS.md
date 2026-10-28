# AGENTS.md

> AI 代理（以及三个月后的你）进入本项目的入口。
> **先读 `docs/vibe-coding.md`（协作规范），再读 `PRD.md`（需求真源）。**

## 项目是什么

制造业设备与工艺知识库，最小多租户 SaaS。
FastAPI + React + Chroma + SQLite；语料只用公开设备文档。

## 开始前必读（按顺序）

1. `docs/vibe-coding.md` — AI 协作规范 + 开发规范
2. `PRD.md` — 需求、范围、指标、里程碑（唯一真源）
3. `architecture.md` — 目标架构与数据流
4. `TODO.md` — 当前状态快照与待办
5. `development.md` — 命令与回归清单

## 目录（现状）

```text
src/
  api_server.py        FastAPI 入口（/auth /kb /admin /health）
  rag/                 入库、切分、检索、缓存、租户配置
  services/            账号、会话、管理、成本、SQLite
  model/               模型路由
  utils/               配置、日志、文件、路径
web/                  React 前端（Vite + TS，构建产物 dist/ 随仓库）
tests/                pytest
scripts/              bootstrap、评测、建租户、建账号、备份
tenants/              租户 YAML（collection / corpus / scope）
docs/                 规范与截图
config/               YAML
prompts/              提示词
data/tenants/{id}/    租户语料与上传文件
```

## 常用命令

```powershell
# 后端（或直接 .\start-api.ps1）
$env:PYTHONPATH="src"; .\.venv\Scripts\python -m uvicorn api_server:app --app-dir src --port 8000

# 前端
cd web; npm run dev        # 开发（代理到 8000）
cd web; npm run build      # 构建到 web/dist

# 测试
$env:PYTHONPATH="src"; .\.venv\Scripts\python -m pytest tests -q

# 评测（50 条）
$env:PYTHONPATH="src"; .\.venv\Scripts\python scripts/eval_kb.py --ids all

# 建租户 / 建账号（密码走环境变量或交互输入，不写脚本）
$env:PYTHONPATH="src"; .\.venv\Scripts\python scripts/init_tenant.py --id demo2
$env:USER_PASSWORD="***"; .\.venv\Scripts\python scripts/create_user.py --username someone --role admin
```

## 红线

- 密钥、密码、token 不进代码、日志、提交信息；密码只存 scrypt 哈希。
- 租户与用户一律从登录 token 推导，**不信任客户端传的 `X-Tenant`**。
- 不删除、不跳过 `tests/`；改检索/切分/提示词必须跑评测。
- 不擅自升级依赖大版本；新依赖写进 `requirements.txt`。
- 不把公司内部资料放进 `data/`；语料必须公开且在 `corpus.csv` 记录来源与许可。
- 没经确认不 commit、不删数据、不改 schema。

## 当前阶段

- **M1–M3 已完成**：评测基线、本地部署、多租户、账号体系、React 对话页、管理页（上传/URL 导入/审计）。
- **M4 待启动**：内测 10 人、demo 视频、模拟面试、简历。
- 旧个人助手代码（`agent/`、Streamlit 入口、`/chat`）已于 2026-10-28 清理。
- PRD v0.10 是目标；实现进度以 `TODO.md` 为准。

## 代码风格

- Python 3.12，类型注解，函数短小，职责单一。
- 配置进 `config/` 与 `tenants/`，不硬编码。
- 日志走 `utils/logger_handler.py`（`log_event` / `logger`），不用 `print`。
- 前端请求集中在 `web/src/api.ts`，组件不直接 fetch。

## 不确定时

先查 `docs/vibe-coding.md`、`PRD.md`、`architecture.md`；仍不确定，写进 `TODO.md` 的「待决问题」，**不要猜着改核心逻辑**。

> 核心原则：每个环节做正确的事；能验证的才叫完成。
