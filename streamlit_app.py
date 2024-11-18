import streamlit as st
import requests
import sseclient
import json

st.title("聊天前端")

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
            login_url = "http://localhost:8000/root/login"
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
    st.write("会话管理")
    # 获取会话列表
    session_list_url = "http://localhost:8000/v1/session/sessionlist?page_id=0&page_size=10"
    response = requests.get(session_list_url, headers=headers)
    if response.status_code == 200:
        sessions = response.json()['data']['session_list']
        session_names = [session['sessionname'] for session in sessions]
        st.session_state['sessionname'] = st.selectbox("选择会话", session_names)
    else:
        st.error("无法获取会话列表")

    # 创建新会话
    new_sessionname = st.text_input("新建会话名称")
    if st.button("创建会话"):
        create_session_url = "http://localhost:8000/v1/session"
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
    if st.button("删除当前会话"):
        delete_session_url = f"http://localhost:8000/v1/session/{st.session_state['sessionname']}/delete"
        response = requests.delete(delete_session_url, headers=headers)
        if response.status_code == 200:
            st.success(f"会话 '{st.session_state['sessionname']}' 删除成功")
            st.rerun()  # 重新运行脚本，刷新会话列表
        else:
            st.error("删除会话失败")

    # 获取并显示历史记录
    history_url = f"http://localhost:8000/v1/session/{st.session_state['sessionname']}"
    response = requests.get(history_url, headers=headers)
    if response.status_code == 200:
        msg = response.json()
        data = msg['data']
        if 'history' in data:
            history = data['history']
            st.session_state['messages'] = []
            for item in history:
                st.session_state['messages'].append((item['usermessage'], item['botmessage'], item['create_at']))
        else:
            st.error("历史记录中没有找到 'history' 键")
    else:
        st.error("无法获取历史记录")

    # 聊天界面
    st.write("开始聊天")
    user_input = st.text_input("你:", key="user_input")
    llm_model_input = st.text_input("模型:", key="llm_model_input")
    api_key_input = st.text_input("API Key:", key="api_key_input")
    base_url_input = st.text_input("Base URL:", key="base_url_input")
    temp_input = st.number_input("温度:", key="temp_input", value=0.5, min_value=0.0, max_value=1.0, step=0.1)
    if st.button("发送"):
        if user_input:
            # 展示用户输入
            st.session_state.messages.append(("你", user_input))
            if llm_model_input == '':
                llm_model_input = 'gpt-4o-mini'
            if api_key_input == '':
                api_key_input = 'sk-SrkteYrb62PmPt0Lo5yyGCaAVSmWlb5zzgiqJ5skf965G4Mr'
            if base_url_input == '':
                base_url_input = 'https://api.openai-proxy.org/v1'
            
            # 向后端发送请求，获取流式响应
            chat_url = f"http://localhost:8000/v1/session/{st.session_state['sessionname']}/chat"
            payload = {
                "llm_model": llm_model_input,
                "temperature": temp_input,
                "api_key": api_key_input,
                "base_url": base_url_input,
                "message": user_input,
                "vector_db_id": None
            }
            response = requests.post(chat_url, headers=headers, json=payload, stream=True)

            bot_response = ''
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    print(f"接收到的行内容：{decoded_line}")
                    if decoded_line.strip() == '[DONE]':
                        break
                    # 去除前缀
                    if decoded_line.startswith('data: '):
                        decoded_line = decoded_line[len('data: '):]
                    try:
                        data = json.loads(decoded_line)
                        content = data.get('content', '')
                        bot_response += content
                    except json.JSONDecodeError as e:
                        print(f"JSON 解析错误：{e}")
                        continue  # 跳过无法解析的行
            st.session_state.messages.append(("usermessage",user_input),("botmessage", bot_response),("create_at", "now"))

    # 显示对话历史
    for usermessage, botmessage, create_at in st.session_state['messages']:
        st.write(f"User:{usermessage}")
        st.write(f"bot:{botmessage}-{create_at}")