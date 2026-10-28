# DEBUG_LOG — 历史归档与运行日志

> **本文件职责**：① 整合既往升级/检测记录；② **每次项目运行自动追加**各阶段情况。  
> 调参说明见 [`DEBUG.md`](DEBUG.md)。项目说明见 [`README.md`](README.md)。  
> 体积过大时由程序自动裁剪「运行时记录」尾部（参数见 `config/logging.yml`）。

---

## 使用说明

- 机器详细日志仍在 `logs/agent.log`（按天轮转）。  
- 本文件追加格式：`### [时间] stage=...` + 关键字段。  
- 请勿手工删除下方固定分隔标题 `## 运行时记录（自动追加）`，否则清理逻辑可能找不到锚点。

---

## 历史归档（整合自 UPGRADE_LOG / RAG_TEST_LOG / PHASE_UPGRADE_TEST_LOG 等）

### 平台 Phase 0–6（2026-09-24）

| 阶段 | 结果 | 测试摘要 |
|------|------|----------|
| 0 地基 | 达标 `状态0` | test_phase0 → 7 passed |
| 1 语料迁移 | 达标 `状态1` | test_phase1 → 5 passed |
| 2 用户存储 | 达标 `状态2` | test_phase2 → 3 passed |
| 3 Tools-A | 达标 `状态3` | test_phase3 → 4 passed（RAG 懒加载） |
| 4 Skills-A | 达标 `状态4` | test_phase4 → 2 passed |
| 5 前端 | 达标 `状态5` | UI 源码断言通过 |
| 6 增强 | 达标 `状态6` | 全量曾 25 passed；计算器/闪卡/护栏 |

### UI 与会话（2026-09-24）

- 优化1–5：caption、切用户、新对话/历史、中文模式技能、DuckDuckGo 搜索 → 相关 pytest 通过。  
- 会话菜单：重命名/置顶/删除；热修复 pinned 参数、菜单关闭、技能 selectbox 双击问题。  

### 和风天气（2026-09-24）

- 接入 `qweather_client`；需 `QWEATHER_API_KEY` + `QWEATHER_API_HOST`。  
- 实网上海天气验证通过；test_qweather 等 **10 passed**。  

### RAG 大体量 A/B/C（2026-09-24）

- Hybrid + 缓存 + 分库 + 增量入库 + embedding 缓存。  
- 阶段测试合计 **21 passed**（含 multiround / phase1）。  
- Qdrant 阶段 D 暂缓。  

### 招聘对照与路线图（2026-09-25）

- 市场缺口：评测看板、私有推理、API、长记忆等（详见 README 可优化清单）。  
- 原 `Study.md` / `UPGRADE_ROADMAP.md` 要点已并入 README / DEBUG。  

### 升级执行检测（2026-09-25）

| 项 | 结果 |
|----|------|
| Phase0 一键启动 3 轮 bootstrap | 通过 |
| Phase1 eval 3 轮 | 工具 100%；RAG **87.5%** |
| API /health 3 轮 | 通过 |
| 整体冒烟 3 轮 | 10 passed |
| 递归入库修复 | sample 6 文件 / 8 chunks |
| 弱相关门控 `min_similarity=0.55` | 拒答改善；1 题会议纪要假阳性待调 |

### 目录重整（2026-09-26）

- 业务包迁入 `src/`；Docker 迁入 `deploy/`；评测报告改 `logs/eval/`。  
- 根文档仅保留 README / DEBUG / DEBUG_LOG。  
- 路径通过 `path_tool` 上溯定位仓库根；`app.py` / `scripts` / `tests/conftest` 注入 `PYTHONPATH=src`。  
- pytest 全量通过。

### P0 安全与正确性加固（2026-10-03）

针对面试作品审计中的 Critical/High 项落地修复，并做多轮自测。

#### 改动摘要

| 项 | 改动 | 预期效果 |
|----|------|----------|
| API 鉴权 | `/chat`、`/rag/summarize` 需 `AGENT_API_KEY`（Bearer / X-API-Key）；未配置 → 503 | 杜绝「用户名即身份」裸奔 |
| SSRF | `ssrf_guard` + `fetch_webpage` 禁本机/内网/元数据；不自动跟随危险重定向 | 阻止内网探测 |
| Workspace | `Path.is_relative_to` + 每用户 `workspace/u{id}/` | 修前缀逃逸；用户文件隔离 |
| 个人语料 | `data/personal/{user_id}/` | 多用户不再共享同一目录 |
| 弱门控 | 向量弱 **且** BM25 弱才拒答；新增 `bm25_min_score` | 关键词强命中不再被误杀 |
| set_skill | 按 user 模块级状态（兼容 LangChain copy_context） | 中途切换真正生效 |
| 技能白名单 | 裁剪为有 prompt 文件的 skill | 消除静默回落 |
| 异常脱敏 | Agent/API 不对用户抛原始异常 | 减少信息泄露 |
| 其它 | YAML SafeLoader；SQLite `foreign_keys=ON`；计算器幂运算限制；缓存绑定 model id | 加固与正确性 |

#### 自测结果（多次）

| 轮次 | 命令 | 结果 |
|------|------|------|
| R1 聚焦 | `pytest tests/test_p0_security.py tests/test_phase3.py tests/test_phase4.py tests/test_rag_phase_a.py tests/test_api_health.py tests/test_phase2.py tests/test_phase56_functional.py -q` | **27 passed** |
| R2 全量 | `pytest tests -q` | **80 passed** |
| R3 全量 | `pytest tests -q` | **80 passed** |
| R4 P0 效果 | `pytest tests/test_p0_security.py` + 弱门控两例 | **8 passed** |
| R5 全量 | `pytest tests -q` | **80 passed** |

新增用例：`tests/test_p0_security.py`（鉴权 / SSRF / 个人路径 / 技能文件对齐 / 计算器限制）。

#### 效果抽检（手工脚本，2026-10-03）

| 检查点 | 结果 |
|--------|------|
| `unsafe_url_reason(http://127.0.0.1/…)` | 拒绝（环回） |
| `unsafe_url_reason(http://169.254.169.254/…)` | 拒绝（保留/元数据） |
| `unsafe_url_reason(https://example.com/)` | 放行（None） |
| `fetch_webpage(localhost)` | 返回「不知道」+ 禁止访问 |
| 个人路径 user1 ≠ user2 | `data/personal/1` vs `data/personal/2` |
| 向量弱(0.2)+BM25 强(4.0) | **召回成功**，`weak_gate` 未触发 |
| 向量弱+BM25 弱 | `weak_gate=True`，拒答 |
| API 无 `AGENT_API_KEY` 调 `/chat` | **503** |
| API 错误 Key | **401** |
| `set_skill(weekly_review)` 后 `get_active_skill()` | **weekly_review** |

结论：P0 改动未破坏既有功能（全量 80 用例连续 3 轮通过）；安全与门控行为符合预期。  
说明：Streamlit 仍为本地用户名切换（无密码），属单机 Demo 约定；API 侧已强制 Key。

---

## 运行时记录（自动追加）

<!-- RUNTIME_LOG_START -->

（以下由程序在启动、对话、检索等阶段自动写入。）


### [2026-09-26 00:21:08] stage=app.start req=- user=- model=-
- entry=doc_reorg_test

### [2026-09-26 00:21:08] stage=rag.retrieve req=- user=- model=-
- vector_hits=1 gated=1 note=trim_test

### [2026-09-26 00:22:10] stage=app.start req=- user=- model=-
- entry=streamlit page=app.py

### [2026-09-26 00:22:13] stage=app.start req=- user=- model=-
- entry=streamlit page=app.py

### [2026-09-26 00:22:43] stage=app.start req=- user=- model=-
- entry=streamlit page=app.py

### [2026-09-26 00:22:46] stage=app.start req=- user=- model=-
- entry=streamlit page=app.py

### [2026-09-26 00:29:09] stage=user.create req=- user=- model=-
- user_id=1 username=PinUser

### [2026-09-26 00:29:09] stage=user.create req=- user=- model=-
- user_id=1 username=KwUser

### [2026-09-26 00:29:09] stage=user.create req=- user=- model=-
- user_id=1 username=OverallUser

### [2026-09-26 00:29:10] stage=user.create req=- user=- model=-
- user_id=1 username=OverallUser

### [2026-09-26 00:29:34] stage=rag.cache req=- user=- model=-
- cache_hit=answer user_scope=u:1

### [2026-09-26 00:29:34] stage=rag.cache req=- user=- model=-
- action=invalidate user_scope=u:1

### [2026-09-26 00:29:34] stage=rag.cache req=- user=- model=-
- cache_hit=miss user_scope=u:1

### [2026-09-26 00:29:34] stage=guard.block req=- user=- model=-
- kind=leak matched=完整系统提示词

### [2026-09-26 00:29:34] stage=rag.retrieve req=- user=- model=-
- vector_hits=8 bm25_hits=8 fused=0 rerank=skipped rerank_top=0 gated=0 top_score=0.0 best_vector=0.4439884207235894 best_bm25=5.205306058801778 weak_gate=True query_preview=完全不存在的星座飞船燃料配方XYZ-999

### [2026-09-26 00:29:34] stage=rag.retrieve req=- user=- model=-
- status=empty query_preview=完全不存在的星座飞船燃料配方XYZ-999 vector_hits=8 bm25_hits=8 fused=0 rerank=skipped rerank_top=0 gated=0 top_score=0.0 best_vector=0.4439884207235894 best_bm25=5.205306058801778 weak_gate=True

### [2026-09-26 00:29:34] stage=chat.start req=req_test_p0 user=u1 model=m1
- phase=0 probe=True

### [2026-09-26 00:29:34] stage=guard.block req=- user=- model=-
- kind=leak matched=输出\s*(你的|完整的)?\s*系统提示

### [2026-09-26 00:29:34] stage=guard.block req=- user=- model=-
- kind=ignore_remind matched=ignore\s+(all\s+)?(previous|prior|above)\s+instructions

### [2026-09-26 00:29:34] stage=guard.block req=- user=- model=-
- kind=leak matched=reveal\s+(your\s+)?(system\s+)?prompt

### [2026-09-26 00:29:35] stage=bootstrap.ok req=- user=- model=-
- streamlit=E:\Study\Programs\AI Agent Demo\.venv\Scripts\streamlit.exe venv=E:\Study\Programs\AI Agent Demo\.venv\Scripts\python.exe

### [2026-09-26 00:29:35] stage=bootstrap.ok req=- user=- model=-
- streamlit=E:\Study\Programs\AI Agent Demo\.venv\Scripts\streamlit.exe venv=E:\Study\Programs\AI Agent Demo\.venv\Scripts\python.exe

### [2026-09-26 00:29:35] stage=bootstrap.ok req=- user=- model=-
- streamlit=E:\Study\Programs\AI Agent Demo\.venv\Scripts\streamlit.exe venv=E:\Study\Programs\AI Agent Demo\.venv\Scripts\python.exe

### [2026-09-26 00:29:35] stage=user.create req=- user=- model=-
- user_id=1 username=Alice

### [2026-09-26 00:29:35] stage=user.create req=- user=- model=-
- user_id=2 username=Bob

### [2026-09-26 00:29:35] stage=user.switch req=- user=- model=-
- user_id=2 username=Bob

### [2026-09-26 00:29:35] stage=user.create req=- user=- model=-
- user_id=1 username=Carol

### [2026-09-26 00:29:35] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-09-26 00:29:35] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-09-26 00:29:35] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-09-26 00:29:58] stage=user.create req=- user=- model=-
- user_id=1 username=SkillUser

### [2026-09-26 00:29:58] stage=user.create req=- user=- model=-
- user_id=1 username=BUser

