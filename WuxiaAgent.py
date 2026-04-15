import streamlit as st
import os
from openai import OpenAI
import json
import datetime

# 列出所有历史会话信息
def list_sessions():
    sessions = []
    for file in os.listdir("session"):
        if file.endswith(".json"):
            try:
                with open(f"session/{file}", "r") as f:
                    session = json.load(f)
                    sessions.append(session)
            except FileNotFoundError:
                print(f"会话文件 {file} 不存在")
            except json.JSONDecodeError:
                print(f"会话文件 {file} 格式错误，跳过加载")
            except Exception as e:
                print(f"会话文件 {file} 读取错误：{e}")
    return sessions

# 加载历史会话信息
def load_session(session_id):
    # 如果文件不存在，返回 None
    if not os.path.exists(f"session/{session_id}.json"):
        return None
    try:
        with open(f"session/{session_id}.json", "r") as f:
            session_data = json.load(f)
            return session_data
    except FileNotFoundError:
        print(f"会话文件 {session_id} 不存在")
        return None
    except json.JSONDecodeError:
        print(f"会话文件 {session_id} 格式错误，跳过加载")
        return None
    except Exception as e:
        print(f"会话文件 {session_id} 读取错误：{e}")
        return None


# 保存当前会话信息
def save_session(session_state):
    # 检查会话目录是否存在
    if not os.path.exists("session"):
        os.makedirs("session")

    session_data = {
        "name": session_state.name,
        "character": session_state.character,
        "messages": session_state.messages,
        "session_id": session_state.current_session_id,
    }
    # 保存当前会话信息
    with open(f"session/{session_state.current_session_id}.json", "w") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=4)

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
if "current_session_id" not in st.session_state or st.session_state.current_session_id == "":
    # 系统时间作为会话id
    st.session_state.current_session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
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
        #保存当前会话信息，包括角色姓名、角色性格、历史消息、会话id
        save_session(st.session_state)

        # 新建会话，清空历史消息
        # 清空角色姓名、角色性格 不需要，输入框的数据不会清空
        # st.session_state.name = ""
        # st.session_state.character = ""
        st.session_state.messages = []
        st.session_state.current_session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        #save_session(st.session_state.current_session_id, session_data)
        # 刷新页面，展示新会话
        st.rerun()


    st.text("历史会话")
    history_sessions = list_sessions()
    for session in history_sessions:
        col_open, col_close = st.columns([5, 1], vertical_alignment="center")
        with col_open:
           # 展示历史会话信息
           if  st.button(f"会话 {session['session_id']}", key=f"open_{session['session_id']}", use_container_width=True):
                # 保存当前会话信息
                save_session(st.session_state)
                # 加载历史会话信息
                session_data = load_session(session['session_id'])
                if session_data:
                    # 更新当前会话状态信息
                    st.session_state.name = session_data["name"]
                    st.session_state.character = session_data["character"]
                    st.session_state.current_session_id = session_data['session_id']
                    st.session_state.messages = session_data["messages"]
                    # 刷新页面，展示新会话
                st.rerun()


        with col_close:
            if st.button("关闭", key=f"close_{session['session_id']}"):
                st.session_state.name = ""
                st.session_state.character = ""
                st.session_state.messages = []
                st.session_state.current_session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                # 刷新页面，展示新会话
                st.rerun()

    # 角色姓名输入框
    role_name = st.text_input("角色姓名")
    st.session_state.name = role_name

    # 角色性格输入框
    role_character = st.text_input("角色性格")
    st.session_state.character = role_character
