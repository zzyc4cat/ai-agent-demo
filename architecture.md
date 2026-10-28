# 架构与数据流

> 当前实现为准；历史个人助手代码已于 2026-10-28 清理。

## 总览

```text
┌─────────────────────────────────────────────────────────┐
│ 前端                                                     │
│  React 18 + Vite（登录/对话/历史/管理页）                 │
└───────────────┬─────────────────────────────────────────┘
                │ HTTPS / SSE
┌───────────────▼─────────────────────────────────────────┐
│ FastAPI                                                  │
│  鉴权（Bearer）、限流、日志、trace_id、成本统计            │
│  ├── /auth/*       注册/登录/退出                         │
│  ├── /kb/stream    SSE 问答 + 引用                        │
│  ├── /kb/conversations 会话管理                           │
│  ├── /feedback     反馈                                   │
│  └── /admin/*      文档/审计/任务/用量                     │
└───────┬──────────────────────┬──────────────────────────┘
        │                      │
┌───────▼────────┐   ┌─────────▼─────────────────────────┐
│ 检索链路        │   │ 生成链路                           │
│ 向量(Chroma)    │   │ qwen3.8-flash（DashScope）         │
│ + BM25          │   │ 可选 DeepSeek 兜底                  │
│ → RRF → rerank  │   │ 提示词 + 引用注入 + 门控            │
│ → 租户 collection│   │                                   │
└───────┬────────┘   └─────────┬─────────────────────────┘
        │                      │
┌───────▼──────────────────────▼─────────────────────────┐
│ 存储                                                    │
│  SQLite：账号/会话/消息/文档元数据/审计/任务/反馈          │
│  Chroma：向量（每租户独立 collection）                    │
│  文件：原始文档、上传、日志                                │
└─────────────────────────────────────────────────────────┘
```

## 数据流一：文档入库

```text
上传文件
 → 计算 hash（去重，决定是否增量更新）
 → 解析（pypdf / python-docx / 文本）
 → 元数据抽取或人工填写（型号、版本、文档类型、生效状态）
 → 切分（按章节优先，chunk 800 / overlap 100）
 → 向量化（BGE 或 DashScope embedding）
 → 写入 Chroma（带 tenant_id、doc_id、model_no、version 元数据）
 → 写入 SQLite documents（状态：已入库 / 解析失败）
 → 刷新 BM25 索引
```

要点：

- 解析失败要留下记录，不能静默跳过。
- 同一 `hash` 的文件不重复入库。
- 新版本入库时，旧版本标记为 `effective=0`，**不删除**（审计需要）。

## 数据流二：问答

```text
用户提问
 → 鉴权：token → tenant_id（不接受 URL 传租户）
 → 查询改写（可选）
 → 检索：向量 Top-K + BM25 Top-K
       过滤条件：tenant_id + model_no（若识别到）+ effective=1
 → RRF 融合 → 可选 rerank
 → 门控：分数过低 → 直接返回“不知道”
 → 组装提示词（系统规则 + 引用片段 + 用户问题）
 → 生成（流式）
 → 返回：答案流 + citations（文档、页码、原文）
 → 落库：messages（答案、引用、延迟、成本）
```

要点：

- **过滤必须在检索前**，不能先检索再过滤（越权与漏召回）。
- 引用要能回到原文位置；没有引用的答案不允许展示。
- 门控阈值在 `config/` 里，不写死。

## 多租户隔离点

| 层 | 隔离方式 |
|---|---|
| 鉴权 | token 里带 `tenant_id`，请求体不接受租户参数 |
| SQLite | 所有业务表带 `tenant_id`，查询统一走封装函数 |
| Chroma | collection 或 metadata 过滤 `tenant_id`，二选一，全项目统一 |
| 文件 | `data/tenants/{tenant_id}/` |
| 日志 | 每条日志带 `tenant_id`，便于排查串数据 |

三条必测用例：跨租户查文档、跨租户查会话、跨租户查 badcase。

## 目标目录结构

```text
web/                  React 对话页（Vite）
  src/components/     MessageBubble / CitationCard / FeedbackBar
  src/api.ts          SSE 客户端
src/
  api_server.py       FastAPI 路由
  auth/               登录与 token
  rag/                解析、切分、检索、融合、门控
  agent/              多跳编排（LangGraph）
  services/           业务表读写（全部带 tenant_id）
  model/              模型路由
  utils/
tenants/
  demo.yaml           租户配置
scripts/
  init_tenant.py      开新租户
  create_user.py      建账号
  eval_kb.py          评测
  build_corpus.py     语料导入
  backup.py           备份
data/
  tenants/{id}/       各租户语料
tests/
  test_isolation.py   隔离测试
  test_auth.py        账号与越权
  test_cost_and_tasks.py 成本与任务兜底
```

## 关键决策

| 决策 | 理由 | 何时改 |
|---|---|---|
| Chroma 而非 pgvector | 当前语料规模小，embedded 最省事 | 10 万文档 |
| SQLite 而非 Postgres | 单机、低并发 | 多实例部署 |
| 每租户独立 collection | 隔离简单、易测 | 跨租户检索需求 |
| React 单页 + /app/ 挂载 | 与后端同域，部署简单 | 需要 SEO 时上 Next.js |
| 账号 token 而非共享 Key | 会话归属与越权可验证 | 接入 SSO |

## 现状 vs 目标

| 项 | 现状 | 目标 |
|---|---|---|
| 前端 | React 对话页 + 管理页 | 保持 |
| 隔离 | `tenant_id` + `user_id` 从 token 推导 | 已完成 |
| 元数据 | 文件名与目录 | 型号、版本、文档类型、生效状态 |
| 检索过滤 | 租户 collection | 型号 + 版本过滤 |
| 评测 | 50 条、严格口径 | 100 条 + 引用准确率 |
| 部署 | 本机 + 临时隧道 | 稳定地址 |
