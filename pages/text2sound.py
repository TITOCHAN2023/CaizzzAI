import streamlit as st
import requests

from env import TTS_URL
tts_url=TTS_URL



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



# 设置页面标题
def config():


    global headers
    headers= {"Authorization": st.session_state['token']}
    st.title("CaizzzAI-Text2Sound")
    st.write("ONLY FOR TEST not open yet")


def siderbar():
    st.sidebar.title("CaizzzAI")
    st.sidebar.markdown("### use chat's api_key and base_url")
    st.sidebar.markdown("login in chat page first")

    uploaded_file = st.sidebar.file_uploader("choose ur own voice ", type=[".mp3", ".wav"])
    voice_name = st.sidebar.text_input("voice name (make it as a password)", key="voice_name")
    
    if st.sidebar.button("upload"):
        if uploaded_file is not None:
            st.write(f"uploading {uploaded_file.name}  as {voice_name}")
            files = {"files": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            
            tts_ip_port = tts_url.split("/")[2]

            url=f"http://{tts_ip_port}/root/upload/{voice_name}"
            response = requests.post(url, headers=headers,  files=files)
            if response.status_code == 200:
                st.sidebar.success(response.json()["message"])
        else:
            st.write("Please add a file first")

    

def body():


    voice_1=st.text_input("voice name", key="voice")
    st.write("for example: Person1, Person2, Person3")


    
    text=st.text_input("text", key="text")


    if st.button("Generate Sound"):
        if 'token' in st.session_state:

            st.markdown(f"### Person1: ")
            st.markdown(f" {text}")
            requestsdata = {
                    "voicename": voice_1,
                    "content": text,
                }
            response = requests.post(tts_url, data=requestsdata)
            jsonresponse1 = response.json()
            st.audio(jsonresponse1['url'])
        else:
            st.markdown("Please login in chat page first")




        

def main():

    if 'token' not in st.session_state:
        st.switch_page("pages/chat.py")
    config()
    siderbar()
    body()

if __name__ == "__main__":
    main()
