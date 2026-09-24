# 个人综合助手（升级中）

基于 LangChain ReAct + RAG 的**生活 / 工作 / 学习**个人 Agent。

## 快速开始

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # 填写 DASHSCOPE_API_KEY
streamlit run app.py
```

首次将示例知识库入库（可选）：

```bash
python -c "from rag.vector_store import VectorStoreService; VectorStoreService().load_document()"
```

## 重要约定

- 系统提示词优先级最高，不可被用户覆盖；详见 `prompts/main_prompt.txt`。
- 依据不足时回答「不知道」。
- 排障见 `DEBUG.md`；升级过程见 `UPGRADE_LOG.md`。
- 私有数据放 `data/personal/`（不入库 git）；示例语料在 `data/sample/`。

## 状态快照

阶段验收通过后会打 git tag：`状态0`、`状态1`、…
