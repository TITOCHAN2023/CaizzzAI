import datetime
import streamlit as st
import requests
import json

# st.title("CaizzzAI-未开放，仅测试阶段")
_ip="localhost"
_port=8000
ABOUT = """\
### CaizzzAI is a project of providing private llm api and webui service
#### Author: [Caizzz](https://titochan.top)
#### Tech Stack
##### LLM fine-tuning:
- Transformers
- PEFT
- Pytorch
- Deepspeed
##### LLM deployment:
- Openai-api
- llama.cpp(in future)
- llama-cpp-python(in future)
##### LLM service:
- Langchain
- FAISS
##### API backend:
- Fastapi
- Sqlalchemy
- Mysql
- Redis
##### WebUI:
- Streamlit
"""
st.set_page_config(
        page_title="CaizzzAI-未开放，仅测试阶段",
        page_icon="🤖",
        layout= "centered",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": "https://github.com/TITOCHAN2023/CaizzzAI/README.md",
            "Report a bug": "https://github.com/TITOCHAN2023/CaizzzAI/issues/new",
            "About": ABOUT,
        },
    )
st.title("CaizzzAI-未开放，仅测试阶段")


def sidebar():
    st.sidebar.title("CaizzzAI")
# 登录
if 'token' not in st.session_state:
    st.session_state['token'] = ''
if 'sessionname' not in st.session_state:
    st.session_state['sessionname'] = ''
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

if st.session_state['token'] == '':
    with st.form("login_form"):
        st.write("请登录")
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        submitted = st.form_submit_button("登录")
        if submitted:
            login_url = f"http://{_ip}:{_port}/root/login"
            payload = {
                "username": username,
                "password": password
            }
            response = requests.post(login_url, json=payload)
            if response.status_code == 200:
                st.success("登录成功")
                st.session_state['token'] = response.json()['token']
                st.rerun()  # 重新运行脚本，跳转到聊天页面
            else:
                st.error("登录失败")
