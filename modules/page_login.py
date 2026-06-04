import streamlit as st
from modules.auth import login
from modules.ui_components import inject_css

def show_login_page():
    inject_css()
    st.markdown("""
    <style>
    .login-wrapper {
        display: flex; align-items: center; justify-content: center;
        min-height: 100vh; padding: 20px;
    }
    .login-box {
        background: #ffffff;
        border-radius: 20px;
        padding: 48px 44px;
        width: 100%; max-width: 420px;
        box-shadow: 0 20px 60px rgba(9,30,66,0.18), 0 0 0 1px rgba(9,30,66,0.06);
        margin: 0 auto;
    }
    .login-logo {
        font-size: 28px; font-weight: 800;
        color: #0052cc; letter-spacing: -1px;
        margin-bottom: 6px;
    }
    .login-subtitle {
        font-size: 14px; color: #5e6c84;
        margin-bottom: 32px;
    }
    .login-label {
        font-size: 12px; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.6px; color: #344563; margin-bottom: 6px;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="height:40px"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="login-box">
            <div class="login-logo">⚡ KanbanPro</div>
            <div class="login-subtitle">Sistema de Gestão Corporativa</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown('<div class="login-label">Usuário</div>', unsafe_allow_html=True)
            login_input = st.text_input("", placeholder="Digite seu login", label_visibility="collapsed")
            st.markdown('<div class="login-label" style="margin-top:16px">Senha</div>', unsafe_allow_html=True)
            password_input = st.text_input("", placeholder="Digite sua senha", type="password", label_visibility="collapsed")
            st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
            submitted = st.form_submit_button("Entrar", use_container_width=True)

            if submitted:
                if not login_input or not password_input:
                    st.error("Preencha todos os campos.")
                else:
                    user = login(login_input.strip(), password_input)
                    if user:
                        st.session_state.user = user
                        st.session_state.page = "boards"
                        st.rerun()
                    else:
                        st.error("Login ou senha incorretos.")

        st.markdown("""
        <div style="text-align:center;margin-top:24px;font-size:12px;color:#97a0af">
            KanbanPro © 2025 · Gestão Corporativa
        </div>
        """, unsafe_allow_html=True)
