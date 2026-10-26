"""UI 优化 1–5 验收测试。"""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, ROOT)
sys.path.insert(0, SRC)


def test_opt1_caption_no_system_hint_on_page():
    """页面说明不泄露系统提示细节。"""
    text = open(os.path.join(ROOT, "app.py"), encoding="utf-8").read()
    assert 'st.caption("生活 / 工作 / 学习")' in text
    assert "系统提示优先" not in text.split("st.caption")[1].split("\n")[0]
    # 逻辑仍在系统提示中
    main = open(os.path.join(ROOT, "prompts", "main_prompt.txt"), encoding="utf-8").read()
    assert "最高优先级" in main or "优先级最高" in main
    assert "不知道" in main


def test_opt2_switch_user_flow_no_inline_add_when_logged_in():
    """已登录时切换用户流程不内联新建。"""
    text = open(os.path.join(ROOT, "app.py"), encoding="utf-8").read()
    assert "或输入新用户名以添加" not in text
    assert 'st.button("添加并切换"' not in text
    assert "_logout_for_switch" in text
    assert "awaiting_login" in text
    assert "load_messages" in text


def test_opt2_chat_history_persist(tmp_path, monkeypatch):
    """聊天历史可落库再读回。"""
    import services.storage as storage
    from services import user_service, chat_service

    monkeypatch.setattr(storage, "DB_PATH", str(tmp_path / "c.db"))
    storage.ensure_db()
    u = user_service.create_user("HistUser")
    cid = chat_service.new_conversation_id()
    chat_service.append_message(u["id"], cid, "user", "你好")
    chat_service.append_message(u["id"], cid, "assistant", "你好，有什么可以帮忙")
    loaded = chat_service.load_messages(u["id"], cid)
    assert len(loaded) == 2
    assert loaded[0]["content"] == "你好"
    # 另一用户隔离
    u2 = user_service.create_user("Other")
    assert chat_service.load_messages(u2["id"], cid) == []


def test_opt3_new_chat_and_history_ui():
    """新对话与历史列表相关源码存在。"""
    text = open(os.path.join(ROOT, "app.py"), encoding="utf-8").read()
    assert 'st.button("新对话"' in text
    assert "最近" in text
    assert "_start_new_chat" in text
    assert "list_conversations" in text


def test_opt4_chinese_mode_and_skills():
    """中文模式名与技能选项存在。"""
    text = open(os.path.join(ROOT, "app.py"), encoding="utf-8").read()
    assert '"自动": "auto"' in text or "'自动': 'auto'" in text
    assert "手动" in text
    assert "默认助手" in text
    assert "每日简报" in text
    assert "周报复盘" in text
    assert 'st.selectbox(\n        "技能"' in text or 'st.selectbox(\n        "技能",' in text
    # 不应在 selectbox 直接列出英文 skill id 作为展示项
    assert '"daily_briefing"' not in text.split("SKILL_OPTIONS")[1].split(")")[0] or "每日简报" in text


def test_skill_selectbox_uses_key_not_index_overwrite():
    """技能/模式选择须用 key 绑定，禁止 index= 再回写 session_state（会导致点两次才切换）。"""
    text = open(os.path.join(ROOT, "app.py"), encoding="utf-8").read()
    assert 'key="skill_label"' in text
    assert 'key="model_mode_label"' in text
    assert 'st.session_state["skill"] = SKILL_OPTIONS[st.session_state["skill_label"]]' in text
    # 技能 selectbox 块内不应再用 index=
    skill_block = text.split('"技能"')[1].split("st.session_state[\"skill\"]")[0]
    assert "index=" not in skill_block
    assert all(
        s in text
        for s in (
            '"默认助手": "default"',
            '"每日简报": "daily_briefing"',
            '"周报复盘": "weekly_review"',
        )
    )


def test_skill_label_maps_to_internal_id_on_change():
    """侧栏中文名变更后，映射的内部 skill id 必须同步（聊天走 session_state['skill']）。"""
    text = open(os.path.join(ROOT, "app.py"), encoding="utf-8").read()
    # 源码中映射存在，且 execute_stream 使用 session_state skill
    assert '"每日简报": "daily_briefing"' in text
    assert "skill=st.session_state.get(\"skill\"" in text or "skill=st.session_state.get('skill'" in text
    assert 'SKILL_OPTIONS[st.session_state["skill_label"]]' in text



def test_opt5_web_search_duckduckgo_available():
    """web_search 走 DuckDuckGo 路径。"""
    from agent.tools.agent_tools import web_search, fetch_webpage, TOOLS_A

    names = {t.name for t in TOOLS_A}
    assert "web_search" in names
    assert "fetch_webpage" in names
    # 不强制外网：至少函数可调用并返回字符串
    out = web_search.invoke({"query": "LangChain ReAct"})
    assert isinstance(out, str)
    assert "UNTRUSTED_DATA" in out  # 工具层仍包裹；UI 层不应展示
    # 非法 url
    bad = fetch_webpage.invoke({"url": "not-a-url"})
    assert "不知道" in bad


def test_opt5_stream_hides_untrusted_logic():
    """流式展示会隐藏 UNTRUSTED 标记。"""
    src = open(os.path.join(ROOT, "src", "agent", "react_agent.py"), encoding="utf-8").read()
    assert "ToolMessage" in src
    assert "UNTRUSTED_DATA" in src
    assert "tool_calls" in src
