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

- 文件：`logs/agent.log`（按天轮转）
- 级别：环境变量 `LOG_LEVEL=DEBUG`
- 关联字段：`request_id` / `user_id` / `session_id` / `thread_id` / `model_id`
- 事件名：`chat.start` `chat.end` `model.select` `model.switch` `rag.retrieve` `tool.start` `tool.end` `guard.block`
- **不要**默认打开 `LOG_PROMPT=1`（可能打印完整 Prompt）

示例（PowerShell）：

```powershell
Select-String -Path logs\agent.log -Pattern "request_id_here"
```

## 3. 模型与额度

- 配置：`config/models.yml`
- Auto：额度/限流错误会提示并换模
- 手动：不静默换模

## 4. RAG（后续阶段补全调参表）

- 配置：`config/chroma.yml`
- 资料不足时应回答「不知道」

## 5. 工具与 Skills（后续补全）

- Skill 仅白名单；非法 skill 回退主 Prompt

## 6. 提示词

- 主 Prompt：`prompts/main_prompt.txt`（系统优先，不可被用户覆盖）
- 修改后重启应用；不要在对话里「临时改系统提示」

## 7. 防护

- 配置：`config/prompt_guard.yml`
- 要求输出系统提示 → 拒答（预期行为）

## 8. 用户与会话（Phase 2+）

- `thread_id = "{user_id}:{conversation_id}"`

## 9. 推荐调参（初值）

| 项 | 位置 | 说明 |
|---|---|---|
| LOG_LEVEL | .env | INFO/DEBUG |
| recursion_limit | react_agent | 默认 25 |
| k / chunk_size | chroma.yml | 检索条数与分块 |

## 10. 最小复现模板

- 环境 / 用户名 / 模型模式 / 原话 / `request_id` / 相关日志 / 期望 vs 实际