### [2026-09-26 00:29:58] stage=guard.block req=- user=- model=-
- kind=leak matched=打印\s*(你的)?\s*(system\s*)?prompt

### [2026-09-26 00:29:59] stage=rag.cache req=- user=- model=-
- cache_hit=miss user_scope=u:9

### [2026-09-26 00:29:59] stage=rag.cache req=- user=- model=-
- cache_hit=miss user_scope=u:9

### [2026-09-26 00:29:59] stage=rag.cache req=- user=- model=-
- cache_hit=answer user_scope=u:9

### [2026-09-26 00:29:59] stage=rag.cache req=- user=- model=-
- action=invalidate user_scope=u:9

### [2026-09-26 00:29:59] stage=rag.cache req=- user=- model=-
- cache_hit=miss user_scope=u:9

### [2026-09-26 00:29:59] stage=rag.cache req=- user=- model=-
- cache_hit=miss user_scope=u:9

### [2026-09-26 00:29:59] stage=rag.cache req=- user=- model=-
- cache_hit=miss user_scope=u:1

### [2026-09-26 00:29:59] stage=rag.cache req=- user=- model=-
- cache_hit=miss user_scope=u:1

### [2026-09-26 00:29:59] stage=rag.cache req=- user=- model=-
- cache_hit=answer user_scope=u:1

### [2026-09-26 00:29:59] stage=rag.cache req=- user=- model=-
- action=invalidate user_scope=u:1

### [2026-09-26 00:29:59] stage=rag.cache req=- user=- model=-
- cache_hit=miss user_scope=u:1

### [2026-09-26 00:29:59] stage=rag.retrieve req=- user=- model=-
- vector_hits=2 bm25_hits=1 fused=2 rerank=rrf rerank_top=2 gated=2 top_score=0.03278688524590164 query_preview=番茄

### [2026-09-26 00:29:59] stage=user.create req=- user=- model=-
- user_id=1 username=HistUser

### [2026-09-26 00:29:59] stage=user.create req=- user=- model=-
- user_id=2 username=Other

### [2026-09-26 00:30:35] stage=bootstrap.ok req=- user=- model=-
- streamlit=E:\Study\Programs\AI Agent Demo\.venv\Scripts\streamlit.exe venv=E:\Study\Programs\AI Agent Demo\.venv\Scripts\python.exe

### [2026-09-26 00:30:35] stage=bootstrap.ok req=- user=- model=-
- streamlit=E:\Study\Programs\AI Agent Demo\.venv\Scripts\streamlit.exe venv=E:\Study\Programs\AI Agent Demo\.venv\Scripts\python.exe

### [2026-09-26 00:30:35] stage=bootstrap.ok req=- user=- model=-
- streamlit=E:\Study\Programs\AI Agent Demo\.venv\Scripts\streamlit.exe venv=E:\Study\Programs\AI Agent Demo\.venv\Scripts\python.exe

### [2026-09-26 00:30:45] stage=user.create req=- user=- model=-
- user_id=1 username=PinUser

### [2026-09-26 00:30:45] stage=user.create req=- user=- model=-
- user_id=1 username=KwUser

### [2026-09-26 00:30:45] stage=user.create req=- user=- model=-
- user_id=1 username=OverallUser

### [2026-09-26 00:30:46] stage=user.create req=- user=- model=-
- user_id=1 username=OverallUser

### [2026-09-26 00:31:09] stage=rag.cache req=- user=- model=-
- cache_hit=answer user_scope=u:1

### [2026-09-26 00:31:09] stage=rag.cache req=- user=- model=-
- action=invalidate user_scope=u:1

### [2026-09-26 00:31:09] stage=rag.cache req=- user=- model=-
- cache_hit=miss user_scope=u:1

### [2026-09-26 00:31:09] stage=guard.block req=- user=- model=-
- kind=leak matched=完整系统提示词

### [2026-09-26 00:31:09] stage=rag.retrieve req=- user=- model=-
- vector_hits=8 bm25_hits=8 fused=0 rerank=skipped rerank_top=0 gated=0 top_score=0.0 best_vector=0.4439884207235894 best_bm25=5.205306058801778 weak_gate=True query_preview=完全不存在的星座飞船燃料配方XYZ-999

### [2026-09-26 00:31:09] stage=rag.retrieve req=- user=- model=-
- status=empty query_preview=完全不存在的星座飞船燃料配方XYZ-999 vector_hits=8 bm25_hits=8 fused=0 rerank=skipped rerank_top=0 gated=0 top_score=0.0 best_vector=0.4439884207235894 best_bm25=5.205306058801778 weak_gate=True

### [2026-09-26 00:31:09] stage=chat.start req=req_test_p0 user=u1 model=m1
- phase=0 probe=True

### [2026-09-26 00:31:09] stage=guard.block req=- user=- model=-
- kind=leak matched=输出\s*(你的|完整的)?\s*系统提示

### [2026-09-26 00:31:09] stage=guard.block req=- user=- model=-
- kind=ignore_remind matched=ignore\s+(all\s+)?(previous|prior|above)\s+instructions

### [2026-09-26 00:31:09] stage=guard.block req=- user=- model=-
- kind=leak matched=reveal\s+(your\s+)?(system\s+)?prompt

### [2026-09-26 00:31:10] stage=bootstrap.ok req=- user=- model=-
- streamlit=E:\Study\Programs\AI Agent Demo\.venv\Scripts\streamlit.exe venv=E:\Study\Programs\AI Agent Demo\.venv\Scripts\python.exe

### [2026-09-26 00:31:10] stage=bootstrap.ok req=- user=- model=-
- streamlit=E:\Study\Programs\AI Agent Demo\.venv\Scripts\streamlit.exe venv=E:\Study\Programs\AI Agent Demo\.venv\Scripts\python.exe

### [2026-09-26 00:31:10] stage=bootstrap.ok req=- user=- model=-
- streamlit=E:\Study\Programs\AI Agent Demo\.venv\Scripts\streamlit.exe venv=E:\Study\Programs\AI Agent Demo\.venv\Scripts\python.exe

### [2026-09-26 00:31:10] stage=user.create req=- user=- model=-
- user_id=1 username=Alice

### [2026-09-26 00:31:10] stage=user.create req=- user=- model=-
- user_id=2 username=Bob

### [2026-09-26 00:31:10] stage=user.switch req=- user=- model=-
- user_id=2 username=Bob

### [2026-09-26 00:31:10] stage=user.create req=- user=- model=-
- user_id=1 username=Carol

### [2026-09-26 00:31:10] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-09-26 00:31:10] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-09-26 00:31:10] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-09-26 00:31:33] stage=user.create req=- user=- model=-
- user_id=1 username=SkillUser

### [2026-09-26 00:31:33] stage=user.create req=- user=- model=-
- user_id=1 username=BUser

### [2026-09-26 00:31:33] stage=guard.block req=- user=- model=-
- kind=leak matched=打印\s*(你的)?\s*(system\s*)?prompt

### [2026-09-26 00:31:34] stage=rag.cache req=- user=- model=-
- cache_hit=miss user_scope=u:9

### [2026-09-26 00:31:34] stage=rag.cache req=- user=- model=-
- cache_hit=miss user_scope=u:9

### [2026-09-26 00:31:34] stage=rag.cache req=- user=- model=-
- cache_hit=answer user_scope=u:9

### [2026-09-26 00:31:34] stage=rag.cache req=- user=- model=-
- action=invalidate user_scope=u:9

### [2026-09-26 00:31:34] stage=rag.cache req=- user=- model=-
- cache_hit=miss user_scope=u:9

### [2026-09-26 00:31:34] stage=rag.cache req=- user=- model=-
- cache_hit=miss user_scope=u:9

### [2026-09-26 00:31:34] stage=rag.cache req=- user=- model=-
- cache_hit=miss user_scope=u:1

### [2026-09-26 00:31:34] stage=rag.cache req=- user=- model=-
- cache_hit=miss user_scope=u:1

### [2026-09-26 00:31:34] stage=rag.cache req=- user=- model=-
- cache_hit=answer user_scope=u:1

### [2026-09-26 00:31:34] stage=rag.cache req=- user=- model=-
- action=invalidate user_scope=u:1

### [2026-09-26 00:31:34] stage=rag.cache req=- user=- model=-
- cache_hit=miss user_scope=u:1

### [2026-09-26 00:31:34] stage=rag.retrieve req=- user=- model=-
- vector_hits=2 bm25_hits=1 fused=2 rerank=rrf rerank_top=2 gated=2 top_score=0.03278688524590164 query_preview=番茄

### [2026-09-26 00:31:35] stage=user.create req=- user=- model=-
- user_id=1 username=HistUser

### [2026-09-26 00:31:35] stage=user.create req=- user=- model=-
- user_id=2 username=Other

### [2026-10-03 11:35:47] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-10-03 11:35:47] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-10-03 11:35:47] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-10-03 11:36:10] stage=user.create req=- user=- model=-
- user_id=1 username=SkillUser

### [2026-10-03 11:36:11] stage=rag.cache req=- user=- model=-
- cache_hit=answer user_scope=u:1

### [2026-10-03 11:36:11] stage=rag.cache req=- user=- model=-
- action=invalidate user_scope=u:1

### [2026-10-03 11:36:11] stage=rag.cache req=- user=- model=-
- cache_hit=miss user_scope=u:1

### [2026-10-03 11:36:11] stage=rag.retrieve req=- user=- model=-
- vector_hits=2 bm25_hits=1 fused=2 rerank=rrf rerank_top=2 gated=2 top_score=0.03278688524590164 query_preview=番茄

### [2026-10-03 11:36:11] stage=rag.retrieve req=- user=- model=-
- vector_hits=1 bm25_hits=1 fused=1 rerank=rrf rerank_top=1 gated=1 top_score=0.03278688524590164 query_preview=会议纪要

### [2026-10-03 11:36:11] stage=rag.retrieve req=- user=- model=-
- vector_hits=1 bm25_hits=1 fused=0 rerank=skipped rerank_top=0 gated=0 top_score=0.0 best_vector=0.1 best_bm25=0.2 weak_gate=True vector_weak=True bm25_weak=True query_preview=星座飞船

### [2026-10-03 11:36:32] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-10-03 11:36:33] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-10-03 11:36:33] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-10-03 11:36:55] stage=user.create req=- user=- model=-
- user_id=1 username=SkillUser

### [2026-10-03 11:36:55] stage=rag.cache req=- user=- model=-
- cache_hit=answer user_scope=u:1

### [2026-10-03 11:36:55] stage=rag.cache req=- user=- model=-
- action=invalidate user_scope=u:1

### [2026-10-03 11:36:55] stage=rag.cache req=- user=- model=-
- cache_hit=miss user_scope=u:1

### [2026-10-03 11:36:55] stage=rag.retrieve req=- user=- model=-
- vector_hits=2 bm25_hits=1 fused=2 rerank=rrf rerank_top=2 gated=2 top_score=0.03278688524590164 query_preview=番茄

### [2026-10-03 11:36:55] stage=rag.retrieve req=- user=- model=-
- vector_hits=1 bm25_hits=1 fused=1 rerank=rrf rerank_top=1 gated=1 top_score=0.03278688524590164 query_preview=会议纪要

### [2026-10-03 11:36:55] stage=rag.retrieve req=- user=- model=-
- vector_hits=1 bm25_hits=1 fused=0 rerank=skipped rerank_top=0 gated=0 top_score=0.0 best_vector=0.1 best_bm25=0.2 weak_gate=True vector_weak=True bm25_weak=True query_preview=星座飞船

### [2026-10-03 11:36:55] stage=user.create req=- user=- model=-
- user_id=1 username=Alice