else:
    headers = {
        "Authorization": st.session_state['token']
    }
    # 会话管理
    st.sidebar.write("会话管理")
    # 获取会话列表
    session_list_url = f"http://{_ip}:{_port}/v1/session/sessionlist?page_id=0&page_size=100"
    response = requests.get(session_list_url, headers=headers)
    if response.status_code == 200:
        sessions = response.json()['data']['session_list']
        session_names = [session['sessionname'] for session in sessions]
        st.session_state['sessionname'] = st.sidebar.selectbox("选择会话", session_names)
    else:
        st.error("无法获取会话列表")

    # 创建新会话
    new_sessionname = st.sidebar.text_input("新建会话名称")
    if st.sidebar.button("创建会话"):
        create_session_url = f"http://{_ip}:{_port}/v1/session"
        payload = {
            "sessionname": new_sessionname
        }
        response = requests.post(create_session_url, headers=headers, json=payload)
        if response.status_code == 200:
            st.success(f"会话 '{new_sessionname}' 创建成功")
            st.rerun()  # 重新运行脚本，刷新会话列表
        else:
            st.error("创建会话失败")

    # 删除会话
    if st.sidebar.button("删除当前会话"):
        delete_session_url = f"http://{_ip}:{_port}/v1/session/{st.session_state['sessionname']}/delete"
        response = requests.delete(delete_session_url, headers=headers)
        if response.status_code == 200:
            st.success(f"会话 '{st.session_state['sessionname']}' 删除成功")
            st.rerun()  # 重新运行脚本，刷新会话列表
        else:
            st.error("删除会话失败")
    
    

    # 获取并显示历史记录
    history_url = f"http://{_ip}:{_port}/v1/session/{st.session_state['sessionname']}"
    response = requests.get(history_url, headers=headers)
    if response.status_code == 200:
        msg = response.json()
        data = msg['data']
        if 'history' in data:
            history = data['history']
            st.session_state['messages'] = []
            for item in history:
                st.session_state['messages'].append((item['usermessage'], item['botmessage']))
                st.session_state['api_key'] = item['user_api_key']
                st.session_state['base_url'] = item['user_base_url']
                st.session_state['llm_model'] = item['llm_model']
        else:
            st.error("历史记录中没有找到 'history' 键")
    else:
        st.error("无法获取历史记录")

    st.session_state['llm_model'] = st.sidebar.text_input("模型:", key="llm_model_input")
    st.session_state['api_key'] = st.sidebar.text_input("API Key:", key="api_key_input")
    st.session_state['base_url']= st.sidebar.text_input("Base URL:", key="base_url_input")
    st.session_state['temp_input'] = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.05)

    vdb_on=st.sidebar.toggle("知识库",False)

    if vdb_on:

        get_vdb_url = f"http://{_ip}:{_port}/v1/vdb/getvdblist"
        response = requests.get(get_vdb_url, headers=headers)
        if response.status_code == 200:
            vdb_list = response.json()['data']['vdb_list']
            vdb_names = [vdb['name'] for vdb in vdb_list]
            st.session_state['vdb_name'] = st.sidebar.selectbox("选择知识库", vdb_names)
        else:
            st.error("无法获取知识库列表")

        new_vdb_name = st.sidebar.text_input("新建知识库名称")#未完成
        if st.sidebar.button("创建知识库"):
            create_vdb_url = f"http://{_ip}:{_port}/v1/vdb"
            payload = {
                "name": new_vdb_name
            }
            response = requests.post(create_vdb_url, headers=headers, json=payload)
            if response.status_code == 200:
                st.success(f"知识库 '{new_vdb_name}' 创建成功")
                st.rerun()
            else:
                st.error("创建知识库失败")

        vdb_model=st.sidebar.text_input("嵌入模型")
        uploaded_file = st.sidebar.file_uploader("选择一个文件", type=["txt", "xlsx", "docx", "pdf"])
        if uploaded_file is not None:
            # # 显示文件信息
            # st.write(f"文件名: {uploaded_file.name}")
            # st.write(f"文件大小: {uploaded_file.size} bytes")

            # 上传文件到 FastAPI 后端
            if st.sidebar.button("上传文件"):
                with st.spinner("上传中..."):
                    payload = {
                        "embedding_model": vdb_model,
                        "api_key": str(st.session_state['api_key']),
                        "base_url": str(st.session_state['base_url']),
                    }
                    files = {
                        "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
                    }
                    response = requests.post(
                        f"http://{_ip}:{_port}/v1/vdb/{st.session_state['vdb_name']}/uploadfile",
                        headers=headers,
                        data=payload,
                        files=files
                    )
                    if response.status_code == 200:
                        st.sidebar.success(response.json()["data"]["info"])
                    else:
                        st.sidebar.error("文件上传失败！")
    
    st.title("💬 CaizzzAI")
    st.caption("🚀 powered by TitoChan")
    # 初始化一个占位符，用于实时显示机器人的回复
    for usermessage, botmessage in st.session_state['messages']:
        st.chat_message("user").write(usermessage)
        st.chat_message("assistant").write(botmessage)
    

    

    if user_input := st.chat_input():
        if user_input:
            # 展示用户输入
            st.session_state.messages.append(("你", user_input))

            # 向后端发送请求，获取流式响应
            chat_url = f"http://{_ip}:{_port}/v1/session/{st.session_state['sessionname']}/chat"
            payload = {
                "llm_model": str(st.session_state['llm_model']),
                "temperature": st.session_state['temp_input'],
                "api_key": str(st.session_state['api_key']),
                "base_url": str(st.session_state['base_url']),
                "message": user_input,
                "vdb_name": None if not vdb_on else str(st.session_state['vdb_name'])
            }
            response = requests.post(chat_url, headers=headers, json=payload, stream=True)

            
            st.chat_message("user").write(user_input)
            message_placeholder_bot = st.empty()
            bot_response = ''
            response = requests.post(chat_url, headers=headers, json=payload, stream=True)
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    print(f"get:{decoded_line}")
                    if decoded_line.startswith('data: '):
                        decoded_line = decoded_line[len('data: '):]
                    if decoded_line.strip() == '[DONE]':
                        break
                    try:
                        data = json.loads(decoded_line)
                        content = data.get('content', '')
                        bot_response += content
                        message_placeholder_bot.markdown("...:"+bot_response)
                        
                    except json.JSONDecodeError as e:
                        print(f"JSON 解析错误：{e}")
                        continue
            message_placeholder_bot.empty()
            st.chat_message("assistant").write(bot_response)
            st.session_state.messages.append((user_input, bot_response))

            