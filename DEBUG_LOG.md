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
