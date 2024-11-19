import streamlit as st

st.set_page_config(page_title="CaizzzAI", page_icon="🧊", layout="wide"
                   , initial_sidebar_state="expanded")

st.title("CaizzzAI Settings")

st.text_input("API Key", value=st.session_state["OPENAI_API_KEY"], max_chars=None, key=None, type='default')