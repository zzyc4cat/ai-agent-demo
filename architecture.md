# 架构与数据流

> 本文描述**目标态**。现状代码是“个人综合助手 Agent”，改造中；差异见文末。

## 总览

```text
┌─────────────────────────────────────────────────────────┐
│ 前端                                                     │
│  React 18 + Vite（对外对话页：登录/对话/引用/反馈）        │
│  Streamlit（对内后台：文档/badcase/租户配置）              │
└───────────────┬─────────────────────────────────────────┘
                │ HTTPS / SSE
┌───────────────▼─────────────────────────────────────────┐
│ FastAPI                                                  │
│  鉴权（Bearer）、限流、日志、trace_id、成本统计            │
│  ├── /auth/login   租户与用户                             │
│  ├── /chat/stream  SSE 问答                              │
│  ├── /documents    上传/删除/重建                         │
│  ├── /feedback     反馈                                  │
│  └── /admin/*      badcase、租户配置                      │
└───────┬──────────────────────┬──────────────────────────┘
        │                      │
┌───────▼────────┐   ┌─────────▼─────────────────────────┐
│ 检索链路        │   │ 生成链路                           │
│ 向量(Chroma)    │   │ 本地 Qwen（开发）                  │
│ + BM25          │   │ DeepSeek（线上）                   │
│ → RRF → rerank  │   │ 提示词 + 引用注入 + 门控            │
│ → 元数据过滤     │   │                                   │
└───────┬────────┘   └─────────┬─────────────────────────┘
        │                      │
┌───────▼──────────────────────▼─────────────────────────┐
│ 存储                                                    │
│  SQLite：租户/文档/会话/消息/反馈/坏例                    │
│  Chroma：向量（按 tenant_id 分区）                       │
│  文件：原始文档、分词缓存、日志                              │
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
  run_eval.py         评测
  build_corpus.py     语料导入
data/
  tenants/{id}/       各租户语料
tests/
  test_isolation.py   隔离测试
```

## 关键决策

| 决策 | 理由 | 何时改 |
|---|---|---|
| Chroma 而非 pgvector | 30 篇文档，embedded 最省事 | 10 万文档 |
| SQLite 而非 Postgres | 单机、低并发 | 多实例部署 |
| Streamlit 只做后台 | 内部工具，一周能做完 | 不对内了才改 |
| React 只做对话页 | 对外要流式与引用交互 | 需要 SEO 时上 Next.js |
| LangGraph 只做多跳 | 核心检索自己写，便于调试 | — |

## 现状 vs 目标

| 项 | 现状 | 目标 |
|---|---|---|
| 前端 | Streamlit 单页 | React 对话页 + Streamlit 后台 |
| 隔离 | `user_id` | `tenant_id`（user 挂在 tenant 下） |
| 元数据 | 无型号/版本 | 型号、版本、文档类型、生效状态 |
| 检索过滤 | 无 | 型号 + 版本 + 租户 |
| 评测 | 8 条、口径宽松 | 50 条、严格三档 |
| 部署 | 本机 | 公网 + 鉴权 + 限流 + 日志 |
