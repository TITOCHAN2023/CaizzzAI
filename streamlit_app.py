import streamlit as st
from streamlit import session_state
import requests


def main():
    st.title("CaizzzAI")
    if "token" not in session_state:
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
        st.switch_page("pages/CaizzzAI.py")


if __name__ == "__main__":
    main()