### [2026-10-03 11:36:55] stage=user.create req=- user=- model=-
- user_id=2 username=Bob

### [2026-10-03 11:36:55] stage=user.switch req=- user=- model=-
- user_id=2 username=Bob

### [2026-10-03 11:36:55] stage=user.create req=- user=- model=-
- user_id=1 username=Carol

### [2026-10-03 11:36:56] stage=user.create req=- user=- model=-
- user_id=1 username=BUser

### [2026-10-03 11:36:56] stage=guard.block req=- user=- model=-
- kind=leak matched=打印\s*(你的)?\s*(system\s*)?prompt

### [2026-10-03 11:37:01] stage=user.create req=- user=- model=-
- user_id=1 username=PinUser

### [2026-10-03 11:37:01] stage=user.create req=- user=- model=-
- user_id=1 username=KwUser

### [2026-10-03 11:37:01] stage=user.create req=- user=- model=-
- user_id=1 username=OverallUser

### [2026-10-03 11:37:03] stage=user.create req=- user=- model=-
- user_id=1 username=OverallUser

### [2026-10-03 11:37:26] stage=rag.cache req=- user=- model=-
- cache_hit=answer user_scope=u:1

### [2026-10-03 11:37:26] stage=rag.cache req=- user=- model=-
- action=invalidate user_scope=u:1

### [2026-10-03 11:37:26] stage=rag.cache req=- user=- model=-
- cache_hit=miss user_scope=u:1

### [2026-10-03 11:37:26] stage=guard.block req=- user=- model=-
- kind=leak matched=完整系统提示词

### [2026-10-03 11:37:28] stage=rag.retrieve req=- user=- model=-
- vector_hits=8 bm25_hits=8 fused=8 rerank=rrf rerank_top=5 gated=5 top_score=0.032018442622950824 query_preview=完全不存在的星座飞船燃料配方XYZ-999

### [2026-10-03 11:37:28] stage=chat.start req=req_test_p0 user=u1 model=m1
- phase=0 probe=True

### [2026-10-03 11:37:28] stage=guard.block req=- user=- model=-
- kind=leak matched=输出\s*(你的|完整的)?\s*系统提示

### [2026-10-03 11:37:28] stage=guard.block req=- user=- model=-
- kind=ignore_remind matched=ignore\s+(all\s+)?(previous|prior|above)\s+instructions

### [2026-10-03 11:37:28] stage=guard.block req=- user=- model=-
- kind=leak matched=reveal\s+(your\s+)?(system\s+)?prompt

### [2026-10-03 11:37:28] stage=bootstrap.ok req=- user=- model=-
- streamlit=E:\Study\Programs\AI Agent Demo\.venv\Scripts\streamlit.exe venv=E:\Study\Programs\AI Agent Demo\.venv\Scripts\python.exe

### [2026-10-03 11:37:28] stage=bootstrap.ok req=- user=- model=-
- streamlit=E:\Study\Programs\AI Agent Demo\.venv\Scripts\streamlit.exe venv=E:\Study\Programs\AI Agent Demo\.venv\Scripts\python.exe

### [2026-10-03 11:37:28] stage=bootstrap.ok req=- user=- model=-
- streamlit=E:\Study\Programs\AI Agent Demo\.venv\Scripts\streamlit.exe venv=E:\Study\Programs\AI Agent Demo\.venv\Scripts\python.exe

### [2026-10-03 11:37:28] stage=user.create req=- user=- model=-
- user_id=1 username=Alice

### [2026-10-03 11:37:28] stage=user.create req=- user=- model=-
- user_id=2 username=Bob

### [2026-10-03 11:37:28] stage=user.switch req=- user=- model=-
- user_id=2 username=Bob

### [2026-10-03 11:37:28] stage=user.create req=- user=- model=-
- user_id=1 username=Carol

### [2026-10-03 11:37:29] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-10-03 11:37:29] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-10-03 11:37:29] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-10-03 11:37:52] stage=user.create req=- user=- model=-
- user_id=1 username=SkillUser

### [2026-10-03 11:37:53] stage=user.create req=- user=- model=-
- user_id=1 username=BUser

### [2026-10-03 11:37:53] stage=guard.block req=- user=- model=-
- kind=leak matched=打印\s*(你的)?\s*(system\s*)?prompt

### [2026-10-03 11:37:55] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-03 11:37:55] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:9

### [2026-10-03 11:37:55] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:9

### [2026-10-03 11:37:55] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-03 11:37:55] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=answer user_scope=u:9

### [2026-10-03 11:37:55] stage=rag.cache req=- user=- model=qwen_turbo
- action=invalidate user_scope=u:9

### [2026-10-03 11:37:55] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-03 11:37:55] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:9

### [2026-10-03 11:37:55] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:9

### [2026-10-03 11:37:55] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-03 11:37:55] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:1

### [2026-10-03 11:37:55] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:1

### [2026-10-03 11:37:55] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=answer user_scope=u:1

### [2026-10-03 11:37:55] stage=rag.cache req=- user=- model=qwen_turbo
- action=invalidate user_scope=u:1

### [2026-10-03 11:37:55] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:1

### [2026-10-03 11:37:55] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=2 bm25_hits=1 fused=2 rerank=rrf rerank_top=2 gated=2 top_score=0.03278688524590164 query_preview=番茄

### [2026-10-03 11:37:55] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=1 bm25_hits=1 fused=1 rerank=rrf rerank_top=1 gated=1 top_score=0.03278688524590164 query_preview=会议纪要

### [2026-10-03 11:37:55] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=1 bm25_hits=1 fused=0 rerank=skipped rerank_top=0 gated=0 top_score=0.0 best_vector=0.1 best_bm25=0.2 weak_gate=True vector_weak=True bm25_weak=True query_preview=星座飞船

### [2026-10-03 11:37:55] stage=user.create req=- user=- model=qwen_turbo
- user_id=1 username=HistUser

### [2026-10-03 11:37:55] stage=user.create req=- user=- model=qwen_turbo
- user_id=2 username=Other

### [2026-10-03 11:38:23] stage=user.create req=- user=- model=-
- user_id=1 username=PinUser

### [2026-10-03 11:38:23] stage=user.create req=- user=- model=-
- user_id=1 username=KwUser

### [2026-10-03 11:38:23] stage=user.create req=- user=- model=-
- user_id=1 username=OverallUser

### [2026-10-03 11:38:25] stage=user.create req=- user=- model=-
- user_id=1 username=OverallUser

### [2026-10-03 11:38:48] stage=rag.cache req=- user=- model=-
- cache_hit=answer user_scope=u:1

### [2026-10-03 11:38:48] stage=rag.cache req=- user=- model=-
- action=invalidate user_scope=u:1

### [2026-10-03 11:38:48] stage=rag.cache req=- user=- model=-
- cache_hit=miss user_scope=u:1

### [2026-10-03 11:38:48] stage=guard.block req=- user=- model=-
- kind=leak matched=完整系统提示词

### [2026-10-03 11:38:49] stage=rag.retrieve req=- user=- model=-
- vector_hits=8 bm25_hits=8 fused=8 rerank=rrf rerank_top=5 gated=5 top_score=0.032018442622950824 query_preview=完全不存在的星座飞船燃料配方XYZ-999

### [2026-10-03 11:38:49] stage=chat.start req=req_test_p0 user=u1 model=m1
- phase=0 probe=True

### [2026-10-03 11:38:49] stage=guard.block req=- user=- model=-
- kind=leak matched=输出\s*(你的|完整的)?\s*系统提示

### [2026-10-03 11:38:49] stage=guard.block req=- user=- model=-
- kind=ignore_remind matched=ignore\s+(all\s+)?(previous|prior|above)\s+instructions

### [2026-10-03 11:38:49] stage=guard.block req=- user=- model=-
- kind=leak matched=reveal\s+(your\s+)?(system\s+)?prompt

### [2026-10-03 11:38:49] stage=bootstrap.ok req=- user=- model=-
- streamlit=E:\Study\Programs\AI Agent Demo\.venv\Scripts\streamlit.exe venv=E:\Study\Programs\AI Agent Demo\.venv\Scripts\python.exe

### [2026-10-03 11:38:49] stage=bootstrap.ok req=- user=- model=-
- streamlit=E:\Study\Programs\AI Agent Demo\.venv\Scripts\streamlit.exe venv=E:\Study\Programs\AI Agent Demo\.venv\Scripts\python.exe

### [2026-10-03 11:38:49] stage=bootstrap.ok req=- user=- model=-
- streamlit=E:\Study\Programs\AI Agent Demo\.venv\Scripts\streamlit.exe venv=E:\Study\Programs\AI Agent Demo\.venv\Scripts\python.exe

### [2026-10-03 11:38:50] stage=user.create req=- user=- model=-
- user_id=1 username=Alice

### [2026-10-03 11:38:50] stage=user.create req=- user=- model=-
- user_id=2 username=Bob

### [2026-10-03 11:38:50] stage=user.switch req=- user=- model=-
- user_id=2 username=Bob

### [2026-10-03 11:38:50] stage=user.create req=- user=- model=-
- user_id=1 username=Carol

### [2026-10-03 11:38:50] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-10-03 11:38:50] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-10-03 11:38:50] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-10-03 11:39:13] stage=user.create req=- user=- model=-
- user_id=1 username=SkillUser

### [2026-10-03 11:39:13] stage=user.create req=- user=- model=-
- user_id=1 username=BUser

### [2026-10-03 11:39:13] stage=guard.block req=- user=- model=-
- kind=leak matched=打印\s*(你的)?\s*(system\s*)?prompt

### [2026-10-03 11:39:15] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-03 11:39:15] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:9

### [2026-10-03 11:39:15] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:9

### [2026-10-03 11:39:15] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-03 11:39:15] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=answer user_scope=u:9

### [2026-10-03 11:39:15] stage=rag.cache req=- user=- model=qwen_turbo
- action=invalidate user_scope=u:9

### [2026-10-03 11:39:15] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-03 11:39:15] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:9

### [2026-10-03 11:39:15] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:9

### [2026-10-03 11:39:15] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-03 11:39:15] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:1

### [2026-10-03 11:39:15] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:1

### [2026-10-03 11:39:15] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=answer user_scope=u:1

### [2026-10-03 11:39:15] stage=rag.cache req=- user=- model=qwen_turbo
- action=invalidate user_scope=u:1

### [2026-10-03 11:39:15] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:1

### [2026-10-03 11:39:15] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=2 bm25_hits=1 fused=2 rerank=rrf rerank_top=2 gated=2 top_score=0.03278688524590164 query_preview=番茄

### [2026-10-03 11:39:15] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=1 bm25_hits=1 fused=1 rerank=rrf rerank_top=1 gated=1 top_score=0.03278688524590164 query_preview=会议纪要

### [2026-10-03 11:39:15] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=1 bm25_hits=1 fused=0 rerank=skipped rerank_top=0 gated=0 top_score=0.0 best_vector=0.1 best_bm25=0.2 weak_gate=True vector_weak=True bm25_weak=True query_preview=星座飞船

### [2026-10-03 11:39:15] stage=user.create req=- user=- model=qwen_turbo
- user_id=1 username=HistUser

### [2026-10-03 11:39:15] stage=user.create req=- user=- model=qwen_turbo
- user_id=2 username=Other

### [2026-10-03 11:39:41] stage=rag.retrieve req=- user=- model=-
- vector_hits=1 bm25_hits=1 fused=1 rerank=rrf rerank_top=1 gated=1 top_score=0.03278688524590164 query_preview=会议纪要

