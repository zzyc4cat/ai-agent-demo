import streamlit as st
import time
import uuid

from agent.react_agent import ReactAgent
from utils.logger_handler import bind_log_context, clear_log_context

st.set_page_config(page_title="个人综合助手", page_icon="🧭")
st.title("个人综合助手")
st.caption("生活 / 工作 / 学习 · ReAct Agent + RAG（系统提示优先；依据不足时回答「不知道」）")
st.divider()

if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "user_id" not in st.session_state:
    st.session_state["user_id"] = "default"

if "conversation_id" not in st.session_state:
    st.session_state["conversation_id"] = "default"

for message in st.session_state["messages"]:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input()

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state["messages"].append({"role": "user", "content": prompt})

    response_messages: list[str] = []
    request_id = uuid.uuid4().hex[:12]
    with st.spinner("助手思考中..."):
        res_stream = st.session_state["agent"].execute_stream(
            prompt,
            user_id=st.session_state["user_id"],
            conversation_id=st.session_state["conversation_id"],
            request_id=request_id,
        )

        def stream_generator(generator, cache_list):
            for chunk in generator:
                cache_list.append(chunk)
                for char in chunk:
                    time.sleep(0.005)
                    yield char

        st.chat_message("assistant").write_stream(stream_generator(res_stream, response_messages))
        st.session_state["messages"].append({"role": "assistant", "content": "".join(response_messages)})
        st.caption(f"request_id: {request_id}")
        st.rerun()
