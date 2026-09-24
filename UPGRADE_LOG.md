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

### 测试

`pytest tests/test_phase0.py` → **7 passed**

---

## Phase 1 — 领域迁移与示例语料

- **日期**：2026-09-24
- **尝试次数**：2（writing_polish 缺「不知道」已修）
- **结果**：**达标**
- **快照标签**：`状态1`

### 测试

`pytest tests/test_phase1.py` → **5 passed**；扫地机器料已清除。

---

## Phase 2 — 用户隔离与存储

- **日期**：2026-09-24
- **尝试次数**：1
- **结果**：**达标**
- **快照标签**：`状态2`

### 改动

`services/storage|user|task|note_service.py`；thread_id=`{user_id}:{conversation_id}`；入库元数据 corpus。

### 测试

`pytest tests/test_phase2.py` → **3 passed**

---

## Phase 3 — Tools-A

- **日期**：2026-09-24
- **尝试次数**：2（模块级 RAG 急切初始化导致无 Key 测试失败 → 改为懒加载）
- **结果**：**达标**
- **快照标签**：`状态3`

### 改动

重写 `agent_tools.py`（rag/搜索/天气/时间/待办/笔记/记忆/沙箱/入库/set_skill）；删除客服 mock。

### 测试

`pytest tests/test_phase3.py` → **4 passed**

---

## Phase 4 — Skills-A

- **日期**：2026-09-24
- **尝试次数**：1
- **结果**：**达标**
- **快照标签**：`状态4`

### 改动

Skills-A 提示词齐套；白名单与 `set_skill` 校验；`tests/test_phase4.py`。

### 测试

`pytest tests/test_phase4.py` → **2 passed**

---

## Phase 5 — 开箱前端

- **日期**：2026-09-24
- **尝试次数**：1
- **结果**：**达标**
- **快照标签**：`状态5`

### 改动

`app.py`：首次建用户、切换/添加用户、Auto/手动模型、Skill 选择、推荐问题、request_id 展示；无 Key 时友好报错。

### 测试

UI 源码断言（pytest 不直接 `import app` 以免无 Key 强建 Agent）→ 见 `test_phase56_functional.py::test_app_source_has_user_and_model_ui` **passed**

---

## Phase 6 — 增强与发布就绪

- **日期**：2026-09-24
- **尝试次数**：2（护栏正则空白、app import/Agent 初始化）
- **结果**：**达标**
- **快照标签**：`状态6`

### 改动

- Tools-B 子集：`calculator`、闪卡三件套（`tools_b.py`）
- Skills-B 部分：`spaced_repetition` / `error_attribution` / `study_plan`
- 护栏规则增强；全量 pytest 绿
- 本日志与 DEBUG 更新

### 未纳入本阶段（明确延期，非失败）

- BM25 混合检索完整实现、天气/搜索真实 API、日历 OAuth、FastAPI、Docker
- 记入后续迭代，不记「不符合预期」

### 测试

全量：`pytest tests` → **25 passed**

---

## 总功能性测试矩阵（无真实 LLM 调用）

| 功能 | 验证方式 | 结果 |
|---|---|---|
| 日志 request_id | test_phase0 | 通过 |
| 模型列表/额度错误识别 | test_phase0 | 通过 |
| 提示词泄露拒答 | test_phase0/56 | 通过 |
| 系统优先 + 不知道 | test_phase1 | 通过 |
| 无扫地机器料 | test_phase1 | 通过 |
| 用户隔离待办/笔记 | test_phase2 | 通过 |
| Tools-A 待办笔记沙箱 | test_phase3 | 通过 |
| 天气/搜索诚实降级 | test_phase3 | 通过 |
| Skills-A 可加载 | test_phase4 | 通过 |
| set_skill 白名单 | test_phase4 | 通过 |
| 计算与闪卡 | test_phase56 | 通过 |
| Tools 注册齐全 | test_phase56 | 通过 |
| 前端含用户/模型 UI | test_phase56 | 通过 |

**需你本机有 Key 时再验**：`streamlit run app.py` 真实对话、RAG 入库后问答、Auto 换模。

---

## 回溯标签

```text
git checkout 状态0   # Phase0
git checkout 状态1   # Phase1
...
git checkout 状态6   # 当前终态
```

（状态2–6 在同一次连续交付提交上打标，详见 git tag）
