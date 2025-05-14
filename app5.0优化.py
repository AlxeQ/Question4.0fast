import streamlit as st
import requests
import json
import pandas as pd

st.set_page_config(layout="wide")

# DeepSeek API 设置
API_URL = "https://api.deepseek.com/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer sk-xxx"  # 请替换为你的 API Key
}

# 默认提示词
@st.cache_data
def get_default_prompt():
    return """你是一名提示词优化助手，请根据用户输入的问题，按照目标、背景、细节、期待的结构，帮助用户优化问题表达"""

# 初始化会话状态
if "custom_prompt" not in st.session_state:
    st.session_state.custom_prompt = get_default_prompt()
if "history" not in st.session_state:
    st.session_state.history = []

# 页面标题与介绍
st.title("问题表达优化助手 💡")
st.markdown("请描述你的问题，我们将帮助你优化表达方式，使其更清晰、具体、易于获得精准回答。")

# 输入区域
user_input = st.text_area("✍️ 请输入你希望优化的问题：", height=150)

# 自定义提示词
with st.expander("🛠️ 编辑提示词（高级设置）", expanded=False):
    new_prompt = st.text_area("系统提示词（Prompt）：", value=st.session_state.custom_prompt, height=150)
    if st.button("✅ 更新提示词"):
        st.session_state.custom_prompt = new_prompt
        st.success("提示词已更新")

# 优化函数
def optimize_question():
    if not user_input.strip():
        st.warning("请输入一个问题再点击优化哦！")
        return

    with st.spinner("正在优化中，请稍候..."):
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": st.session_state.custom_prompt},
                {"role": "user", "content": user_input}
            ],
            "temperature": 0.3,
            "max_tokens": 1024
        }

        try:
            response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=(10, 30))
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # 保存历史记录
            st.session_state.history.insert(0, {
                "原始问题": user_input,
                "优化结果": content
            })

            st.session_state.optimized_output = content

        except Exception as e:
            st.error(f"请求失败：{str(e)}")

# 优化按钮
st.button("✨ 优化表达", on_click=optimize_question)

# 显示结果
if "optimized_output" in st.session_state and st.session_state.optimized_output:
    st.markdown("#### 🪄 优化后的问题表达：")
    st.success(st.session_state.optimized_output)

# 展示历史记录
if st.session_state.history:
    st.markdown("#### 📜 历史记录")
    for i, record in enumerate(st.session_state.history):
        with st.expander(f"🔹 记录 {i + 1}"):
            st.markdown(f"**原始问题：** {record['原始问题']}")
            st.markdown(f"**优化结果：**\n\n{record['优化结果']}")
