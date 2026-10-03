# 个人综合助手 Agent

基于 **LangChain / LangGraph ReAct + 混合 RAG** 的本地个人助手，覆盖生活 / 工作 / 学习场景。核心不是「调一次大模型」，而是：**工具循环、知识库拒答、多用户数据隔离、可配置检索与安全边界**。

> 系统提示词优先级最高。知识库与工具依据不足时必须回答「不知道」，禁止编造。

| 文档 | 用途 |
|------|------|
| [`README.md`](README.md) | 项目说明、功能、技术栈、启动与边界（本文） |
| [`DEBUG.md`](DEBUG.md) | 调参 / 排障：改哪个配置、如何对比效果 |
| [`DEBUG_LOG.md`](DEBUG_LOG.md) | 历史验收归档 + 运行时阶段日志（过大自动裁剪） |

---

## 目录

1. [项目定位与边界](#1-项目定位与边界)
2. [架构与数据流](#2-架构与数据流)
3. [功能说明](#3-功能说明)
4. [技术栈](#4-技术栈)
5. [仓库地图](#5-仓库地图)
6. [快速开始](#6-快速开始)
7. [配置与环境变量](#7-配置与环境变量)
8. [HTTP API](#8-http-api)
9. [安全模型](#9-安全模型)
10. [测试与评测](#10-测试与评测)
11. [Docker](#11-docker)
12. [常见问题](#12-常见问题)

---

## 1. 项目定位与边界

**是什么：** 单机可运行的个人 Agent Demo / 面试作品。Streamlit 为主界面，FastAPI 为可选接入层。

**不是什么：**

| 已实现 | 明确未做（避免误读） |
|--------|----------------------|
| 单 Agent ReAct（思考 → 工具 → 观察 → 回答） | Multi-Agent 协作图、MCP / A2A |
| 本地 SQLite 多用户数据隔离 | 密码登录、企业多租户、SSO |
| 混合检索 + 弱门控拒答 | Query Rewrite / HyDE（配置项存在但未启用实现） |
| 通义 DashScope 云模型 | Ollama / vLLM 私有化推理、LoRA 微调 |
| Chroma 本地向量库 | Milvus / Qdrant 生产集群 |
| 黄金集脚本 `run_eval.py` | 生产级 Eval Harness / CI 门禁（仓库无 GitHub Actions） |

Streamlit 侧用**用户名创建/切换**身份，适合本机自用。若把服务暴露到网络，必须以 API Key 使用 FastAPI，且不要把 Streamlit 当多租户后台。

---

## 2. 架构与数据流

```text
用户
 ├─ Streamlit  app.py          用户名切换、会话菜单、技能/模型选择、对话
 └─ FastAPI    src/api_server.py   /health 公开；/chat、/rag/summarize 需 AGENT_API_KEY
        │
        ▼
 ReactAgent（src/agent/react_agent.py）
  ├─ PromptGuard：泄露系统提示拒答；忽略规则类请求注入安全提醒
  ├─ ModelRouter：Auto 按 priority 选模；额度/限流可换模；手动模式不静默换模
  ├─ LangGraph create_agent
  │    middleware：monitor_tool / log_before_model / skill_prompt_switch
  │    tools：Tools-A + Tools-B
  │    checkpointer：优先 storage/checkpoints.db，失败回退 MemorySaver
  └─ thread_id = {user_pk}:{conversation_id}
        │
        ├─ RAG  rag_summarize / RagSummarizeService
        │    L2 答案缓存 → L1 文档缓存 → 混合检索
        │    向量(Chroma) + BM25 → RRF → 可选 gte-rerank → 分数门控
        │    sample 库 + 登录用户 personal 库（collection: agent_personal_{id}）
        │
        └─ 其它工具：搜索 / 抓页 / 天气 / 待办笔记记忆 / 沙箱 / 闪卡 / 计算器
               │
               ▼
 SQLite storage/app.db     用户、会话、消息、待办、笔记、记忆、kb 元数据、查询缓存
 Chroma  chroma_db/        向量
 文件    workspace/u{id}/  每用户沙箱
 语料    data/sample/ 与 data/personal/{user_id}/
```

**隔离约定：**

- 业务表按 `user_id` 过滤；Agent 用 `ContextVar` 注入当前用户。
- 个人知识库 collection 名 `agent_personal_{user_id}`；语料目录 `data/personal/{user_id}/`。
- 工作区仅 `workspace/u{user_id}/`，路径用 `Path.is_relative_to`，禁止 `..` 与绝对路径。
- 示例库 `agent_sample` 会并入每位登录用户的检索（另可读遗留 collection `agent`）。

---

## 3. 功能说明

### 3.1 对话 Agent

- **范式：** ReAct。中间 `ToolMessage` 与带 `tool_calls` 的 AI 轮次不对用户展示；工具原文带 `<<<UNTRUSTED_DATA>>>` 标记。
- **技能（Skills）：** 侧栏中文名映射内部 id；仅白名单且必须有对应 `prompts/skills/{id}.txt`。`set_skill` 按用户写入运行时状态，后续模型调用立即换系统提示。非法 skill 回退主 Prompt。
- **递归上限：** `recursion_limit=25`。
- **失败：** 异常写入日志，对用户只提示执行失败（不回传堆栈）。Auto 额度错误可换模重试本轮。

| 界面中文 | skill id | Prompt 文件 |
|----------|----------|-------------|
| 默认助手 | `default` | `prompts/main_prompt.txt` |
| 每日简报 | `daily_briefing` | `prompts/skills/daily_briefing.txt` |
| 周报复盘 | `weekly_review` | `prompts/skills/weekly_review.txt` |
| 会议纪要 | `meeting_minutes` | `prompts/skills/meeting_minutes.txt` |
| 文稿润色 | `writing_polish` | `prompts/skills/writing_polish.txt` |
| 学习导师 | `study_tutor` | `prompts/skills/study_tutor.txt` |
| 深度消化 | `deep_digest` | `prompts/skills/deep_digest.txt` |
| 间隔复习 | `spaced_repetition` | `prompts/skills/spaced_repetition.txt` |
| 错题归因 | `error_attribution` | `prompts/skills/error_attribution.txt` |
| 学习计划 | `study_plan` | `prompts/skills/study_plan.txt` |

### 3.2 多模型

注册表：`config/models.yml`。需 `.env` 中 `DASHSCOPE_API_KEY`（占位符视为不可用）。

| id | 模型 | Auto priority | 说明 |
|----|------|---------------|------|
| `qwen_turbo` | qwen-turbo | 10（优先） | 低成本 |
| `qwen_plus` | qwen-plus | 20 | 均衡 |
| `qwen3_max` | qwen3-max | 30 | 高质量 |
| `dashscope_embedding_v4` | text-embedding-v4 | — | 向量 |

- **Auto：** 按 priority 选用；匹配 `quota_error_markers` 时换下一档。
- **手动：** 侧栏指定模型；额度不足只提示，不换模。
- 对话 L2 缓存 key 绑定当前聊天 `model_id`，避免换模串答案。

### 3.3 RAG

流水线：规范化查询 →（可选）L2/L1 缓存 → 向量召回 `vector_k` + BM25 `bm25_k` → RRF → DashScope `gte-rerank`（失败则用 RRF 分）→ 门控 → 填入 `prompts/rag_summarize.txt`。

**弱门控（与配置注释一致）：** `best_vector < min_similarity` **且** `best_bm25 < bm25_min_score` 才整路拒答返回空，上层总结为「不知道」。仅向量弱、关键词仍强时会放行融合。

**入库：** `python -m rag.ingest --scope sample|personal --user <id> [--path] [--force]`。按文件 `content_hash` 增量更新；`kb_version` 变化使查询缓存失效。个人默认路径为 `data/personal/{user_id}/`。支持 txt / pdf / md。切分以 `rag_runtime.yml` 的 chunking（800/100）为主，与 `chroma.yml` 旧值合并。

**缓存：** L1 缓存检索文档，L2 缓存最终答案；可落 SQLite。Embedding 磁盘缓存目录 `storage/embedding_cache/`，key 含 embedding 模型 id。

### 3.4 本地用户与业务数据

SQLite：`storage/app.db`（`PRAGMA foreign_keys=ON`）。

- 用户创建/切换、偏好、上次用户。
- 会话：新建、重命名、置顶、删除；消息按用户隔离。
- 待办：增删改完成状态（`task_complete` 校验归属）。
- 笔记、长期记忆（kind + content）。
- 闪卡：到期列表与对错反馈（间隔天数）。

Streamlit 提供会话菜单与技能/模型控件。界面流式展示为按块输出（底层 `stream_mode=values`，非 token 流）。

### 3.5 工具一览

工具返回一律 `wrap_untrusted`。失败时倾向「不知道」+ 原因，不假装成功。

**Tools-A**

| 工具 | 入参 | 行为要点 |
|------|------|----------|
| `rag_summarize` | `query` | 示例库 + 当前用户个人库；空检索 → 不知道 |
| `web_search` | `query` | DuckDuckGo（ddgs）为主；失败且配置了 `TAVILY_API_KEY` 则回退 Tavily |
| `fetch_webpage` | `url` | 仅 http(s)；拦截本机/内网/云元数据；不盲目跟随危险重定向；去标签截断约 6000 字 |
| `get_weather` | `city` | 和风：需 `QWEATHER_API_KEY` + `QWEATHER_API_HOST` |
| `datetime_now` | 无 | 本地日期时间与星期 |
| `task_add` / `task_list` / `task_complete` | 见描述 | 仅当前用户 |
| `note_write` / `note_search` | title/body 或 query | 仅当前用户 |
| `memory_set` / `memory_get` | kind, content | 仅当前用户 |
| `workspace_list` / `workspace_read` | 相对路径 | 仅 `workspace/u{id}/` |
| `kb_ingest_sample` | 无 | 增量加载 sample 语料 |
| `set_skill` | `skill_name` | 白名单；立即影响后续 Prompt |

**Tools-B**

| 工具 | 入参 | 行为要点 |
|------|------|----------|
| `calculator` | `expression` | AST 白名单四则与幂；长度 ≤200；幂嵌套 ≤2；结果绝对值过大拒绝 |
| `flashcard_add` / `flashcard_due` / `flashcard_answer` | 见描述 | 按用户隔离 |

### 3.6 界面、启动与日志

- 一键：`start.bat` / `start.ps1` → `scripts/bootstrap.py`（venv、依赖、目录、`.env` 检查）→ Streamlit。
- 机器日志：`logs/agent.log`（按天轮转）。
- 人读阶段：`DEBUG_LOG.md` 自动追加；超体积裁剪运行时区。
- 环境：`LOG_LEVEL`、`LOG_JSON`、`LOG_PROMPT`（Prompt 片段仅本机短时开启）。

---

## 4. 技术栈

### 4.1 语言与运行时

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | ≥ 3.10（开发常用 3.12） | 主语言 |
| venv | 标准库 | `.venv/` |

依赖锁定范围见 [`requirements.txt`](requirements.txt)（LangChain / LangGraph 1.x 线）。

### 4.2 Agent 编排

| 技术 | 用途 |
|------|------|
| LangChain | Tool、Prompt、LCEL、Chat 封装 |
| LangGraph | `create_agent`、middleware、Checkpointer |
| langgraph-checkpoint-sqlite | 会话状态 → `storage/checkpoints.db` |
| 自研 middleware | 工具耗时与错误降级、模型前日志、Skill 动态系统提示 |

### 4.3 模型与向量

| 技术 | 用途 |
|------|------|
| 阿里云百炼 DashScope | 对话、Embedding、可选重排 |
| ChatTongyi（langchain-community） | Qwen 系列 |
| DashScopeEmbeddings | text-embedding-v4 |
| ModelRouter（`src/model/factory.py`） | 可用性检测、Auto/手动、额度判定 |

### 4.4 RAG

| 技术 | 用途 |
|------|------|
| Chroma + langchain-chroma | 本地持久化向量库 |
| rank_bm25 | 稀疏检索（pickle 按 collection 落盘） |
| RRF | 多路融合 |
| DashScope gte-rerank | 重排；失败回退 RRF |
| RecursiveCharacterTextSplitter / MarkdownHeaderTextSplitter | 切分 |
| pypdf / TextLoader 等 | 文档加载 |

### 4.5 数据、配置与外部调用

| 技术 | 用途 |
|------|------|
| SQLite | 业务库 `storage/app.db` |
| PyYAML（SafeLoader） | `config/*.yml` |
| python-dotenv | `.env` |
| httpx | 天气、Tavily、重排 HTTP |
| ddgs / duckduckgo-search | 网页搜索 |

### 4.6 界面、服务与质量

| 技术 | 用途 |
|------|------|
| Streamlit | 主 UI |
| FastAPI + Uvicorn + Pydantic | 可选 HTTP API |
| Docker / Compose | `deploy/` |
| pytest | `tests/` |
| logging + TimedRotatingFileHandler | `logs/agent.log` |

`tenacity` 在依赖中预留，当前核心路径未作为重试主实现。

---

## 5. 仓库地图

```text
app.py                    Streamlit 入口
start.bat / start.ps1     一键启动
src/
  agent/react_agent.py    Agent 主体、换模、流式输出
  agent/tools/            Tools-A/B、护栏、SSRF、天气客户端、middleware
  rag/                    入库、向量、BM25、混合检索、缓存、总结
  services/               SQLite：用户 / 会话 / 待办 / 笔记
  model/factory.py        模型路由
  utils/                  配置、日志、路径、Prompt 加载
  api_server.py           FastAPI
scripts/bootstrap.py      环境准备
scripts/run_eval.py       黄金集 + 工具冒烟，报告 logs/eval/
deploy/                   Dockerfile、compose
config/                   YAML
prompts/                  主 Prompt、RAG Prompt、skills/
data/sample/              示例语料
data/personal/{user_id}/  个人语料（按用户）
tests/
storage/ logs/ chroma_db/ workspace/   运行时，默认 gitignore
```

| 想改的行为 | 先看 |
|------------|------|
| 对话循环、换模、thread | `src/agent/react_agent.py` |
| 工具与沙箱 | `src/agent/tools/agent_tools.py` |
| 检索门控 | `src/rag/retriever.py`、`config/rag_runtime.yml` |
| 模型列表 | `config/models.yml` |
| API 鉴权 | `src/api_server.py` |
| 调参对比 | [`DEBUG.md`](DEBUG.md) |

---

## 6. 快速开始

**环境：** Python ≥ 3.10。对话与向量需要阿里云百炼 API Key。

### 6.1 一键（Windows）

项目根目录双击 `start.bat`，或 PowerShell：

```powershell
.\start.ps1
```

首次会创建 `.venv`、安装依赖、检查 `.env`。请把 `DASHSCOPE_API_KEY` 改成真实 Key。

### 6.2 手动

Windows：

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
REM 编辑 .env 填入 DASHSCOPE_API_KEY
set PYTHONPATH=src
python -m rag.ingest --scope sample
streamlit run app.py
```

Linux / macOS：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env
export PYTHONPATH=src
python -m rag.ingest --scope sample
streamlit run app.py
```

个人库示例：

```bash
# 语料放到 data/personal/<SQLite用户id>/ 后再入库
python -m rag.ingest --scope personal --user 1
```

### 6.3 最小验收

1. 侧栏创建用户，确认有可用模型。
2. 问「番茄工作法专注多久」一类示例库问题：应能引用语料，而不是空编。
3. 问「某某星座飞船的官方射程」一类库外事实：应「不知道」或明确依据不足。
4. 切换技能「周报复盘」后再问，口吻/结构应跟随 skill Prompt。
5. 无天气 Key 时问天气：应提示未配置，而不是伪造气温。

---

## 7. 配置与环境变量

### 7.1 `.env`

| 变量 | 必填 | 作用 |
|------|------|------|
| `DASHSCOPE_API_KEY` | 对话/向量 | 百炼 |
| `AGENT_API_KEY` | 仅当用 FastAPI 写接口 | 未配置则 `/chat`、`/rag/summarize` 返回 503 |
| `QWEATHER_API_KEY` + `QWEATHER_API_HOST` | 天气 | Host 形如 `xxx.qweatherapi.com`，不要带 `https://` |
| `TAVILY_API_KEY` | 否 | DDG 失败时的搜索回退 |
| `LOG_LEVEL` / `LOG_JSON` / `LOG_PROMPT` | 否 | 日志 |

### 7.2 YAML（改什么 → 影响什么）

| 文件 | 关键项 | 影响 |
|------|--------|------|
| `config/models.yml` | `priority`、`enabled`、`quota_error_markers` | Auto 顺序与换模判定 |
| `config/rag_runtime.yml` | `min_similarity`、`bm25_min_score`、`vector_k`/`bm25_k`、缓存 TTL、collection 名 | 召回松紧、拒答、费用 |
| `config/chroma.yml` | `persist_directory`、`data_path`、允许后缀 | 向量落盘与 sample 默认目录 |
| `config/prompt_guard.yml` | leak / ignore 正则 | 泄露拒答 vs 提醒后继续 |
| `config/logging.yml` | 级别、轮转、DEBUG_LOG 裁剪 | 日志体积 |
| `config/prompts.yml` | Prompt 路径 | 主提示 / RAG 总结 / skills 目录 |

`enable_query_rewrite`、`semantic_l1` 等开关目前为占位，不要当成已上线能力。逐 key 对比方法见 [`DEBUG.md`](DEBUG.md)。

---

## 8. HTTP API

启动（需已设 `PYTHONPATH=src` 且 `.env` 有 `AGENT_API_KEY`）：

```bash
uvicorn api_server:app --app-dir src --port 8000
```

| 方法 | 路径 | 鉴权 | 说明 |
|------|------|------|------|
| GET | `/health` | 无 | `{ "status": "ok", "api_key_configured": true/false }` |
| POST | `/chat` | Bearer 或 `X-API-Key` | body：`message`、`username`、`skill`（白名单）、`conversation_id` 可选 |
| GET | `/rag/summarize?q=...&username=...` | 同上 | 仅走 RAG 总结 |

```bash
curl -s http://127.0.0.1:8000/health
curl -s -X POST http://127.0.0.1:8000/chat ^
  -H "Content-Type: application/json" ^
  -H "X-API-Key: 你的AGENT_API_KEY" ^
  -d "{\"message\":\"现在几点\",\"username\":\"api_user\"}"
```

`skill` 不在白名单 → 400。错误密钥 → 401。未配置 Key → 503。服务端异常对客户端脱敏。

---

## 9. 安全模型

1. **系统提示不可被用户或工具内容覆盖**；RAG/工具结果包在 UNTRUSTED 标记内。
2. **泄露类请求**（打印 system prompt 等）直接拒答；**忽略规则类**注入提醒后仍用原系统提示继续。
3. **依据不足 →「不知道」**，禁止把检索噪声编成事实。
4. **API：** 用户名不是凭证；必须 `AGENT_API_KEY`（`secrets.compare_digest`）。
5. **SSRF：** `fetch_webpage` 拒绝 localhost、环回、私网、链路本地、云 metadata。
6. **沙箱：** 每用户目录 + `is_relative_to`；禁止 `..` 与绝对路径。
7. **配置加载：** YAML `SafeLoader`。
8. **计算器：** 无 `eval`；限制表达式长度与幂嵌套。
9. **密钥：** `.env` gitignore；日志对常见 key 字段脱敏。`LOG_PROMPT=1` 有泄露风险。

正则护栏可被改写绕过，不能替代模型侧纪律与工具硬限制。本项目按**本机可信用户**设计。

---

## 10. 测试与评测

```bash
# 仓库根目录，保证能 import src
set PYTHONPATH=src
pytest tests -q

python scripts/run_eval.py
```

pytest 覆盖配置与路径、用户/会话隔离、工具与沙箱、护栏、天气降级、RAG 规范化/RRF/缓存/弱门控、API health 与鉴权（`tests/test_p0_security.py`）等。全量约 80 条（随用例增减）。

`run_eval.py` 读取 `tests/fixtures/rag_eval.jsonl`，尽量少调 LLM；部分期望标签较宽松，适合回归门控而非对外宣称准确率。报告目录：`logs/eval/`。

---

## 11. Docker

在 `deploy/` 下：

```bash
docker compose up --build
```

默认起 Streamlit `8501`，挂载 `storage`、`chroma_db`、`logs`、`data`、`workspace`，读取仓库根 `.env`。镜像暴露 8000 但 compose 未默认启动 API。容器监听 `0.0.0.0`，请配合本机防火墙，勿在无鉴权情况下把 Streamlit 对公网开放。

---

## 12. 常见问题

| 现象 | 处理 |
|------|------|
| 无法初始化助手 / 无可用模型 | 检查 `DASHSCOPE_API_KEY` 是否为真实值 |
| 知识问答总是「不知道」 | 是否已 ingest；`min_similarity` / `bm25_min_score` 是否过高；语料是否为空 |
| 胡编知识库内容 | 看 `DEBUG_LOG.md` 里 `rag.retrieve` 的 `gated`、`weak_gate`、`best_vector` |
| API 503 | 未设置 `AGENT_API_KEY` |
| API 401 | Header 不是 `Authorization: Bearer` 或 `X-API-Key`，或 Key 错误 |
| 抓网页提示禁止访问 | SSRF 拦截了本机/内网 URL |
| 天气不可用 | 同时配置 Key 与 API Host |
| 个人库找不到自己的文档 | 文件是否在 `data/personal/<用户id>/` 且对该 id 执行过 ingest |
| import 失败 | `PYTHONPATH` 需包含 `src` |

一次对话可用界面或日志中的 `request_id` 串联 `logs/agent.log` 与 `DEBUG_LOG.md`。