### [2026-10-03 11:39:41] stage=rag.retrieve req=- user=- model=-
- vector_hits=1 bm25_hits=1 fused=0 rerank=skipped rerank_top=0 gated=0 top_score=0.0 best_vector=0.1 best_bm25=0.2 weak_gate=True vector_weak=True bm25_weak=True query_preview=星座飞船

### [2026-10-03 11:39:43] stage=user.create req=- user=- model=-
- user_id=1 username=PinUser

### [2026-10-03 11:39:43] stage=user.create req=- user=- model=-
- user_id=1 username=KwUser

### [2026-10-03 11:39:43] stage=user.create req=- user=- model=-
- user_id=1 username=OverallUser

### [2026-10-03 11:39:45] stage=user.create req=- user=- model=-
- user_id=1 username=OverallUser

### [2026-10-03 11:40:08] stage=rag.cache req=- user=- model=-
- cache_hit=answer user_scope=u:1

### [2026-10-03 11:40:08] stage=rag.cache req=- user=- model=-
- action=invalidate user_scope=u:1

### [2026-10-03 11:40:08] stage=rag.cache req=- user=- model=-
- cache_hit=miss user_scope=u:1

### [2026-10-03 11:40:08] stage=guard.block req=- user=- model=-
- kind=leak matched=完整系统提示词

### [2026-10-03 11:40:09] stage=rag.retrieve req=- user=- model=-
- vector_hits=8 bm25_hits=8 fused=8 rerank=rrf rerank_top=5 gated=5 top_score=0.032018442622950824 query_preview=完全不存在的星座飞船燃料配方XYZ-999

### [2026-10-03 11:40:09] stage=chat.start req=req_test_p0 user=u1 model=m1
- phase=0 probe=True

### [2026-10-03 11:40:09] stage=guard.block req=- user=- model=-
- kind=leak matched=输出\s*(你的|完整的)?\s*系统提示

### [2026-10-03 11:40:09] stage=guard.block req=- user=- model=-
- kind=ignore_remind matched=ignore\s+(all\s+)?(previous|prior|above)\s+instructions

### [2026-10-03 11:40:09] stage=guard.block req=- user=- model=-
- kind=leak matched=reveal\s+(your\s+)?(system\s+)?prompt

### [2026-10-03 11:40:09] stage=bootstrap.ok req=- user=- model=-
- streamlit=E:\Study\Programs\AI Agent Demo\.venv\Scripts\streamlit.exe venv=E:\Study\Programs\AI Agent Demo\.venv\Scripts\python.exe

### [2026-10-03 11:40:10] stage=bootstrap.ok req=- user=- model=-
- streamlit=E:\Study\Programs\AI Agent Demo\.venv\Scripts\streamlit.exe venv=E:\Study\Programs\AI Agent Demo\.venv\Scripts\python.exe

### [2026-10-03 11:40:10] stage=bootstrap.ok req=- user=- model=-
- streamlit=E:\Study\Programs\AI Agent Demo\.venv\Scripts\streamlit.exe venv=E:\Study\Programs\AI Agent Demo\.venv\Scripts\python.exe

### [2026-10-03 11:40:10] stage=user.create req=- user=- model=-
- user_id=1 username=Alice

### [2026-10-03 11:40:10] stage=user.create req=- user=- model=-
- user_id=2 username=Bob

### [2026-10-03 11:40:10] stage=user.switch req=- user=- model=-
- user_id=2 username=Bob

### [2026-10-03 11:40:10] stage=user.create req=- user=- model=-
- user_id=1 username=Carol

### [2026-10-03 11:40:10] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-10-03 11:40:10] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-10-03 11:40:10] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-10-03 11:40:33] stage=user.create req=- user=- model=-
- user_id=1 username=SkillUser

### [2026-10-03 11:40:33] stage=user.create req=- user=- model=-
- user_id=1 username=BUser

### [2026-10-03 11:40:33] stage=guard.block req=- user=- model=-
- kind=leak matched=打印\s*(你的)?\s*(system\s*)?prompt

### [2026-10-03 11:40:35] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-03 11:40:35] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:9

### [2026-10-03 11:40:35] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:9

### [2026-10-03 11:40:35] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-03 11:40:35] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=answer user_scope=u:9

### [2026-10-03 11:40:35] stage=rag.cache req=- user=- model=qwen_turbo
- action=invalidate user_scope=u:9

### [2026-10-03 11:40:35] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-03 11:40:35] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:9

### [2026-10-03 11:40:35] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:9

### [2026-10-03 11:40:35] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-03 11:40:35] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:1

### [2026-10-03 11:40:35] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:1

### [2026-10-03 11:40:35] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=answer user_scope=u:1

### [2026-10-03 11:40:35] stage=rag.cache req=- user=- model=qwen_turbo
- action=invalidate user_scope=u:1

### [2026-10-03 11:40:35] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:1

### [2026-10-03 11:40:35] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=2 bm25_hits=1 fused=2 rerank=rrf rerank_top=2 gated=2 top_score=0.03278688524590164 query_preview=番茄

### [2026-10-03 11:40:35] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=1 bm25_hits=1 fused=1 rerank=rrf rerank_top=1 gated=1 top_score=0.03278688524590164 query_preview=会议纪要

### [2026-10-03 11:40:35] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=1 bm25_hits=1 fused=0 rerank=skipped rerank_top=0 gated=0 top_score=0.0 best_vector=0.1 best_bm25=0.2 weak_gate=True vector_weak=True bm25_weak=True query_preview=星座飞船

### [2026-10-03 11:40:36] stage=user.create req=- user=- model=qwen_turbo
- user_id=1 username=HistUser

### [2026-10-03 11:40:36] stage=user.create req=- user=- model=qwen_turbo
- user_id=2 username=Other

### [2026-10-03 11:41:07] stage=rag.retrieve req=- user=- model=-
- vector_hits=1 bm25_hits=1 fused=1 rerank=rrf rerank_top=1 gated=1 top_score=0.03278688524590164 query_preview=会议纪要

### [2026-10-03 11:41:23] stage=p0.harden.verify req=- user=- model=-
- rounds=R1-R5 pytest_full=80passedx3 p0_tests=8passed api_no_key=503 api_bad_key=401 ssrf=blocked_loopback_metadata weak_gate=vector_and_bm25 set_skill=ok workspace=per_user_is_relative_to personal_path=data/personal/{uid} status=pass

### [2026-10-05 17:43:08] stage=bootstrap.ok req=- user=- model=-
- streamlit=E:\Study\Programs\AI Agent Demo\.venv\Scripts\streamlit.exe venv=E:\Study\Programs\AI Agent Demo\.venv\Scripts\python.exe

### [2026-10-05 17:43:16] stage=app.start req=- user=- model=-
- entry=streamlit page=app.py

### [2026-10-05 17:43:17] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-05 17:43:28] stage=app.start req=- user=- model=-
- entry=streamlit page=app.py

### [2026-10-05 17:43:29] stage=app.start req=- user=- model=-
- entry=streamlit page=app.py

### [2026-10-05 18:16:48] stage=user.create req=- user=- model=-
- user_id=1 username=PinUser

### [2026-10-05 18:16:48] stage=user.create req=- user=- model=-
- user_id=1 username=KwUser

### [2026-10-05 18:16:48] stage=user.create req=- user=- model=-
- user_id=1 username=OverallUser

### [2026-10-05 18:16:49] stage=user.create req=- user=- model=-
- user_id=1 username=OverallUser

### [2026-10-05 18:17:12] stage=rag.cache req=- user=- model=-
- cache_hit=answer user_scope=u:1

### [2026-10-05 18:17:12] stage=rag.cache req=- user=- model=-
- action=invalidate user_scope=u:1

### [2026-10-05 18:17:12] stage=rag.cache req=- user=- model=-
- cache_hit=miss user_scope=u:1

### [2026-10-05 18:17:12] stage=guard.block req=- user=- model=-
- kind=leak matched=完整系统提示词

### [2026-10-05 18:17:12] stage=rag.retrieve req=- user=- model=-
- vector_hits=8 bm25_hits=8 fused=8 rerank=rrf rerank_top=5 gated=5 top_score=0.032018442622950824 query_preview=完全不存在的星座飞船燃料配方XYZ-999

### [2026-10-05 18:17:13] stage=chat.start req=req_test_p0 user=u1 model=m1
- phase=0 probe=True

### [2026-10-05 18:17:13] stage=guard.block req=- user=- model=-
- kind=leak matched=输出\s*(你的|完整的)?\s*系统提示

### [2026-10-05 18:17:13] stage=guard.block req=- user=- model=-
- kind=ignore_remind matched=ignore\s+(all\s+)?(previous|prior|above)\s+instructions

### [2026-10-05 18:17:13] stage=guard.block req=- user=- model=-
- kind=leak matched=reveal\s+(your\s+)?(system\s+)?prompt

### [2026-10-05 18:17:13] stage=bootstrap.ok req=- user=- model=-
- streamlit=E:\Study\Programs\AI Agent Demo\.venv\Scripts\streamlit.exe venv=E:\Study\Programs\AI Agent Demo\.venv\Scripts\python.exe

### [2026-10-05 18:17:13] stage=bootstrap.ok req=- user=- model=-
- streamlit=E:\Study\Programs\AI Agent Demo\.venv\Scripts\streamlit.exe venv=E:\Study\Programs\AI Agent Demo\.venv\Scripts\python.exe

### [2026-10-05 18:17:13] stage=bootstrap.ok req=- user=- model=-
- streamlit=E:\Study\Programs\AI Agent Demo\.venv\Scripts\streamlit.exe venv=E:\Study\Programs\AI Agent Demo\.venv\Scripts\python.exe

### [2026-10-05 18:17:13] stage=user.create req=- user=- model=-
- user_id=1 username=Alice

### [2026-10-05 18:17:13] stage=user.create req=- user=- model=-
- user_id=2 username=Bob

### [2026-10-05 18:17:13] stage=user.switch req=- user=- model=-
- user_id=2 username=Bob

### [2026-10-05 18:17:13] stage=user.create req=- user=- model=-
- user_id=1 username=Carol

### [2026-10-05 18:17:13] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-10-05 18:17:13] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-10-05 18:17:13] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-10-05 18:17:36] stage=user.create req=- user=- model=-
- user_id=1 username=SkillUser

### [2026-10-05 18:17:36] stage=user.create req=- user=- model=-
- user_id=1 username=BUser

### [2026-10-05 18:17:36] stage=guard.block req=- user=- model=-
- kind=leak matched=打印\s*(你的)?\s*(system\s*)?prompt

### [2026-10-05 18:17:37] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-05 18:17:37] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:9

### [2026-10-05 18:17:37] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:9

### [2026-10-05 18:17:37] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-05 18:17:37] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=answer user_scope=u:9

### [2026-10-05 18:17:37] stage=rag.cache req=- user=- model=qwen_turbo
- action=invalidate user_scope=u:9

### [2026-10-05 18:17:37] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-05 18:17:37] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:9

### [2026-10-05 18:17:37] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:9

### [2026-10-05 18:17:37] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-05 18:17:37] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:1

### [2026-10-05 18:17:37] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:1

### [2026-10-05 18:17:37] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=answer user_scope=u:1

### [2026-10-05 18:17:37] stage=rag.cache req=- user=- model=qwen_turbo
- action=invalidate user_scope=u:1

### [2026-10-05 18:17:37] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:1

### [2026-10-05 18:17:37] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=2 bm25_hits=1 fused=2 rerank=rrf rerank_top=2 gated=2 top_score=0.03278688524590164 query_preview=番茄

### [2026-10-05 18:17:37] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=1 bm25_hits=1 fused=1 rerank=rrf rerank_top=1 gated=1 top_score=0.03278688524590164 query_preview=会议纪要

