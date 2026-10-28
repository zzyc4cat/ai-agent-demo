# TODO

> 更新规则：每天结束前更新一次；完成打勾，不删除记录。
> 优先级：P0 = 不做就卡住；P1 = 本周该做；P2 = 有余力。

## 图例

- `[ ]` 待办　`[~]` 进行中　`[x]` 完成　`[!]` 阻塞
- 归属里程碑：M1 证据 / M2 上线 / M3 交付 / M4 可面试（见 `PRD.md` 6.2）

## 状态快照（2026-10-28）

- **语料**：44 篇，`corpus.csv` 校验通过；索引 234 块（已清洗 front-matter/来源行/媒体资源，已合并 <200 字碎片）
- **评测**：50 条 `eval/eval_set_v1.csv`；最新结果 `eval/results_qwen.csv`
- **基线**：文档命中 40/40；可答题拒答 0；库外拒答 10/10；50 题约 300 秒（约 6 秒/题）
- **模型**：qwen3.8-flash 已接入（`dashscope_compat`，关闭思考模式，45 秒超时），不再 429
- **已知问题**：m02 的 X1 侧对比依据不足（只能给 A1 侧）；s07 已修复
- **回滚点**：commit `178812b`（上一版 `c769ff9` / tag `pre-pivot`）

### 下一步（M2 上线）

1. 公网部署（Docker + Nginx 或 Cloudflare Tunnel）
2. API Key 鉴权 + 限流
3. 结构化日志 + trace_id + 成本统计
4. `/health` 健康检查

## 本周（W1 · M1 证据）

- [x] P0 语料清单 `corpus.csv`（文件名、型号、版本、文档类型、来源URL、许可）
- [x] P0 收语料：X1 故障排除索引全量 35 条（HMS 除外），共 44 篇；HMS 代码 7 篇 + HMS 介绍 1 篇
- [ ] P0 自写《设备知识管理规范》10 页（5 个小节：元数据、版本、引用、权限、更新）
- [x] P0 建 50 条评测集：40 可答（单文档 20 / 概念 6 / 跨文档 8 / 多跳 6）+ 10 库外
- [x] P0 评测脚本 `scripts/eval_kb.py`：命中、延迟、拒答、成本口径
- [x] P0 跑基线：命中 40/40、拒答 0、库外 10/10、50 题约 300s（`eval/results_qwen.csv`）
- [x] P1 badcase 归因：front-matter 成块、碎片 chunk、对比题过度保守、代码查询向量弱
- [x] P1 修 top3：清洗元数据、合并碎片、top_n=8、代码精确通道、提示词补两条规则
- [ ] P1 写 1500 字《基线评测报告》
- [ ] P2 把 `RAG_Demo` 设为 private

## 后续（按里程碑，不按日期）

### M2 上线（W3）
- [x] 本地公网暴露：Cloudflare Quick Tunnel（临时地址，重启会变；固定地址需命名隧道 + 域名）
- [x] 鉴权：API Key（M2）→ 账号 token（M3 已替换，旧 Key 不再用于问答）
- [x] 限流 10 次/分钟（滑动窗口，按 Key/IP）
- [x] 结构化日志 + trace_id（`api.access` / `api.kb`）
- [x] 成本统计：每条回答记录 prompt/completion tokens，`/admin/usage` 汇总，价格见 `config/pricing.yml`
- [x] `/health` 健康检查
- [x] `/kb/ask` 知识库问答接口（返回答案 + 引用）
- [x] 一键启动脚本 `start-api.ps1` / `start-tunnel.ps1`

### M3 交付（W4–W5）
- [x] 租户配置化：`tenants/<id>.yaml` + `scripts/init_tenant.py`
- [x] 检索隔离：每租户独立 collection（demo 复用 agent_sample，demo2 独立）
- [x] 隔离测试 `tests/test_isolation.py`（4 条，全部通过）
- [x] 反馈按租户落库（`feedback` 表 + `POST /feedback`）
- [x] 对外 React 对话页（Vite + TS，SSE 流式、引用卡片、点赞点踩）
- [x] `POST /kb/stream` SSE 接口（meta → citations → token* → done）
- [x] 会话历史按租户落库（`kb_conversations` / `kb_messages`）
- [x] 会话置顶/取消置顶、重命名、删除
- [x] 账号体系：scrypt 密码、注册/登录/退出、token 会话（`auth_sessions`）
- [x] 租户从登录用户推导，不再信任 `X-Tenant`（旧接口已切换）
- [x] 会话按用户隔离（列表/读取/改名/删除，越权 404）
- [x] 管理员角色与接口权限（普通用户访问 admin 返回 403）
- [x] 账号测试 `tests/test_auth.py`（3 条，通过）
- [x] P2 管理页：文档列表、软删除/恢复、审计日志
- [x] P3 录入：文件上传（md/txt/pdf/docx）、URL 导入（Node + Edge 渲染）、异步入库 + 任务轮询
- [x] Word（.docx）入库：python-docx 解析段落与表格
- [x] 软删除 30 天后自动彻底删除（含原文件），审计页支持恢复

