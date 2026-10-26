# 开发方式、命令与回归清单

## 环境

| 依赖 | 版本 | 说明 |
|---|---|---|
| Python | 3.12 | 已有 `.venv`，见 `start.bat` |
| Node | 20+ | 仅 React 前端需要 |
| 包管理 | pip / npm | 后端 `requirements.txt`，前端 `web/package.json` |
| 数据库 | SQLite（内置） | 无需安装 |
| 向量库 | Chroma（embedded） | 数据在 `chroma_db/` |

## 首次准备

```powershell
cd "E:\Study\Programs\AI Agent Demo"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env      # 填入 DASHSCOPE_API_KEY / DEEPSEEK_API_KEY
```

前端（W3 后）：

```powershell
cd web
npm install
npm run dev
```

## 日常命令

```powershell
# 后端 API
$env:PYTHONPATH="src"; uvicorn api_server:app --app-dir src --port 8000 --reload

# 管理台（Streamlit）
streamlit run app.py

# 全量测试
$env:PYTHONPATH="src"; pytest tests -q

# 只跑隔离测试
$env:PYTHONPATH="src"; pytest tests/test_isolation.py -q

# 评测（50 条）
$env:PYTHONPATH="src"; python scripts/run_eval.py

# 语料导入
$env:PYTHONPATH="src"; python scripts/build_corpus.py --tenant demo

# 开新租户
$env:PYTHONPATH="src"; python -m scripts.init_tenant --id demo2
```

## 环境变量

| 变量 | 必填 | 用途 |
|---|---|---|
| `DASHSCOPE_API_KEY` | 是 | 通义（embedding/重排/备选模型） |
| `DEEPSEEK_API_KEY` | 是 | 线上生成模型 |
| `AGENT_API_KEY` | 是 | FastAPI 鉴权 |
| `LOG_LEVEL` / `LOG_JSON` | 否 | 日志 |
| `TENANT_DEFAULT` | 否 | 默认租户 id |

**纪律**：`.env` 不进 git；新增变量同时更新 `.env.example`。

## 回归清单

改完代码，按改动类型跑对应项：

| 改动 | 必跑 | 通过标准 |
|---|---|---|
| 检索 / 切分 / 提示词 | 50 条评测 | 四个数不低于上次，且记录到 `logs/eval/` |
| 数据表结构 | `pytest tests -q` | 全绿，隔离测试必过 |
| 多租户逻辑 | `tests/test_isolation.py` | 3 条越权用例全部拦截 |
| 前端对话页 | 手工：登录 → 提问 → 引用 → 反馈 | SSE 正常、引用可展开、反馈入库 |
| 上传/删除文档 | 手工 + 单测 | 上传后能检索到，删除后检索不到 |
| 部署配置 | 手工访问 `/health` | 200，且公网可访问 |

**任何改动后都不许跳过 `pytest`。** 评测与测试是两件事：测试保功能，评测保效果。

## 分支与提交

- 分支：`main` 保持可运行；开发用 `feat/xxx`、`fix/xxx`。
- 提交信息：`feat: 新增型号过滤`、`fix: 修复跨租户查询`、`chore: 更新依赖`。
- 一次提交只做一件事；评测结果变化单独提交。

## 目录约定

- 语料放 `data/tenants/{tenant_id}/`，不放进仓库历史里的大文件（>10 MB 用外链 + 校验）。
- 日志写 `logs/`，不提交。
- 评测结果写 `logs/eval/eval_YYYYMMDD.json`。
- 临时脚本放 `scripts/`，用完删除或标注 `_tmp_`。

## 常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| `ModuleNotFoundError: rag` | `PYTHONPATH` 没设 | 设 `src` 或从项目根跑 |
| 检索不到刚上传的文档 | 索引没刷新 / 元数据过滤掉了 | 查 `effective` 与 `tenant_id` |
| 评测结果波动大 | 温度 >0 或评测集太小 | 温度固定 0，评测集 ≥50 |
| 前端 SSE 断流 | 反代缓冲 | Nginx 关 `proxy_buffering` |
