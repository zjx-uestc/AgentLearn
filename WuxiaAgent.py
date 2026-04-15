import streamlit as st
import os
from openai import OpenAI

# 列出所有会话
#@st.cache_data
def list_sessions():
    return {"a","b","c"}

# 初始化 Ollama 客户端
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama api key'  # 本地调用，秘钥可随意填
)

system_prompt = "你是一个武侠小说内的角色，你的任务是根据用户的问题，生成一个符合该角色人物性格的回复"

st.set_page_config(page_title="Wuxia", layout="wide", initial_sidebar_state="expanded")

# 页面交互后刷新
print("---------重新加载页面---------")

# 初始化会话状态信息
if "session_id" not in st.session_state:
    st.session_state.session_id = 1
if "messages" not in st.session_state:
    st.session_state.messages = []
if "name" not in st.session_state or st.session_state.name == "":
    st.session_state.name = "杨过"
if "character" not in st.session_state or st.session_state.character == "":
    st.session_state.character = "洒脱，自信，聪明"

system_prompt = f"你是一个武侠小说内的{st.session_state.name}，是一个{st.session_state.character}的角色，你的任务是根据用户的问题，生成一个符合该角色人物性格的回复"

print(system_prompt)

st.title("武侠智能体")
st.write("这里是介绍/说明")

# 展示历史消息
for message in st.session_state.messages:
    if message["role"] == "assistant":
        st.chat_message("assistant").write(message["content"])
    else:
        st.chat_message("user").write(message["content"])


#聊天消息输入框
prompt = st.chat_input("请输入你的问题")
if prompt:
    print(f"---------收到用户消息：{prompt}---------")
    st.chat_message("user").write(prompt)
    #保存用户消息方便重新加载后再展示
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="deepseek-r1:8b",
        messages=[
            {"role": "system", "content": system_prompt},
            *st.session_state.messages # 展开所有消息 列表解包操作
        ],
        stream=True
    )
    # print(f"---------收到模型回复：{response.choices[0].message.content}---------")

    # 流式输出模型回复
    result = ""
    response_msg = st.empty() # 空容器，用于存储模型回复
    for chunk in response:
        if chunk.choices[0].delta.content != "":
            result+=chunk.choices[0].delta.content
            response_msg.chat_message("assistant").write(result)

    # 非流式输出模型回复
    #st.chat_message("assistant").write(response.choices[0].message.content)
    #保存模型回复方便重新加载后再展示
    st.session_state.messages.append({"role": "assistant", "content": result})


with st.sidebar:
    st.header("会话管理")

    if st.button("新建会话", use_container_width=True):
        #保存当前会话信息，并新建会话
        st.session_state.session_id += 1
        st.session_state.messages = []
        st.rerun()


    st.text("历史会话")
    sessions = list_sessions()
    for session in sessions:
        col_open, col_close = st.columns([5, 1], vertical_alignment="center")
        with col_open:
            st.button(f"会话 {session}", key=f"open_{session}", use_container_width=True)
        with col_close:
            st.button("关闭", key=f"close_{session}")

    # 角色姓名输入框
    role_name = st.text_input("角色姓名")
    st.session_state.name = role_name

    # 角色性格输入框
    role_character = st.text_input("角色性格")
    st.session_state.character = role_character
