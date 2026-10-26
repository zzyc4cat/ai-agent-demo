"""
services 包：SQLite 业务层。

storage 建库；user/chat/task/note 均按 user_id 隔离，供 Streamlit、API 与 Agent 工具调用。
"""
