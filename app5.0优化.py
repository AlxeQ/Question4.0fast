import streamlit as st
import requests
import json
import urllib.parse
from copy import deepcopy

# 页面配置
st.set_page_config(
    page_title="商圈经理提问优化助手",
    page_icon="🏢",
    layout="centered"
)

# 自定义样式
st.markdown("""
<style>
.stTextArea textarea {
    min-height: 150px;
}
.result-block {
    background-color: #f9f9f9;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
    line-height: 1.6;
}
.feedback-section {
    border-top: 1px solid #eee;
    padding-top: 1.5rem;
    margin-top: 1.5rem;
}
.feedback-item {
    margin-bottom: 1rem;
}
.code-block {
    background: #f5f5f5;
    padding: 1rem;
    border-radius: 0.5rem;
    font-family: monospace;
    white-space: pre-wrap;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# 初始化session状态
def init_session():
    if "custom_prompt" not in st.session_state:
        st.session_state.custom_prompt = """你是一位"问题优化教练"，服务对象是链家商圈经理。请严格遵守：
1. 必须保留原始问题中的所有具体信息（特别是地理位置等），不得修改或编造
2. 从"目标、背景、细节、期待"四个维度分析，指出提问中缺失或模糊的信息
3. 针对每个维度生成 3~5 条可选的引导词示例
4. 输出结构化完整的优化提问示范
5. 用温和专业的教练语气，教他们如何精准提问"""

    if "optimized_result" not in st.session_state:
        st.session_state.optimized_result = None

    if "feedback_data" not in st.session_state:
        st.session_state.feedback_data = {
            "goal": "",
            "context": "",
            "details": "",
            "expectation": ""
        }

    if "final_result" not in st.session_state:
        st.session_state.final_result = None

init_session()

# 应用标题
st.title("🏢 商圈经理提问优化助手")
st.caption("帮助商圈经理优化提问方式，获得更精准的业务建议")

# 自定义提示词区域
with st.expander("🛠️ 自定义系统提示词（高级选项）"):
    st.session_state.custom_prompt = st.text_area(
        "修改系统提示词以改变AI行为：",
        value=st.session_state.custom_prompt,
        height=200,
        help="此提示词将指导AI如何优化您的问题",
        key="custom_prompt_input"
    )

# 主输入区域
with st.form("question_form"):
    user_input = st.text_area(
        "请输入您要优化的问题：",
        placeholder="例如：我不知道怎么说服不配合的同事",
        help="描述您在工作中遇到的困惑或问题",
        key="user_input"
    )
    
    api_key = st.text_input(
        "DeepSeek API Key",
        type="password",
        placeholder="以 sk- 开头的密钥",
        help="请确保API Key有效且有足够额度",
        key="api_key_input"
    )
    
    submitted = st.form_submit_button("🚀 生成优化提问", use_container_width=True)

# 处理初始提交
if submitted:
    if not user_input or not api_key:
        st.error("请填写问题和API Key")
        st.stop()
    
    with st.spinner("正在优化您的提问，请稍候..."):
        messages = [
            {"role": "system", "content": st.session_state.custom_prompt},
            {"role": "user", "content": f"用户原始问题：{user_input}"}
        ]
        
        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get("choices") and data["choices"][0]:
                st.session_state.optimized_result = data["choices"][0]["message"]["content"]
                st.session_state.final_result = None  # 重置最终结果
                st.rerun()
            else:
                st.error("API返回异常：" + json.dumps(data, ensure_ascii=False, indent=2))
                
        except requests.exceptions.RequestException as e:
            st.error(f"请求失败：{str(e)}")
        except Exception as e:
            st.error(f"处理出错：{str(e)}")

# 显示优化结果和反馈表单
if st.session_state.optimized_result and not st.session_state.final_result:
    st.subheader("📌 优化分析结果")
    st.markdown(st.session_state.optimized_result)
    
    st.link_button("🌐 在DeepSeek中继续对话", 
                  f"https://chat.deepseek.com/?q={urllib.parse.quote(st.session_state.optimized_result)}",
                  use_container_width=True)
    
    # 结构化反馈区域
    with st.form("feedback_form"):
        st.subheader("🔧 根据建议完善您的问题")
        
        st.markdown("""
        **请根据AI的分析补充以下信息**（可部分填写）：
        """)
        
        cols = st.columns(2)
        with cols[0]:
            st.session_state.feedback_data["goal"] = st.text_area(
                "🎯 目标",
                value=st.session_state.feedback_data["goal"],
                placeholder="您希望达成的具体目标是什么？",
                height=100,
                key="goal_input"
            )
            st.session_state.feedback_data["context"] = st.text_area(
                "📍 背景",
                value=st.session_state.feedback_data["context"],
                placeholder="相关的背景情况是怎样的？",
                height=100,
                key="context_input"
            )
        
        with cols[1]:
            st.session_state.feedback_data["details"] = st.text_area(
                "🔍 细节",
                value=st.session_state.feedback_data["details"],
                placeholder="需要特别说明的细节有哪些？",
                height=100,
                key="details_input"
            )
            st.session_state.feedback_data["expectation"] = st.text_area(
                "✨ 期待",
                value=st.session_state.feedback_data["expectation"],
                placeholder="您希望获得什么样的帮助？",
                height=100,
                key="expectation_input"
            )
        
        feedback_submitted = st.form_submit_button("🔄 生成最终优化版", use_container_width=True)
    
    # 处理反馈提交
    if feedback_submitted:
        feedback_text = "\n".join([
            f"【用户补充内容】",
            f"目标：{st.session_state.feedback_data['goal']}",
            f"背景：{st.session_state.feedback_data['context']}",
            f"细节：{st.session_state.feedback_data['details']}",
            f"期待：{st.session_state.feedback_data['expectation']}"
        ])
        
        with st.spinner("正在生成最终优化版本..."):
            messages = [
                {"role": "system", "content": st.session_state.custom_prompt},
                {"role": "assistant", "content": st.session_state.optimized_result},
                {"role": "user", "content": f"根据以下补充信息生成最终优化版问题：\n{feedback_text}"}
            ]
            
            try:
                response = requests.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": messages,
                        "temperature": 0.5,
                        "max_tokens": 800
                    },
                    timeout=30
                )
                
                response.raise_for_status()
                data = response.json()
                
                if data.get("choices") and data["choices"][0]:
                    st.session_state.final_result = data["choices"][0]["message"]["content"]
                    st.rerun()
                else:
                    st.error("优化失败：" + json.dumps(data, ensure_ascii=False, indent=2))
                    
            except requests.exceptions.RequestException as e:
                st.error(f"请求失败：{str(e)}")
            except Exception as e:
                st.error(f"处理出错：{str(e)}")

# 显示最终结果（同时保留初始建议）
if st.session_state.final_result:
    st.subheader("📌 优化分析结果（初始建议）")
    st.markdown(st.session_state.optimized_result)
    
    st.subheader("✨ 最终优化版问题（根据您的补充）") 
    st.markdown(st.session_state.final_result)
    
    # 交互按钮
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 下载最终版",
            data=st.session_state.final_result,
            file_name="优化后问题.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col2:
        st.link_button(
            "🌐 在DeepSeek中使用",
            f"https://chat.deepseek.com/?q={urllib.parse.quote(st.session_state.final_result)}",
            use_container_width=True
        )
    
    if st.button("🔄 重新开始新的优化", use_container_width=True):
        st.session_state.optimized_result = None
        st.session_state.final_result = None
        st.session_state.feedback_data = {k: "" for k in st.session_state.feedback_data}
        st.rerun()

# 页脚说明
st.markdown("---")
st.caption("💡 使用提示：通过多次补充信息迭代优化可以获得更精准的问题表述")