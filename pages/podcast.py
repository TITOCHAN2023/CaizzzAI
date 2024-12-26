import streamlit as st
import requests

from dotenv import load_dotenv
import os
load_dotenv()
tts_url = os.environ.get("TTS_URL")


_IP = "localhost"
_PORT = 8000
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


def upload_file_to_podcast(sessionname, llm_model, base_url, api_key, uploaded_file):
    url = f"http://{_IP}:{_PORT}/v1/podcast/{sessionname}/upload"
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    
    response = requests.post(url, headers=headers,  files=files)
    return response


# 设置页面标题
def config():


    global headers
    headers= {"Authorization": st.session_state['token']}
    st.title("CaizzzAI-Podcast")
    st.write("ONLY FOR TEST not open yet")

    


def siderbar():
    st.sidebar.title("CaizzzAI")
    st.sidebar.markdown("### use chat's api_key and base_url")
    st.sidebar.markdown("login in chat page first")

def body():
    # 创建文件上传组件
    uploaded_file = st.file_uploader("选择一个文件", type=[".txt", ".pdf", ".docx", ".xlsx",".htm","html"])

    


    voice_1=st.selectbox("Select Person1 Voice", ["Person1", "Person2", "Person3", "Person4"])
    voice_2=st.selectbox("Select Person2 Voice", ["Person2", "Person1", "Person3", "Person4"])
    
    # Session management
    session_list_url = f"http://{_IP}:{_PORT}/v1/podcast/sessionlist?page_id=0&page_size=100"
    response = requests.get(session_list_url, headers=headers)

    if response.status_code == 200:
        sessions = response.json()['data']['session_list']
        session_names = [session['sessionname'] for session in sessions]
        st.session_state['sessionname'] = st.sidebar.selectbox("Select Session", session_names)
    else:
        st.error("Failed to fetch session list")



    history_url = f"http://{_IP}:{_PORT}/v1/podcast/{st.session_state['sessionname']}"
    response = requests.get(history_url, headers=headers)
    
    if response.status_code == 200:
        msg = response.json()
        data = msg['data']
        if 'history' in data:
            history = data['history']
            st.session_state['podcast_messages'] = []
            for item in history:
                st.session_state['podcast_messages'].append((item['content_1'], item['content_2']))
        else:
            st.error("Could not find 'history' in response")
    else:
        st.error("Failed to fetch history")


    
    sessionname=st.text_input("Session Name", key="session_name_input")

    if st.button("Upload File"):
        st.write(f"Session Name: {sessionname} llm_model: {st.session_state['llm_model']} base_url: {st.session_state['base_url']} api_key: {st.session_state['api_key']}")
        if uploaded_file is not None  and sessionname:

            # 发送POST请求到后端API
            response = upload_file_to_podcast(sessionname, st.session_state['llm_model'], st.session_state['base_url'], st.session_state['api_key'], uploaded_file)

            if response.status_code == 200:
                msg = response.json()
                data = msg['data']
                if 'history' in data:
                    history = data['history']
                    st.session_state['podcast_messages'] = []
                    for item in history:
                        st.session_state['podcast_messages'].append((item['content_1'], item['content_2']))
                else:
                    st.error("Could not find 'history' in response")
            else:
                st.error("Failed to fetch history")

        else:
            st.error("Make sure to upload a file and provide a session name")

    if st.session_state['podcast_messages']:
        for message in st.session_state['podcast_messages']:

            st.markdown(f"### Person1: ")
            st.markdown(f" {message[0]}")
            requestsdata = {
                    "voicename": voice_1,
                    "content": message[0],
                }
            response = requests.post(tts_url, data=requestsdata)
            jsonresponse1 = response.json()
            st.audio(jsonresponse1['url'])


            st.markdown(f"### Person2: ")
            st.markdown(f" {message[1]}")
            requestsdata = {
                    "voicename": voice_2,
                    "content": message[1],
                }
            response = requests.post(tts_url, data=requestsdata)
            jsonresponse2 = response.json()
            st.audio(jsonresponse2['url'])



        

def main():

    if 'token' not in st.session_state:
        st.switch_page("pages/chat.py")
    config()
    siderbar()
    body()

if __name__ == "__main__":
    main()