### 稳定性（2026-10-28）
- [x] 测试全绿：90 条通过（含新增账号、成本、任务兜底测试）
- [x] 入库任务重启兜底：遗留 pending/processing 标记 failed
- [x] 备份脚本 `scripts/backup.py`（app.db + 语料 + 可选向量库）
- [x] 基线评测报告 `docs/基线评测报告.md`
- [x] `component-api.md` 鉴权说明同步
- [x] 旧个人助手清理：`agent/`、`app.py`、Streamlit 启动脚本、`/chat`、`/rag/summarize`、旧测试
- [x] 管理员可见范围：保留本租户全部会话（A）
- [x] `docs/设备知识管理规范.md`
- [x] 稳定公网地址 —— 决定：暂不做
- [x] 评测集 v2（100 条）跑通：DocHit@5 66/67、可答拒答 0/67、库外 33/33、1065ms
- [x] 修正 v2 标注：n14/n16 转为跨文档题并补测（rank 2 / 1）
- [ ] p01 排第 6：排序边缘，待调融合或补样本

### M4 可面试（W6）
- [ ] 内测 10 人 × 1 周，收集 ≥20 条反馈
- [ ] 3 分钟演示视频
- [ ] 题库过两遍 + 2 轮模拟面试
- [ ] 简历定稿

### 文档债务
- [x] `README.md` 重写为知识库产品说明
- [x] `component-api.md` 鉴权说明同步为账号 token
- [x] 评测集扩到 100 条（v2 已跑，待修标注）
- [ ] LoRA 对照实验（可砍）

## 待决问题

| # | 问题 | 现状 | 决定时间 |
|---|---|---|---|
| 1 | 元数据从文件名解析还是人工填？ | 待 W1 验证 | W1 末 |
| 2 | Chroma 的租户隔离用 collection 还是 metadata？ | 已定：collection/租户（demo 复用 agent_sample，其余独立） | 2026-10-28 |
| 3 | 线上模型最终用 DeepSeek 还是通义？ | 已定：qwen3.8-flash 主用（0.8/2.7 元每 M），deepseek-flash 备用 | 2026-10-26 |
| 4 | 前端部署与后端同域还是分域？ | 已定：同域，构建产物挂 `/app/` | 2026-10-28 |
| 5 | 稳定公网地址怎么解决？ | 已定：暂不做，继续用临时隧道 | 2026-10-28 |
| 6 | 管理员能看本租户全部会话吗？ | 已定：保留（客服场景），写入 README 与规范 | 2026-10-28 |
| 7 | 旧个人助手代码 / 接口是否清理？ | 已定：已清理（2026-10-28） | 2026-10-28 |

## 已完成

| 日期 | 事项 |
|---|---|
| 2026-10-26 | PRD v0.10 定稿；项目文档 8 件套建立 |
| 2026-10-26 | X1 故障排除语料 44 篇入库，corpus 校验通过 |
| 2026-10-26 | Phase 1 清理：删除缓存/旧向量库/日志，释放 1.6 MB；80 项测试全过；标签 `pre-pivot` |
| 2026-10-26 | 评测集 50 条 + `eval_kb.py` + 基线（命中 40/40、拒答 0、库外 9/10、1.1s） |
| 2026-10-26 | 切分修复：合并碎片块 + 清洗元数据，530 → 234 块；HMS 代码精确通道 |
| 2026-10-26 | 模型对比：qwen3.8-flash vs deepseek-flash，价格与实测 token 已记录 |
| 2026-10-28 | 接入 qwen3.8-flash（dashscope_compat + 关思考），全量 50 条跑通；n06 标注修正；s07 已答对 |
| 2026-10-28 | 账号体系 + 多租户隔离 + React 页 + 管理页（上传/URL/审计/恢复） |
| 2026-10-28 | 测试修复至 90 条全绿；任务重启兜底；token/成本统计；备份脚本；基线评测报告 |
