import streamlit as st


def check_password():
    """올바른 비밀번호를 입력해야 다음으로 진행할 수 있게 막습니다.
    main.py와 pages/ 안의 모든 페이지에서 공용으로 사용합니다.
    """
    def password_entered():
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("비밀번호", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("비밀번호", type="password", on_change=password_entered, key="password")
        st.error("비밀번호가 틀렸습니다.")
        return False
    else:
        return True