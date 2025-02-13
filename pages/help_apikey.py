import streamlit as st
import requests

import os
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
    st.title("CaizzzAI-API Document")
    st.write("ONLY FOR TEST not open yet")

    


def siderbar():
    st.sidebar.title("CaizzzAI")
    st.sidebar.markdown("### use chat's api_key and base_url")
    st.sidebar.markdown("login in chat page first")


    

def body():
    # Main chat interface
    st.title("💬 CaizzzAI")
    st.caption("🚀 powered by TitoChan")
    st.caption("Free Plan : 50000 tokens for deepseek")
    st.caption("Model: deepseek-v3 deepseek-r1 gpt-4o-mini ...")
    st.caption(f"Your Api Key: {st.session_state['key'] if 'key' in st.session_state.keys() else 'login in chat page first'}")
    st.caption("Base URL: https://api.titochan.top/v1")

    st.markdown("Method CURL:")
    st.code('''
curl --location 'https://api.titochan.top/v1/chat/completions' \
        
--header 'Content-Type: application/json' \
            
--header 'Authorization: Bearer sk-5xxxx' \
            
--data '{
    "messages": [
        {"role": "user", "content": "你是谁"}
    ],
    "stream": false,
    "model": "deepseek-r1",
    "temperature": 0.5,
    "presence_penalty": 0,
    "frequency_penalty": 0,
    "top_p": 1
  }'
  ''')
    st.markdown("Method Python:")
    st.code('''
from openai import OpenAI

url = 'https://api.titochan.top/v1'
llm_api_key = 'your llm_api_key'

client = OpenAI(
    base_url=url,
    api_key=llm_api_key
)

# 发送带有流式输出的请求
content = ""
messages = [
    {"role": "user", "content": "你是谁"}
]
response = client.chat.completions.create(
    model="deepseek-v3",
    messages=messages,
    stream=True,  # 启用流式输出
    max_tokens=4096
)
# 逐步接收并处理响应
for chunk in response:
    if chunk.choices[0].delta.content:
        content += chunk.choices[0].delta.content

print(content)

# Round 2
messages.append({"role": "assistant", "content": content})
messages.append({'role': 'user', 'content': "继续"})
response = client.chat.completions.create(
    model="deepseek-v3",
    messages=messages,
    stream=True
)
for chunk in response:
    if chunk.choices[0].delta.content:
        content += chunk.choices[0].delta.content

print(content)

  ''')


    




        

def main():
    # Page configuration
    st.set_page_config(
        page_title="CaizzzAI-ONLY FOR TEST not open yet",
        page_icon="static/img/logo.png",
        layout="centered",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": "https://github.com/TITOCHAN2023/CaizzzAI/README.md",
            "Report a bug": "https://github.com/TITOCHAN2023/CaizzzAI/issues/new",
            "About": ABOUT,
        },
    )
    if 'token' not in st.session_state:
        st.switch_page("pages/chat.py")
    config()
    siderbar()
    body()

if __name__ == "__main__":
    main()
