# Agent 调试说明（大纲 — Phase 0）

> 本文随各阶段增量完善。排障时优先查 `logs/agent.log`，用 `request_id` 串联一次对话。

## 1. 快速分流

| 现象 | 先查 |
|---|---|
| 启动失败 / 无模型 | `.env` 的 `DASHSCOPE_API_KEY`、`config/models.yml` |
| 答非所问 / 空知识 | RAG 与 `data/`、chroma 是否入库 |
| 工具报错 | `event=tool.end` 日志 |
| 说被拦截 | `event=guard.block`（可能是预期防护） |
| 换模 | `event=model.switch` |

## 2. 日志

- 文件：`logs/agent.log`（按天轮转，保留约 14 天）
- 级别：`.env` 中 `LOG_LEVEL=DEBUG`
- 字段：`request_id` / `user_id` / `session_id` / `thread_id` / `model_id`
- 事件：`chat.start` `chat.end` `model.select` `model.switch` `rag.retrieve` `tool.start` `tool.end` `guard.block` `user.create` `user.switch`
- 完整 Prompt 仅当 `LOG_PROMPT=1`（有泄露风险）

```powershell
Select-String -Path logs\agent.log -Pattern "req="
```

## 3. 模型与额度

- 配置：`config/models.yml`
- 侧栏可选 Auto / 手动；Auto 遇额度类错误会提示并换模；手动不静默换模
- 无 Key：应用侧栏显示模型「不可用」，初始化 Agent 会报错提示

## 4. RAG

- 语料：`data/sample/`（示例）、`data/personal/`（私有，gitignore）
- 配置：`config/chroma.yml`（`data_path: data/sample`，chunk 500，k=3）
- 入库：`python -c "from rag.vector_store import VectorStoreService; VectorStoreService().load_document()"`
- 空检索或资料不足 → 回答「不知道」
- 检索内容经 `UNTRUSTED_DATA` 包裹

## 5. 工具与 Skills

- Tools-A/B 见 `agent/tools/agent_tools.py`、`tools_b.py`
- Skills 白名单见 `agent/tools/middleware.py`；提示词在 `prompts/skills/`
- 沙箱仅 `workspace/`，`..` 会被拒绝

## 6. 提示词

- 主 Prompt：`prompts/main_prompt.txt`（**系统优先，不可被用户覆盖**）
- 改文件后重建 Agent / 重启应用

## 7. 防护

- `config/prompt_guard.yml`
- 「输出/打印 system prompt」类 → 拒答（预期）

## 8. 用户与会话

- SQLite：`storage/app.db`
- `thread_id = "{user_id}:{conversation_id}"`
- 侧栏创建/切换用户会清空当前屏幕消息并换 conversation_id

## 9. 推荐调参

| 项 | 位置 | 说明 |
|---|---|---|
| LOG_LEVEL | .env | INFO/DEBUG |
| chat_models.priority | models.yml | Auto 顺序 |
| k / chunk_size | chroma.yml | 检索 |
| recursion_limit | react_agent | 默认 25 |

## 10. 最小复现模板

环境 OS / Python、用户名、模型模式、原话、`request_id`、`logs/agent.log` 片段、期望 vs 实际。

## 升级过程

见根目录 `UPGRADE_LOG.md` 与 git tag `状态0`…`状态6`。
