import base64
import streamlit as st
import requests
import json

from dotenv import load_dotenv
import os
load_dotenv()
tts_url = os.environ.get("TTS_URL")

allowed_extensions = [".txt", ".pdf", ".docx", ".xlsx",".htm","html"]


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
def config():
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

    st.title("CaizzzAI")
    st.write("ONLY FOR TEST not open yet")


    # Session state initialization
    if 'token' not in st.session_state:
        st.session_state['token'] = ''
    if 'sessionname' not in st.session_state:
        st.session_state['sessionname'] = ''
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    if 'avatar' not in st.session_state:
        st.session_state['avatar'] = '🦖'
    st.session_state["assistant"] = "static/img/Isshiki.png"

# Functions
def sidebar_bg(side_bg):
    st.sidebar.title("CaizzzAI")
    side_bg_ext = 'png'
    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"] > div:first-child {{
            background: url(data:image/{side_bg_ext};base64,{base64.b64encode(open(side_bg, "rb").read()).decode()});
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def body_bg():
    # Login form
    if st.session_state['token'] == '':
        with st.form("login_form"):
            st.write("Please login to continue")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                login_url = f"http://{_IP}:{_PORT}/root/login"
                payload = {"username": username, "password": password}
                response = requests.post(login_url, json=payload)
                if response.status_code == 200:
                    st.success("Login successful")
                    st.session_state['token'] = response.json()['token']
                    st.session_state['avatar'] = response.json()['avatar']
                    st.rerun()
                else:
                    st.error("Failed to login")
    else:
        headers = {"Authorization": st.session_state['token']}
        st.sidebar.header("CaizzzAI")
        st.sidebar.write("ONLY FOR TEST not open yet")
        st.sidebar.write("Select a session to continue")

        # Session management
        session_list_url = f"http://{_IP}:{_PORT}/v1/session/sessionlist?page_id=0&page_size=100"
        response = requests.get(session_list_url, headers=headers)
        if response.status_code == 200:
            sessions = response.json()['data']['session_list']
            session_names = [session['sessionname'] for session in sessions]
            st.session_state['sessionname'] = st.sidebar.selectbox("Select Session", session_names)
        else:
            st.error("Failed to fetch session list")

        # Create new session
        new_sessionname = st.sidebar.text_input("Create New Session")
        if st.sidebar.button("Create Session"):
            create_session_url = f"http://{_IP}:{_PORT}/v1/session"
            payload = {"sessionname": new_sessionname}
            response = requests.post(create_session_url, headers=headers, json=payload)
            if response.status_code == 200:
                st.success(f"Session '{new_sessionname}' created successfully")
                st.rerun()
            else:
                st.error("Failed to create session")

        # Delete session
        if st.sidebar.button("Delete Current Session"):
            delete_session_url = f"http://{_IP}:{_PORT}/v1/session/{st.session_state['sessionname']}/delete"
            response = requests.delete(delete_session_url, headers=headers)
            if response.status_code == 200:
                st.success(f"Session '{st.session_state['sessionname']}' deleted successfully")
                st.rerun()
            else:
                st.error("Failed to delete session")

        # Fetch and display history
        history_url = f"http://{_IP}:{_PORT}/v1/session/{st.session_state['sessionname']}"
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
                st.error("Could not find 'history' in response")
        else:
            st.error("Failed to fetch history")

        # Sidebar inputs
        st.sidebar.header("Settings")
        st.sidebar.write("Left blank is the default value")
        st.session_state['llm_model'] = st.sidebar.text_input("LLM Model:", key="llm_model_input")
        st.session_state['api_key'] = st.sidebar.text_input("API Key:", key="api_key_input")
        st.session_state['base_url'] = st.sidebar.text_input("Base URL:", key="base_url_input")
        st.session_state['temp_input'] = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.05)

        vdb_on = st.sidebar.toggle("Knowledge Base", False)

        if vdb_on:
            get_vdb_url = f"http://{_IP}:{_PORT}/v1/vdb/getvdblist"
            response = requests.get(get_vdb_url, headers=headers)
            if response.status_code == 200:
                vdb_list = response.json()['data']['vdb_list']
                vdb_names = [vdb['name'] for vdb in vdb_list]
                st.session_state['vdb_name'] = st.sidebar.selectbox("Select a Knowledge Base", vdb_names)
            else:
                st.error("Failed to fetch knowledge base list")

            new_vdb_name = st.sidebar.text_input("Create a New Knowledge Base")
            if st.sidebar.button("Create Knowledge Base"):
                create_vdb_url = f"http://{_IP}:{_PORT}/v1/vdb"
                payload = {"name": new_vdb_name}
                response = requests.post(create_vdb_url, headers=headers, json=payload)
                if response.status_code == 200:
                    st.success(f"Knowledge base '{new_vdb_name}' created successfully")
                    st.rerun()
                else:
                    st.error("Failed to create knowledge base")

            vdb_model = st.sidebar.text_input("Embedding Model")
            uploaded_file = st.sidebar.file_uploader("Select a File", type=allowed_extensions)
            if uploaded_file is not None:
                if st.sidebar.button("Upload File"):
                    with st.status("Uploading...", expanded=True) as status:
                        st.write("Preparing model...")
                        payload = {
                            "embedding_model": vdb_model,
                            "api_key": str(st.session_state['api_key']),
                            "base_url": str(st.session_state['base_url']),
                        }
                        st.write("Preparing file...")
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        st.write("Processing upload and embedding into knowledge base...")
                        response = requests.post(
                            f"http://{_IP}:{_PORT}/v1/vdb/{st.session_state['vdb_name']}/uploadfile",
                            headers=headers,
                            data=payload,
                            files=files
                        )
                        if response.status_code == 200:
                            st.sidebar.success(response.json()["data"]["info"])
                        else:
                            st.sidebar.error("File upload failed!")
                            status.update(label="Upload complete!", state="complete", expanded=False)
        
        voice_on = st.sidebar.toggle("Voice", False)
        if voice_on:
            st.session_state['voice'] = st.sidebar.selectbox("Select Voice", ["Person1", "Person2", "Person3", "Person4"])

        # Main chat interface
        st.title("💬 CaizzzAI")
        st.caption("🚀 powered by TitoChan")

        for usermessage, botmessage in st.session_state['messages']:
            st.chat_message("user", avatar=st.session_state['avatar']).write(usermessage)
            st.chat_message("assistant", avatar=st.session_state["assistant"]).write(botmessage)
            if voice_on:
                voice = st.session_state.get('voice', 'Person3')
                
                requestsdata = {
                    "voicename": voice,
                    "content": botmessage,
                }
                response = requests.post(tts_url, data=requestsdata)

                jsonresponse1 = response.json()
                st.audio(jsonresponse1['url'])
            

        if user_input := st.chat_input():
            if user_input:
                st.session_state.messages.append(("You", user_input))
                chat_url = f"http://{_IP}:{_PORT}/v1/session/{st.session_state['sessionname']}/chat"
                payload = {
                    "llm_model": str(st.session_state['llm_model']),
                    "temperature": st.session_state['temp_input'],
                    "api_key": str(st.session_state['api_key']),
                    "base_url": str(st.session_state['base_url']),
                    "message": user_input,
                    "vdb_name": None if not vdb_on else str(st.session_state['vdb_name'])
                }
                response = requests.post(chat_url, headers=headers, json=payload, stream=True)

                st.chat_message("user", avatar=st.session_state["avatar"]).write(user_input)
                message_placeholder_bot = st.empty()
                bot_response = ''
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith('data: '):
                            decoded_line = decoded_line[len('data: '):]
                        if decoded_line.strip() == '[DONE]':
                            break
                        try:
                            data = json.loads(decoded_line)
                            content = data.get('content', '')
                            bot_response += content
                            message_placeholder_bot.markdown("...:" + bot_response)
                        except json.JSONDecodeError as e:
                            continue
                message_placeholder_bot.empty()


            st.chat_message("assistant", avatar=st.session_state["assistant"]).write(bot_response)
            if voice_on:
                voice = st.session_state.get('voice', 'Person3')
                
                requestsdata = {
                    "voicename": voice,
                    "content": bot_response,
                }
                response = requests.post(tts_url, data=requestsdata)

                jsonresponse1 = response.json()
                st.audio(jsonresponse1['url'])



            st.session_state.messages.append((user_input, bot_response))



def main():
    config()
    sidebar_bg('static/img/cat.png')
    body_bg()

if __name__ == "__main__":
    main()





# # CSS styling
# CSS_STYLE = """
#     <style>
#         div[data-testid="stAppDeployButton"] {
#             visibility: hidden;
#             height: 0.5%;
#             position: fixed;
#         }
#         [data-testid="stBaseButton"], [data-testid="stBaseButton-secondary"], [data-testid="stTooltipHoverTarget"] {
#             aspect-ratio: 5 !important;
#             width: 100% !important;
#             height: auto !important;
#         }
#     </style>
# """
# st.markdown(CSS_STYLE, unsafe_allow_html=True)