### [2026-10-05 18:17:37] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=1 bm25_hits=1 fused=0 rerank=skipped rerank_top=0 gated=0 top_score=0.0 best_vector=0.1 best_bm25=0.2 weak_gate=True vector_weak=True bm25_weak=True query_preview=星座飞船

### [2026-10-05 18:17:38] stage=user.create req=- user=- model=qwen_turbo
- user_id=1 username=HistUser

### [2026-10-05 18:17:38] stage=user.create req=- user=- model=qwen_turbo
- user_id=2 username=Other


### [2026-10-08 16:59:32] stage=docs.tech_stack_knowledge
- 文档：docs/TECH_STACK_KNOWLEDGE.md；按最新要求整理纯技术知识，去除逐项工具功能与项目业务流程。
- 范围：22 章、134 个小节；覆盖全部 requirements.txt 声明依赖、源码直接第三方导入与相关基础知识；扩展概念明确区分。
- 验证：章节顺序、22 个目录锚点、代码块闭合、依赖名称覆盖、README 入口及旧草稿移除检查通过；纯文档结构与覆盖核验，不代表模型质量、性能或外部服务验收。
- 改动：新增技术知识文档、README 链接和本记录；未修改业务代码，未执行真实模型或天气请求。

### [2026-10-26 18:09:03] stage=user.create req=- user=- model=-
- user_id=1 username=PinUser

### [2026-10-26 18:09:03] stage=user.create req=- user=- model=-
- user_id=1 username=KwUser

### [2026-10-26 18:09:03] stage=user.create req=- user=- model=-
- user_id=1 username=OverallUser

### [2026-10-26 18:09:05] stage=user.create req=- user=- model=-
- user_id=1 username=OverallUser

### [2026-10-26 18:09:28] stage=rag.cache req=- user=- model=-
- cache_hit=answer user_scope=u:1

### [2026-10-26 18:09:28] stage=rag.cache req=- user=- model=-
- action=invalidate user_scope=u:1

### [2026-10-26 18:09:28] stage=rag.cache req=- user=- model=-
- cache_hit=miss user_scope=u:1

### [2026-10-26 18:09:28] stage=guard.block req=- user=- model=-
- kind=leak matched=完整系统提示词

### [2026-10-26 18:09:30] stage=rag.retrieve req=- user=- model=-
- vector_hits=0 bm25_hits=0 fused=0 rerank=skipped rerank_top=0 gated=0 top_score=0.0 best_vector=0.0 best_bm25=0.0 weak_gate=True vector_weak=True bm25_weak=True query_preview=完全不存在的星座飞船燃料配方XYZ-999

### [2026-10-26 18:09:30] stage=rag.retrieve req=- user=- model=-
- status=empty query_preview=完全不存在的星座飞船燃料配方XYZ-999 vector_hits=0 bm25_hits=0 fused=0 rerank=skipped rerank_top=0 gated=0 top_score=0.0 best_vector=0.0 best_bm25=0.0 weak_gate=True vector_weak=True bm25_weak=True

### [2026-10-26 18:09:30] stage=chat.start req=req_test_p0 user=u1 model=m1
- phase=0 probe=True

### [2026-10-26 18:09:30] stage=guard.block req=- user=- model=-
- kind=leak matched=输出\s*(你的|完整的)?\s*系统提示

### [2026-10-26 18:09:30] stage=guard.block req=- user=- model=-
- kind=ignore_remind matched=ignore\s+(all\s+)?(previous|prior|above)\s+instructions

### [2026-10-26 18:09:30] stage=guard.block req=- user=- model=-
- kind=leak matched=reveal\s+(your\s+)?(system\s+)?prompt

### [2026-10-26 18:09:30] stage=bootstrap.ok req=- user=- model=-
- streamlit=E:\Study\Programs\AI Agent Demo\.venv\Scripts\streamlit.exe venv=E:\Study\Programs\AI Agent Demo\.venv\Scripts\python.exe

### [2026-10-26 18:09:30] stage=bootstrap.ok req=- user=- model=-
- streamlit=E:\Study\Programs\AI Agent Demo\.venv\Scripts\streamlit.exe venv=E:\Study\Programs\AI Agent Demo\.venv\Scripts\python.exe

### [2026-10-26 18:09:30] stage=bootstrap.ok req=- user=- model=-
- streamlit=E:\Study\Programs\AI Agent Demo\.venv\Scripts\streamlit.exe venv=E:\Study\Programs\AI Agent Demo\.venv\Scripts\python.exe

### [2026-10-26 18:09:30] stage=user.create req=- user=- model=-
- user_id=1 username=Alice

### [2026-10-26 18:09:30] stage=user.create req=- user=- model=-
- user_id=2 username=Bob

### [2026-10-26 18:09:30] stage=user.switch req=- user=- model=-
- user_id=2 username=Bob

### [2026-10-26 18:09:30] stage=user.create req=- user=- model=-
- user_id=1 username=Carol

### [2026-10-26 18:09:30] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-10-26 18:09:30] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-10-26 18:09:31] stage=user.create req=- user=- model=-
- user_id=1 username=ToolUser

### [2026-10-26 18:09:50] stage=user.create req=- user=- model=-
- user_id=1 username=SkillUser

### [2026-10-26 18:09:50] stage=user.create req=- user=- model=-
- user_id=1 username=BUser

### [2026-10-26 18:09:50] stage=guard.block req=- user=- model=-
- kind=leak matched=打印\s*(你的)?\s*(system\s*)?prompt

### [2026-10-26 18:09:52] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:09:52] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:9

### [2026-10-26 18:09:52] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:9

### [2026-10-26 18:09:52] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:09:52] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=answer user_scope=u:9

### [2026-10-26 18:09:52] stage=rag.cache req=- user=- model=qwen_turbo
- action=invalidate user_scope=u:9

### [2026-10-26 18:09:52] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:09:52] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:9

### [2026-10-26 18:09:52] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:9

### [2026-10-26 18:09:52] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:09:52] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:1

### [2026-10-26 18:09:52] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:1

### [2026-10-26 18:09:52] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=answer user_scope=u:1

### [2026-10-26 18:09:52] stage=rag.cache req=- user=- model=qwen_turbo
- action=invalidate user_scope=u:1

### [2026-10-26 18:09:52] stage=rag.cache req=- user=- model=qwen_turbo
- cache_hit=miss user_scope=u:1

### [2026-10-26 18:09:52] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=2 bm25_hits=1 fused=2 rerank=rrf rerank_top=2 gated=2 top_score=0.03278688524590164 query_preview=番茄

### [2026-10-26 18:09:52] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=1 bm25_hits=1 fused=1 rerank=rrf rerank_top=1 gated=1 top_score=0.03278688524590164 query_preview=会议纪要

### [2026-10-26 18:09:52] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=1 bm25_hits=1 fused=0 rerank=skipped rerank_top=0 gated=0 top_score=0.0 best_vector=0.1 best_bm25=0.2 weak_gate=True vector_weak=True bm25_weak=True query_preview=星座飞船

### [2026-10-26 18:09:53] stage=user.create req=- user=- model=qwen_turbo
- user_id=1 username=HistUser

### [2026-10-26 18:09:53] stage=user.create req=- user=- model=qwen_turbo
- user_id=2 username=Other

### [2026-10-26 18:31:19] stage=rag.cache req=- user=- model=-
- action=invalidate user_scope=u:anon

### [2026-10-26 18:31:39] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=5 gated=5 top_score=0.032266458495966696 query_preview=X1 报 HMS 0300-0100-0001-0003，说明文档列出的常见原因有哪些？

### [2026-10-26 18:31:39] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:31:40] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=5 gated=5 top_score=0.03278688524590164 query_preview=X1 系列热床最高允许温度是多少？

### [2026-10-26 18:31:40] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:31:42] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=5 gated=5 top_score=0.03278688524590164 query_preview=P1 系列热床最高许用温度是多少？

### [2026-10-26 18:31:42] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:31:43] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=30 rerank=rrf rerank_top=5 gated=5 top_score=0.03278688524590164 query_preview=A1 mini 的热床最高许用温度是多少？

### [2026-10-26 18:31:43] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:31:44] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=5 gated=5 top_score=0.03131881575727918 query_preview=热床设置温度超过上限时，打印机会做什么处理？

### [2026-10-26 18:31:44] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:31:45] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=28 rerank=rrf rerank_top=5 gated=5 top_score=0.032266458495966696 query_preview=“喷嘴温度异常，加热器可能短路”对应的 HMS 代码是什么？

### [2026-10-26 18:31:45] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:31:47] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=5 gated=5 top_score=0.03278688524590164 query_preview=喷嘴温度传感器可能开路时，文档建议先检查什么？

### [2026-10-26 18:31:47] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:31:48] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=5 gated=5 top_score=0.032266458495966696 query_preview=热床不升温且温度显示为 0 时，属于文档里的哪种情形？

### [2026-10-26 18:31:48] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:31:49] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=34 rerank=rrf rerank_top=5 gated=5 top_score=0.03177805800756621 query_preview=打印机检测不到 AMS 时，操作指导分哪几步？

### [2026-10-26 18:31:49] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:31:50] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=38 rerank=rrf rerank_top=5 gated=5 top_score=0.032266458495966696 query_preview=AMS 无法上电时，怎么确认是不是供电问题？

### [2026-10-26 18:31:50] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:32:25] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=5 gated=5 top_score=0.032266458495966696 query_preview=X1 报 HMS 0300-0100-0001-0003，说明文档列出的常见原因有哪些？

### [2026-10-26 18:32:25] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:32:28] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=5 gated=5 top_score=0.03278688524590164 query_preview=X1 系列热床最高允许温度是多少？

### [2026-10-26 18:32:28] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:32:30] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=5 gated=5 top_score=0.03278688524590164 query_preview=P1 系列热床最高许用温度是多少？

### [2026-10-26 18:32:30] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:32:33] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=30 rerank=rrf rerank_top=5 gated=5 top_score=0.03278688524590164 query_preview=A1 mini 的热床最高许用温度是多少？

### [2026-10-26 18:32:33] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:32:35] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=5 gated=5 top_score=0.03131881575727918 query_preview=热床设置温度超过上限时，打印机会做什么处理？

### [2026-10-26 18:32:35] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:32:39] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=28 rerank=rrf rerank_top=5 gated=5 top_score=0.032266458495966696 query_preview=“喷嘴温度异常，加热器可能短路”对应的 HMS 代码是什么？

### [2026-10-26 18:32:39] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:32:42] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=5 gated=5 top_score=0.03278688524590164 query_preview=喷嘴温度传感器可能开路时，文档建议先检查什么？

### [2026-10-26 18:32:42] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:32:45] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=5 gated=5 top_score=0.032266458495966696 query_preview=热床不升温且温度显示为 0 时，属于文档里的哪种情形？

### [2026-10-26 18:32:45] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:32:47] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=34 rerank=rrf rerank_top=5 gated=5 top_score=0.03177805800756621 query_preview=打印机检测不到 AMS 时，操作指导分哪几步？

### [2026-10-26 18:32:47] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:32:50] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=38 rerank=rrf rerank_top=5 gated=5 top_score=0.032266458495966696 query_preview=AMS 无法上电时，怎么确认是不是供电问题？

### [2026-10-26 18:32:50] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:37:53] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=5 gated=5 top_score=0.032266458495966696 query_preview=X1 报 HMS 0300-0100-0001-0003，说明文档列出的常见原因有哪些？

### [2026-10-26 18:38:00] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=5 gated=5 top_score=0.03278688524590164 query_preview=X1 系列热床最高允许温度是多少？

