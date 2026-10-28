# 组件与接口契约

> 前端（React）与后端（FastAPI）的约定。改接口先改本文，再改代码。

## 一、React 组件

目录：`web/src/components/`

### 组件树

```text
App
├── LoginPage
└── ChatPage
    ├── TopBar
    ├── MessageList
    │   └── MessageBubble
    │       ├── CitationCard ×N
    │       └── FeedbackBar
    ├── EmptyState
    └── Composer
```

### 组件契约

| 组件 | 职责 | Props | 事件 |
|---|---|---|---|
| `App` | 鉴权状态、路由切换 | — | — |
| `LoginPage` | 登录表单 | `tenants: Tenant[]` | `onLogin(token)` |
| `ChatPage` | 会话状态、SSE 订阅 | `token` | — |
| `TopBar` | 租户名、用户菜单 | `tenantName`, `userName` | `onLogout()` |
| `MessageList` | 消息滚动、自动到底 | `messages: Message[]` | — |
| `MessageBubble` | 单条消息渲染 | `message`, `isStreaming` | `onFeedback(messageId, rating)` |
| `CitationCard` | 引用展示与展开 | `citation` | `onOpen(docId, page)` |
| `FeedbackBar` | 点赞点踩 + 原因 | `messageId`, `current?` | `onSubmit(rating, reason?)` |
| `Composer` | 输入与发送 | `disabled`, `onSend(text)` | — |
| `EmptyState` | 空态示例问题 | `examples: string[]` | `onPick(text)` |

### 数据结构

```ts
type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  pending?: boolean;
  feedback?: 'up' | 'down' | null;
};

type Citation = {
  docId: string;
  title: string;
  page?: number;
  snippet: string;
};
```

### 状态约定

- 流式期间 `pending=true`，`content` 增量追加；结束后置 `false` 并写入 `citations`。
- 同一会话只允许一个进行中的请求；发送中 `Composer` 禁用。
- 反馈提交后本地立即置位，失败回滚并提示。

## 二、HTTP 接口

Base：`/api`；鉴权：`Authorization: Bearer <token>`。

| 方法 | 路径 | 请求 | 响应 |
|---|---|---|---|
| POST | `/auth/login` | `{username, password, tenantId}` | `{token, user:{id,name}, tenant:{id,name}}` |
| POST | `/chat/stream` | `{conversationId?, message}` | `text/event-stream` |
| GET | `/documents` | `?page=&size=` | `{items:[{id,title,modelNo,version,status}], total}` |
| POST | `/documents` | multipart：file + `{modelNo,version,docType,effective}` | `{id,status}` |
| DELETE | `/documents/{id}` | — | `{ok:true}` |
| POST | `/documents/{id}/reindex` | — | `{jobId}` |
| POST | `/feedback` | `{messageId, rating, reason?}` | `{ok:true}` |
| GET | `/admin/badcases` | `?status=&page=` | `{items:[...], total}` |
| GET | `/health` | 无鉴权 | `{status:'ok'}` |

### SSE 事件格式

```text
event: token
data: {"text":"E07 表示"}

event: citation
data: {"docId":"d1","title":"X1 手册","page":42,"snippet":"..."}

event: done
data: {"messageId":"m1","latencyMs":1234,"cost":0.0008}

event: error
data: {"code":"RETRIEVAL_EMPTY","message":"没有找到可靠依据"}
```

前端按 `event` 分派；收到 `done` 关闭连接。

## 三、错误码

| code | HTTP | 含义 | 前端表现 |
|---|---|---|---|
| `AUTH_INVALID` | 401 | token 无效/过期 | 跳登录 |
| `FORBIDDEN` | 403 | 越权（跨租户） | 提示无权限 |
| `RATE_LIMITED` | 429 | 触发限流 | 提示稍后再试 |
| `RETRIEVAL_EMPTY` | 200 | 无可靠依据 | 显示“没有找到依据” |
| `PARSE_FAILED` | 422 | 文档解析失败 | 后台标记失败原因 |
| `INTERNAL` | 500 | 服务异常 | 通用提示 + 重试 |

## 四、前端页面（React）

| 页面 | 组件 | 说明 |
|---|---|---|
| 登录/注册 | `Login` | 账号密码，token 存 localStorage |
| 对话 | `ChatApp` | 流式问答、引用、反馈 |
| 历史 | 侧边栏 | 置顶、重命名、删除、刷新恢复 |
| 管理 | `AdminPage` | 文档列表、上传、URL 导入、删除/恢复、审计、用量 |

前端只通过 `web/src/api.ts` 访问后端，不直连数据库。

## 五、改造注意

- `/chat` 与 `/rag/summarize` 已于 2026-10-28 删除；知识库对话统一走 `/kb/stream`。
- 鉴权已切换为账号体系：`/auth/login` 发 token，用户侧 `/kb/*` 与管理侧 `/admin/*` 统一校验 `Authorization: Bearer`；不再使用 `AGENT_API_KEY`。
- 租户与用户由 token 推导，客户端传入的 `X-Tenant` 一律忽略。
- 所有响应体不得包含 `tenant_id` 之外的租户信息，避免前端拼错。
