# 升级执行日志（UPGRADE_LOG）

本文件记录各阶段目标、改动、测试与是否达标。尝试次数按「完整验收一轮」计，超过 10 次记「阶段 N 不符合预期」。

---

## Phase 0 — 平台地基

- **日期**：2026-09-24
- **尝试次数**：1
- **结果**：**达标**
- **快照标签**：`状态0`

### 目标

工程模板、日志轮转与 contextvars、ModelRouter、PromptGuard 骨架、Checkpointer、DEBUG 大纲；系统提示含最高优先级与「不知道」约束。

### 主要改动

- 新增 `.gitignore`、`.env.example`、`requirements.txt`、`DEBUG.md`
- `config/logging.yml`、`models.yml`、`prompt_guard.yml`；更新 `rag.yml` / `prompts.yml`
- 重写 `utils/logger_handler.py`、`model/factory.py`（懒加载路由）
- `agent/tools/prompt_guard.py`、`middleware.py`（skill 白名单 + 工具降级）、`react_agent.py`（checkpointer/护栏/Auto 换模钩子）
- `rag/rag_service.py` 去掉 print，空检索返回「不知道」，UNTRUSTED 包裹
- 更新 `prompts/main_prompt.txt`、`rag_summarize.txt`；新增 `prompts/skills/weekly_review.txt`
- `tests/test_phase0.py`

### 测试

```text
pytest tests/test_phase0.py -v
7 passed
```

覆盖：日志写入与 request_id、护栏泄露/忽略、额度错误识别、系统 Prompt 加载、UNTRUSTED、懒加载 import。

### 备注

- 旧扫地机器人民服语料仍在 `data/`，**Phase 1 清除并替换**。
- Checkpointer 当前为 MemorySaver；持久化 SQLite 在 Phase 2 用户模块一并加强。

---

## Phase 1 — （进行中）

（完成后追加）