### [2026-10-26 18:38:06] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=5 gated=5 top_score=0.03278688524590164 query_preview=P1 系列热床最高许用温度是多少？

### [2026-10-26 18:38:11] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=30 rerank=rrf rerank_top=5 gated=5 top_score=0.03278688524590164 query_preview=A1 mini 的热床最高许用温度是多少？

### [2026-10-26 18:38:17] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=5 gated=5 top_score=0.03131881575727918 query_preview=热床设置温度超过上限时，打印机会做什么处理？

### [2026-10-26 18:38:22] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=28 rerank=rrf rerank_top=5 gated=5 top_score=0.032266458495966696 query_preview=“喷嘴温度异常，加热器可能短路”对应的 HMS 代码是什么？

### [2026-10-26 18:38:29] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=5 gated=5 top_score=0.03278688524590164 query_preview=喷嘴温度传感器可能开路时，文档建议先检查什么？

### [2026-10-26 18:38:39] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=5 gated=5 top_score=0.032266458495966696 query_preview=热床不升温且温度显示为 0 时，属于文档里的哪种情形？

### [2026-10-26 18:38:45] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=34 rerank=rrf rerank_top=5 gated=5 top_score=0.03177805800756621 query_preview=打印机检测不到 AMS 时，操作指导分哪几步？

### [2026-10-26 18:38:56] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=38 rerank=rrf rerank_top=5 gated=5 top_score=0.032266458495966696 query_preview=AMS 无法上电时，怎么确认是不是供电问题？

### [2026-10-26 18:42:19] stage=rag.cache req=- user=- model=-
- action=invalidate user_scope=u:anon

### [2026-10-26 18:42:26] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=X1 报 HMS 0300-0100-0001-0003，说明文档列出的常见原因有哪些？

### [2026-10-26 18:42:26] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:42:30] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=X1 系列热床最高允许温度是多少？

### [2026-10-26 18:42:30] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:42:32] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=P1 系列热床最高许用温度是多少？

### [2026-10-26 18:42:32] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:42:35] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=30 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=A1 mini 的热床最高许用温度是多少？

### [2026-10-26 18:42:35] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:42:38] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=热床设置温度超过上限时，打印机会做什么处理？

### [2026-10-26 18:42:38] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:42:41] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=30 rerank=rrf rerank_top=8 gated=8 top_score=0.032018442622950824 query_preview=“喷嘴温度异常，加热器可能短路”对应的 HMS 代码是什么？

### [2026-10-26 18:42:41] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:42:44] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.032018442622950824 query_preview=喷嘴温度传感器可能开路时，文档建议先检查什么？

### [2026-10-26 18:42:44] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:42:47] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.031754032258064516 query_preview=热床不升温且温度显示为 0 时，属于文档里的哪种情形？

### [2026-10-26 18:42:47] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:42:49] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.032018442622950824 query_preview=打印机检测不到 AMS 时，操作指导分哪几步？

### [2026-10-26 18:42:49] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:42:52] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=37 rerank=rrf rerank_top=8 gated=8 top_score=0.032266458495966696 query_preview=AMS 无法上电时，怎么确认是不是供电问题？

### [2026-10-26 18:42:52] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:43:10] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=X1 报 HMS 0300-0100-0001-0003，说明文档列出的常见原因有哪些？

### [2026-10-26 18:43:11] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.032018442622950824 query_preview=喷嘴温度传感器可能开路时，文档建议先检查什么？

### [2026-10-26 18:43:12] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.032018442622950824 query_preview=打印机检测不到 AMS 时，操作指导分哪几步？

### [2026-10-26 18:43:36] stage=rag.cache req=- user=- model=-
- action=invalidate user_scope=u:anon

### [2026-10-26 18:43:44] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.031754032258064516 query_preview=X1 报 HMS 0300-0100-0001-0003，说明文档列出的常见原因有哪些？

### [2026-10-26 18:43:44] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:43:47] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=34 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=X1 系列热床最高允许温度是多少？

### [2026-10-26 18:43:47] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:43:50] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=P1 系列热床最高许用温度是多少？

### [2026-10-26 18:43:50] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:43:53] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=A1 mini 的热床最高许用温度是多少？

### [2026-10-26 18:43:53] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:43:56] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=热床设置温度超过上限时，打印机会做什么处理？

### [2026-10-26 18:43:56] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:43:59] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=“喷嘴温度异常，加热器可能短路”对应的 HMS 代码是什么？

### [2026-10-26 18:43:59] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:44:02] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.032266458495966696 query_preview=喷嘴温度传感器可能开路时，文档建议先检查什么？

### [2026-10-26 18:44:02] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:44:05] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=热床不升温且温度显示为 0 时，属于文档里的哪种情形？

### [2026-10-26 18:44:05] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:44:08] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.032018442622950824 query_preview=打印机检测不到 AMS 时，操作指导分哪几步？

### [2026-10-26 18:44:08] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:44:13] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=34 rerank=rrf rerank_top=8 gated=8 top_score=0.032018442622950824 query_preview=AMS 无法上电时，怎么确认是不是供电问题？

### [2026-10-26 18:44:13] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:44:27] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.031754032258064516 query_preview=X1 报 HMS 0300-0100-0001-0003，说明文档列出的常见原因有哪些？

### [2026-10-26 18:44:28] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.032266458495966696 query_preview=喷嘴温度传感器可能开路时，文档建议先检查什么？

### [2026-10-26 18:44:29] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.032018442622950824 query_preview=打印机检测不到 AMS 时，操作指导分哪几步？

### [2026-10-26 18:45:14] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.031754032258064516 query_preview=X1 报 HMS 0300-0100-0001-0003，说明文档列出的常见原因有哪些？

### [2026-10-26 18:45:14] stage=rag.exact_code req=- user=- model=-
- code=0300-0100-0001-0003 hits=1

### [2026-10-26 18:45:14] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:45:18] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=34 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=X1 系列热床最高允许温度是多少？

### [2026-10-26 18:45:18] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:45:20] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=P1 系列热床最高许用温度是多少？

### [2026-10-26 18:45:20] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:45:23] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=A1 mini 的热床最高许用温度是多少？

### [2026-10-26 18:45:23] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:45:26] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=热床设置温度超过上限时，打印机会做什么处理？

### [2026-10-26 18:45:26] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:45:29] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=“喷嘴温度异常，加热器可能短路”对应的 HMS 代码是什么？

### [2026-10-26 18:45:29] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:45:32] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.032266458495966696 query_preview=喷嘴温度传感器可能开路时，文档建议先检查什么？

### [2026-10-26 18:45:32] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:45:35] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=热床不升温且温度显示为 0 时，属于文档里的哪种情形？

### [2026-10-26 18:45:35] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:45:38] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.032018442622950824 query_preview=打印机检测不到 AMS 时，操作指导分哪几步？

### [2026-10-26 18:45:38] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:45:42] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=34 rerank=rrf rerank_top=8 gated=8 top_score=0.032018442622950824 query_preview=AMS 无法上电时，怎么确认是不是供电问题？

### [2026-10-26 18:45:42] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 18:45:57] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.032266458495966696 query_preview=喷嘴温度传感器可能开路时，文档建议先检查什么？

### [2026-10-26 19:29:00] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.031754032258064516 query_preview=X1 报 HMS 0300-0100-0001-0003，说明文档列出的常见原因有哪些？

### [2026-10-26 19:29:00] stage=rag.exact_code req=- user=- model=-
- code=0300-0100-0001-0003 hits=1

### [2026-10-26 19:29:00] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 19:29:04] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=34 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=X1 系列热床最高允许温度是多少？

### [2026-10-26 19:29:07] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=P1 系列热床最高许用温度是多少？

### [2026-10-26 19:29:10] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=A1 mini 的热床最高许用温度是多少？

### [2026-10-26 19:29:13] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=热床设置温度超过上限时，打印机会做什么处理？

### [2026-10-26 19:29:16] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=“喷嘴温度异常，加热器可能短路”对应的 HMS 代码是什么？

### [2026-10-26 19:29:19] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.032266458495966696 query_preview=喷嘴温度传感器可能开路时，文档建议先检查什么？

### [2026-10-26 19:29:22] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=热床不升温且温度显示为 0 时，属于文档里的哪种情形？

### [2026-10-26 19:29:25] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.032018442622950824 query_preview=打印机检测不到 AMS 时，操作指导分哪几步？

### [2026-10-26 19:29:30] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=34 rerank=rrf rerank_top=8 gated=8 top_score=0.032018442622950824 query_preview=AMS 无法上电时，怎么确认是不是供电问题？

### [2026-10-26 19:29:33] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=35 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=AMS 一直进料退料循环，常见原因有哪些？

### [2026-10-26 19:29:36] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=34 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=AMS 指示灯的不同状态分别代表什么？

### [2026-10-26 19:29:40] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=打印机提示切刀卡住，为什么会这样、怎么处理？

### [2026-10-26 19:29:45] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=显示屏完全黑屏和“黑屏但背光闪烁”，处理方式一样吗？

### [2026-10-26 19:29:48] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=35 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=触摸屏功能失效，第一步检查什么？

### [2026-10-26 19:29:51] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=开机后屏幕无法正常启动，第一步做什么？

### [2026-10-26 19:29:54] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=36 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=X1 固件升级失败，文档列出的故障原因有哪些？

### [2026-10-26 19:29:57] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=28 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=挤出机堵塞后，维护指南的核心步骤是什么？

### [2026-10-26 19:29:59] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.032266458495966696 query_preview=喷嘴/热端堵塞有哪三种处理方法？

### [2026-10-26 19:30:03] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=清理热端裹头需要哪些工具，大概要多久？

### [2026-10-26 19:30:06] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.032018442622950824 query_preview=HMS 是什么的缩写，它负责什么？

### [2026-10-26 19:30:09] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=26 rerank=rrf rerank_top=8 gated=8 top_score=0.032266458495966696 query_preview=HMS 代码里 0300 这一段代表哪个部件？

### [2026-10-26 19:30:12] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=26 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=HMS 告警等级 0001、0002、0003 分别是什么？

### [2026-10-26 19:30:15] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=HMS 有哪些局限性？

### [2026-10-26 19:30:19] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=36 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=“无法拉回料线”文档列出的原因有哪几个？

### [2026-10-26 19:30:22] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=打印 PLA 翘边，除了涂胶还要调哪个参数？

### [2026-10-26 19:30:25] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=27 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=热床过温（0001-0003）和 AC 板故障（0001-000A）都指向热床温控，处理上怎么区分？

### [2026-10-26 19:30:29] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=喷嘴加热短路和喷嘴传感器开路，排查重点有什么不同？

### [2026-10-26 19:30:34] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=30 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=“打印机堵塞排查”和“喷嘴/热端堵塞”两篇分别解决什么问题？

### [2026-10-26 19:30:37] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=27 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=AMS 无法上电和检测不到 AMS，排查重点有何不同？

### [2026-10-26 19:30:40] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.032266458495966696 query_preview=屏幕黑屏时，怎么判断是屏幕问题还是电路板问题？

### [2026-10-26 19:30:44] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=Z 轴回中失败有哪两种原因，分别看哪篇？

### [2026-10-26 19:30:47] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=耗材断裂在料管里和在 AMS 内部，处理方式一样吗？

### [2026-10-26 19:30:50] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=热床不升温和热床过温，排查思路有什么不同？

### [2026-10-26 19:30:54] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=28 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=用户报 0300-0200-0001-0001，这个码属于哪个部件、该按什么顺序排查？

### [2026-10-26 19:30:54] stage=rag.exact_code req=- user=- model=qwen_turbo
- code=0300-0200-0001-0001 hits=1

### [2026-10-26 19:30:58] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=37 rerank=rrf rerank_top=8 gated=8 top_score=0.031544957774465976 query_preview=A1 报 0300-0100-0001-0008，处理方式和 X1 有什么不同？

### [2026-10-26 19:30:58] stage=rag.exact_code req=- user=- model=qwen_turbo
- code=0300-0100-0001-0008 hits=1

### [2026-10-26 19:31:01] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=打印 PETG 时冷却风扇有什么限制？

### [2026-10-26 19:31:05] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=35 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=为什么要确认 AMS 主板版本，怎么确认？

### [2026-10-26 19:31:09] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=25 rerank=rrf rerank_top=8 gated=8 top_score=0.03131881575727918 query_preview=升级失败后，怎么把日志交给客服？

### [2026-10-26 19:31:12] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=27 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=热床不升温时，怎么判断是热床本身还是 AC 板的问题？

### [2026-10-26 19:31:16] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=36 rerank=rrf rerank_top=8 gated=8 top_score=0.03125 query_preview=如何更换汽车轮胎？

### [2026-10-26 19:31:19] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=38 rerank=rrf rerank_top=8 gated=8 top_score=0.028371628371628373 query_preview=这台打印机的保修期是几年？

### [2026-10-26 19:31:21] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.03131881575727918 query_preview=Bambu Lab 公司是哪一年成立的？

### [2026-10-26 19:31:24] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=37 rerank=rrf rerank_top=8 gated=8 top_score=0.029957522915269395 query_preview=X1 的最大打印尺寸是多少？

### [2026-10-26 19:31:27] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=39 rerank=rrf rerank_top=8 gated=8 top_score=0.027799227799227798 query_preview=可以用洗衣机清洗打印件吗？

### [2026-10-26 19:31:30] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.03200204813108039 query_preview=3D 打印机喷嘴直径有几种规格？

### [2026-10-26 19:31:33] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=39 rerank=rrf rerank_top=8 gated=8 top_score=0.027222222222222224 query_preview=如何申请退款？

### [2026-10-26 19:31:36] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=35 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=Prusa 打印机的校准步骤是什么？

### [2026-10-26 19:31:39] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03177805800756621 query_preview=A1 mini 的屏幕怎么更换？

### [2026-10-26 19:31:41] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=34 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=2024 年的固件版本号是多少？

### [2026-10-26 19:32:30] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.031754032258064516 query_preview=X1 报 HMS 0300-0100-0001-0003，说明文档列出的常见原因有哪些？

### [2026-10-26 19:32:30] stage=rag.exact_code req=- user=- model=-
- code=0300-0100-0001-0003 hits=1

### [2026-10-26 19:32:30] stage=model.select req=- user=- model=qwen_turbo
- mode=auto model_id=qwen_turbo model_name=qwen-turbo

### [2026-10-26 19:32:33] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=34 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=X1 系列热床最高允许温度是多少？

### [2026-10-26 19:32:36] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=P1 系列热床最高许用温度是多少？

### [2026-10-26 19:32:39] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=A1 mini 的热床最高许用温度是多少？

### [2026-10-26 19:32:42] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=热床设置温度超过上限时，打印机会做什么处理？

### [2026-10-26 19:32:45] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=“喷嘴温度异常，加热器可能短路”对应的 HMS 代码是什么？

### [2026-10-26 19:32:48] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.032266458495966696 query_preview=喷嘴温度传感器可能开路时，文档建议先检查什么？

### [2026-10-26 19:32:51] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=热床不升温且温度显示为 0 时，属于文档里的哪种情形？

### [2026-10-26 19:32:54] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.032018442622950824 query_preview=打印机检测不到 AMS 时，操作指导分哪几步？

### [2026-10-26 19:32:59] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=34 rerank=rrf rerank_top=8 gated=8 top_score=0.032018442622950824 query_preview=AMS 无法上电时，怎么确认是不是供电问题？

### [2026-10-26 19:33:04] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=35 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=AMS 一直进料退料循环，常见原因有哪些？

### [2026-10-26 19:33:07] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=34 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=AMS 指示灯的不同状态分别代表什么？

### [2026-10-26 19:33:11] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=打印机提示切刀卡住，为什么会这样、怎么处理？

### [2026-10-26 19:33:17] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=显示屏完全黑屏和“黑屏但背光闪烁”，处理方式一样吗？

### [2026-10-26 19:33:21] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=35 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=触摸屏功能失效，第一步检查什么？

### [2026-10-26 19:33:24] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=开机后屏幕无法正常启动，第一步做什么？

### [2026-10-26 19:33:27] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=36 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=X1 固件升级失败，文档列出的故障原因有哪些？

### [2026-10-26 19:33:30] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=28 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=挤出机堵塞后，维护指南的核心步骤是什么？

### [2026-10-26 19:33:33] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.032266458495966696 query_preview=喷嘴/热端堵塞有哪三种处理方法？

### [2026-10-26 19:33:37] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=清理热端裹头需要哪些工具，大概要多久？

### [2026-10-26 19:33:41] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.032018442622950824 query_preview=HMS 是什么的缩写，它负责什么？

### [2026-10-26 19:33:44] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=26 rerank=rrf rerank_top=8 gated=8 top_score=0.032266458495966696 query_preview=HMS 代码里 0300 这一段代表哪个部件？

### [2026-10-26 19:33:47] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=26 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=HMS 告警等级 0001、0002、0003 分别是什么？

### [2026-10-26 19:33:50] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=HMS 有哪些局限性？

### [2026-10-26 19:33:53] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=36 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=“无法拉回料线”文档列出的原因有哪几个？

### [2026-10-26 19:33:56] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=打印 PLA 翘边，除了涂胶还要调哪个参数？

### [2026-10-26 19:33:59] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=27 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=热床过温（0001-0003）和 AC 板故障（0001-000A）都指向热床温控，处理上怎么区分？

### [2026-10-26 19:34:04] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=喷嘴加热短路和喷嘴传感器开路，排查重点有什么不同？

### [2026-10-26 19:34:09] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=30 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=“打印机堵塞排查”和“喷嘴/热端堵塞”两篇分别解决什么问题？

### [2026-10-26 19:34:14] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=27 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=AMS 无法上电和检测不到 AMS，排查重点有何不同？

### [2026-10-26 19:34:19] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.032266458495966696 query_preview=屏幕黑屏时，怎么判断是屏幕问题还是电路板问题？

### [2026-10-26 19:34:23] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=Z 轴回中失败有哪两种原因，分别看哪篇？

### [2026-10-26 19:34:27] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=耗材断裂在料管里和在 AMS 内部，处理方式一样吗？

### [2026-10-26 19:34:30] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=热床不升温和热床过温，排查思路有什么不同？

### [2026-10-26 19:34:36] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=28 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=用户报 0300-0200-0001-0001，这个码属于哪个部件、该按什么顺序排查？

### [2026-10-26 19:34:36] stage=rag.exact_code req=- user=- model=qwen_turbo
- code=0300-0200-0001-0001 hits=1

### [2026-10-26 19:34:39] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=37 rerank=rrf rerank_top=8 gated=8 top_score=0.031544957774465976 query_preview=A1 报 0300-0100-0001-0008，处理方式和 X1 有什么不同？

### [2026-10-26 19:34:39] stage=rag.exact_code req=- user=- model=qwen_turbo
- code=0300-0100-0001-0008 hits=1

### [2026-10-26 19:34:45] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=打印 PETG 时冷却风扇有什么限制？

### [2026-10-26 19:34:48] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=35 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=为什么要确认 AMS 主板版本，怎么确认？

### [2026-10-26 19:34:53] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=25 rerank=rrf rerank_top=8 gated=8 top_score=0.03131881575727918 query_preview=升级失败后，怎么把日志交给客服？

### [2026-10-26 19:34:57] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=27 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=热床不升温时，怎么判断是热床本身还是 AC 板的问题？

### [2026-10-26 19:35:02] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=36 rerank=rrf rerank_top=8 gated=8 top_score=0.03125 query_preview=如何更换汽车轮胎？

### [2026-10-26 19:35:05] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=38 rerank=rrf rerank_top=8 gated=8 top_score=0.028371628371628373 query_preview=这台打印机的保修期是几年？

### [2026-10-26 19:35:08] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.03131881575727918 query_preview=Bambu Lab 公司是哪一年成立的？

### [2026-10-26 19:35:10] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=37 rerank=rrf rerank_top=8 gated=8 top_score=0.029957522915269395 query_preview=X1 的最大打印尺寸是多少？

### [2026-10-26 19:35:13] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=39 rerank=rrf rerank_top=8 gated=8 top_score=0.027799227799227798 query_preview=可以用洗衣机清洗打印件吗？

### [2026-10-26 19:35:16] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.03200204813108039 query_preview=3D 打印机喷嘴直径有几种规格？

### [2026-10-26 19:35:20] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=39 rerank=rrf rerank_top=8 gated=8 top_score=0.027222222222222224 query_preview=如何申请退款？

### [2026-10-26 19:35:23] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=35 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=Prusa 打印机的校准步骤是什么？

### [2026-10-26 19:35:27] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03177805800756621 query_preview=A1 mini 的屏幕怎么更换？

### [2026-10-26 19:35:30] stage=rag.retrieve req=- user=- model=qwen_turbo
- vector_hits=20 bm25_hits=20 fused=34 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=2024 年的固件版本号是多少？

### [2026-10-28 14:28:45] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:28:45] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:29:33] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:29:42] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.031754032258064516 query_preview=X1 报 HMS 0300-0100-0001-0003，说明文档列出的常见原因有哪些？

### [2026-10-28 14:29:42] stage=rag.exact_code req=- user=- model=-
- code=0300-0100-0001-0003 hits=1

### [2026-10-28 14:29:43] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:29:48] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=34 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=X1 系列热床最高允许温度是多少？

### [2026-10-28 14:29:48] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:29:52] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=P1 系列热床最高许用温度是多少？

### [2026-10-28 14:29:52] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:29:56] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=A1 mini 的热床最高许用温度是多少？

### [2026-10-28 14:29:56] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:30:01] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=热床设置温度超过上限时，打印机会做什么处理？

### [2026-10-28 14:30:01] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:30:07] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=“喷嘴温度异常，加热器可能短路”对应的 HMS 代码是什么？

### [2026-10-28 14:30:07] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:30:16] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.032266458495966696 query_preview=喷嘴温度传感器可能开路时，文档建议先检查什么？

### [2026-10-28 14:30:16] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:30:52] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=热床不升温且温度显示为 0 时，属于文档里的哪种情形？

### [2026-10-28 14:30:52] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:31:13] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.032018442622950824 query_preview=打印机检测不到 AMS 时，操作指导分哪几步？

### [2026-10-28 14:31:13] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:31:59] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=34 rerank=rrf rerank_top=8 gated=8 top_score=0.032018442622950824 query_preview=AMS 无法上电时，怎么确认是不是供电问题？

### [2026-10-28 14:31:59] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:32:13] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=35 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=AMS 一直进料退料循环，常见原因有哪些？

### [2026-10-28 14:32:13] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:32:27] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=34 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=AMS 指示灯的不同状态分别代表什么？

### [2026-10-28 14:32:27] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:32:37] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=打印机提示切刀卡住，为什么会这样、怎么处理？

### [2026-10-28 14:32:37] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:33:15] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=显示屏完全黑屏和“黑屏但背光闪烁”，处理方式一样吗？

### [2026-10-28 14:33:15] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:34:07] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=35 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=触摸屏功能失效，第一步检查什么？

### [2026-10-28 14:34:07] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:34:22] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=开机后屏幕无法正常启动，第一步做什么？

### [2026-10-28 14:34:22] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:34:36] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=36 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=X1 固件升级失败，文档列出的故障原因有哪些？

### [2026-10-28 14:34:36] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:34:45] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=28 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=挤出机堵塞后，维护指南的核心步骤是什么？

### [2026-10-28 14:34:45] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:35:00] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.032266458495966696 query_preview=喷嘴/热端堵塞有哪三种处理方法？

### [2026-10-28 14:35:00] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:35:22] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=清理热端裹头需要哪些工具，大概要多久？

### [2026-10-28 14:35:22] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:35:56] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.032018442622950824 query_preview=HMS 是什么的缩写，它负责什么？

### [2026-10-28 14:35:56] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:36:04] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=26 rerank=rrf rerank_top=8 gated=8 top_score=0.032266458495966696 query_preview=HMS 代码里 0300 这一段代表哪个部件？

### [2026-10-28 14:36:04] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:36:20] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=26 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=HMS 告警等级 0001、0002、0003 分别是什么？

### [2026-10-28 14:36:20] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:36:27] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=HMS 有哪些局限性？

### [2026-10-28 14:36:27] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:36:33] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=36 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=“无法拉回料线”文档列出的原因有哪几个？

### [2026-10-28 14:36:33] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:36:37] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=打印 PLA 翘边，除了涂胶还要调哪个参数？

### [2026-10-28 14:36:37] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:36:42] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=27 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=热床过温（0001-0003）和 AC 板故障（0001-000A）都指向热床温控，处理上怎么区分？

### [2026-10-28 14:36:42] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:37:05] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=喷嘴加热短路和喷嘴传感器开路，排查重点有什么不同？

### [2026-10-28 14:37:05] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:38:33] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=30 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=“打印机堵塞排查”和“喷嘴/热端堵塞”两篇分别解决什么问题？

### [2026-10-28 14:38:33] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:38:52] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=27 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=AMS 无法上电和检测不到 AMS，排查重点有何不同？

### [2026-10-28 14:38:52] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:39:40] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.032266458495966696 query_preview=屏幕黑屏时，怎么判断是屏幕问题还是电路板问题？

### [2026-10-28 14:39:40] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:39:47] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:40:16] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:40:46] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.031754032258064516 query_preview=X1 报 HMS 0300-0100-0001-0003，说明文档列出的常见原因有哪些？

### [2026-10-28 14:40:46] stage=rag.exact_code req=- user=- model=-
- code=0300-0100-0001-0003 hits=1

### [2026-10-28 14:40:46] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:40:50] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=34 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=X1 系列热床最高允许温度是多少？

### [2026-10-28 14:40:50] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:40:54] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=P1 系列热床最高许用温度是多少？

### [2026-10-28 14:40:54] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:40:57] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=A1 mini 的热床最高许用温度是多少？

### [2026-10-28 14:40:57] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:41:00] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=热床设置温度超过上限时，打印机会做什么处理？

### [2026-10-28 14:41:00] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:41:12] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.031754032258064516 query_preview=X1 报 HMS 0300-0100-0001-0003，说明文档列出的常见原因有哪些？

### [2026-10-28 14:41:12] stage=rag.exact_code req=- user=- model=-
- code=0300-0100-0001-0003 hits=1

### [2026-10-28 14:41:12] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:41:16] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=34 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=X1 系列热床最高允许温度是多少？

### [2026-10-28 14:41:16] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:41:19] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=P1 系列热床最高许用温度是多少？

### [2026-10-28 14:41:19] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:41:22] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=A1 mini 的热床最高许用温度是多少？

### [2026-10-28 14:41:22] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:41:25] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=热床设置温度超过上限时，打印机会做什么处理？

### [2026-10-28 14:41:25] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:41:28] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=“喷嘴温度异常，加热器可能短路”对应的 HMS 代码是什么？

### [2026-10-28 14:41:28] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:41:30] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.032266458495966696 query_preview=喷嘴温度传感器可能开路时，文档建议先检查什么？

### [2026-10-28 14:41:30] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:41:36] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=热床不升温且温度显示为 0 时，属于文档里的哪种情形？

### [2026-10-28 14:41:36] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:41:40] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.032018442622950824 query_preview=打印机检测不到 AMS 时，操作指导分哪几步？

### [2026-10-28 14:41:40] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:41:52] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=34 rerank=rrf rerank_top=8 gated=8 top_score=0.032018442622950824 query_preview=AMS 无法上电时，怎么确认是不是供电问题？

### [2026-10-28 14:41:52] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:41:58] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=35 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=AMS 一直进料退料循环，常见原因有哪些？

### [2026-10-28 14:41:58] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:42:02] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=34 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=AMS 指示灯的不同状态分别代表什么？

### [2026-10-28 14:42:02] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:42:08] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=打印机提示切刀卡住，为什么会这样、怎么处理？

### [2026-10-28 14:42:08] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:42:22] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=显示屏完全黑屏和“黑屏但背光闪烁”，处理方式一样吗？

### [2026-10-28 14:42:22] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:42:34] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=35 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=触摸屏功能失效，第一步检查什么？

### [2026-10-28 14:42:34] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:42:38] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=开机后屏幕无法正常启动，第一步做什么？

### [2026-10-28 14:42:38] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:42:41] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=36 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=X1 固件升级失败，文档列出的故障原因有哪些？

### [2026-10-28 14:42:41] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:42:48] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=28 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=挤出机堵塞后，维护指南的核心步骤是什么？

### [2026-10-28 14:42:48] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:42:54] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.032266458495966696 query_preview=喷嘴/热端堵塞有哪三种处理方法？

### [2026-10-28 14:42:54] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:42:59] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=清理热端裹头需要哪些工具，大概要多久？

### [2026-10-28 14:42:59] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:43:03] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.032018442622950824 query_preview=HMS 是什么的缩写，它负责什么？

### [2026-10-28 14:43:03] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:43:06] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=26 rerank=rrf rerank_top=8 gated=8 top_score=0.032266458495966696 query_preview=HMS 代码里 0300 这一段代表哪个部件？

### [2026-10-28 14:43:06] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:43:10] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=26 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=HMS 告警等级 0001、0002、0003 分别是什么？

### [2026-10-28 14:43:10] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:43:15] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=HMS 有哪些局限性？

### [2026-10-28 14:43:15] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:43:21] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=36 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=“无法拉回料线”文档列出的原因有哪几个？

### [2026-10-28 14:43:21] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:43:24] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=打印 PLA 翘边，除了涂胶还要调哪个参数？

### [2026-10-28 14:43:24] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:43:28] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=27 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=热床过温（0001-0003）和 AC 板故障（0001-000A）都指向热床温控，处理上怎么区分？

### [2026-10-28 14:43:28] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:43:43] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=喷嘴加热短路和喷嘴传感器开路，排查重点有什么不同？

### [2026-10-28 14:43:43] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:44:00] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=30 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=“打印机堵塞排查”和“喷嘴/热端堵塞”两篇分别解决什么问题？

### [2026-10-28 14:44:00] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:44:05] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=27 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=AMS 无法上电和检测不到 AMS，排查重点有何不同？

### [2026-10-28 14:44:05] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:44:15] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.032266458495966696 query_preview=屏幕黑屏时，怎么判断是屏幕问题还是电路板问题？

### [2026-10-28 14:44:15] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:44:25] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=Z 轴回中失败有哪两种原因，分别看哪篇？

### [2026-10-28 14:44:25] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:44:28] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=32 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=耗材断裂在料管里和在 AMS 内部，处理方式一样吗？

### [2026-10-28 14:44:28] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:44:36] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=热床不升温和热床过温，排查思路有什么不同？

### [2026-10-28 14:44:36] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:44:52] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=28 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=用户报 0300-0200-0001-0001，这个码属于哪个部件、该按什么顺序排查？

### [2026-10-28 14:44:52] stage=rag.exact_code req=- user=- model=qwen3_8_flash
- code=0300-0200-0001-0001 hits=1

### [2026-10-28 14:44:52] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:44:58] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=37 rerank=rrf rerank_top=8 gated=8 top_score=0.031544957774465976 query_preview=A1 报 0300-0100-0001-0008，处理方式和 X1 有什么不同？

### [2026-10-28 14:44:58] stage=rag.exact_code req=- user=- model=qwen3_8_flash
- code=0300-0100-0001-0008 hits=1

### [2026-10-28 14:44:58] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:45:09] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=打印 PETG 时冷却风扇有什么限制？

### [2026-10-28 14:45:09] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:45:13] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=35 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=为什么要确认 AMS 主板版本，怎么确认？

### [2026-10-28 14:45:13] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:45:21] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=25 rerank=rrf rerank_top=8 gated=8 top_score=0.03131881575727918 query_preview=升级失败后，怎么把日志交给客服？

### [2026-10-28 14:45:21] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:45:26] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=27 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=热床不升温时，怎么判断是热床本身还是 AC 板的问题？

### [2026-10-28 14:45:26] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:45:36] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=36 rerank=rrf rerank_top=8 gated=8 top_score=0.03125 query_preview=如何更换汽车轮胎？

### [2026-10-28 14:45:36] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:45:38] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=38 rerank=rrf rerank_top=8 gated=8 top_score=0.028371628371628373 query_preview=这台打印机的保修期是几年？

### [2026-10-28 14:45:38] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:45:40] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=31 rerank=rrf rerank_top=8 gated=8 top_score=0.03131881575727918 query_preview=Bambu Lab 公司是哪一年成立的？

### [2026-10-28 14:45:40] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:45:44] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=37 rerank=rrf rerank_top=8 gated=8 top_score=0.029957522915269395 query_preview=X1 的最大打印尺寸是多少？

### [2026-10-28 14:45:44] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:45:48] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=39 rerank=rrf rerank_top=8 gated=8 top_score=0.027799227799227798 query_preview=可以用洗衣机清洗打印件吗？

### [2026-10-28 14:45:48] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:45:51] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=29 rerank=rrf rerank_top=8 gated=8 top_score=0.03200204813108039 query_preview=3D 打印机喷嘴直径有几种规格？

### [2026-10-28 14:45:51] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:45:56] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=39 rerank=rrf rerank_top=8 gated=8 top_score=0.027222222222222224 query_preview=如何申请退款？

### [2026-10-28 14:45:56] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:45:59] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=35 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=Prusa 打印机的校准步骤是什么？

### [2026-10-28 14:45:59] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:46:03] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=33 rerank=rrf rerank_top=8 gated=8 top_score=0.03177805800756621 query_preview=A1 mini 的屏幕怎么更换？

### [2026-10-28 14:46:03] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:46:07] stage=rag.retrieve req=- user=- model=qwen3_8_flash
- vector_hits=20 bm25_hits=20 fused=34 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=2024 年的固件版本号是多少？

### [2026-10-28 14:46:07] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 14:46:25] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=38 rerank=rrf rerank_top=8 gated=8 top_score=0.03252247488101534 query_preview=X1 打印机的整机重量是多少？

### [2026-10-28 14:46:26] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 15:08:13] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=34 rerank=rrf rerank_top=8 gated=8 top_score=0.03278688524590164 query_preview=X1 系列热床最高允许温度是多少？

### [2026-10-28 15:08:13] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash

### [2026-10-28 15:11:50] stage=rag.retrieve req=- user=- model=-
- vector_hits=20 bm25_hits=20 fused=34 rerank=rrf rerank_top=8 gated=8 top_score=0.032018442622950824 query_preview=AMS 无法上电时，怎么确认是不是供电问题？

### [2026-10-28 15:11:50] stage=model.select req=- user=- model=qwen3_8_flash
- mode=auto model_id=qwen3_8_flash model_name=qwen3.8-flash
