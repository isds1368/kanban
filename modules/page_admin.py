import streamlit as st
from modules.auth import get_current_user, require_role, get_all_users, create_user, update_user, deactivate_user, change_password
from modules.ui_components import page_header, ROLE_LABELS
from modules.backup import create_backup, list_backups
from modules.database import get_connection
import os

def show_admin_page():
    user = get_current_user()
    if not require_role("administrador"):
        st.error("🚫 Acesso negado. Apenas administradores podem acessar esta área.")
        return

    page_header("⚙️ Administração", "Gestão de usuários, sistema e configurações")

    tab1, tab2, tab3, tab4 = st.tabs(["👥 Usuários", "💾 Backup", "📊 Logs", "🔧 Sistema"])

    # ===== USERS =====
    with tab1:
        st.markdown("### Usuários do Sistema")

        with st.expander("➕ Criar Novo Usuário", expanded=False):
            with st.form("create_user_form"):
                uc1, uc2 = st.columns(2)
                with uc1:
                    u_name = st.text_input("Nome Completo*")
                    u_login = st.text_input("Login*")
                    u_password = st.text_input("Senha*", type="password")
                with uc2:
                    u_role = st.selectbox("Perfil", ["colaborador","gestor","leitor","administrador"],
                        format_func=lambda x: ROLE_LABELS[x])
                    u_sector = st.text_input("Setor")
                    u_position = st.text_input("Cargo")

                if st.form_submit_button("👤 Criar Usuário", use_container_width=True):
                    if u_name and u_login and u_password:
                        ok, msg = create_user(u_name, u_login, u_password, u_role, u_sector, u_position)
                        if ok:
                            st.success(f"✅ {msg}")
                            st.rerun()
                        else:
                            st.error(f"Erro: {msg}")
                    else:
                        st.error("Nome, login e senha são obrigatórios.")

        # Users list
        users = get_all_users()
        st.markdown(f"**{len(users)} usuário(s) ativo(s)**")

        role_colors = {
            "administrador": "#de350b",
            "gestor": "#6554c0",
            "colaborador": "#0052cc",
            "leitor": "#97a0af",
        }

        for u in users:
            with st.expander(f"{'🔴' if u['role']=='administrador' else '🟣' if u['role']=='gestor' else '🔵' if u['role']=='colaborador' else '⚪'} {u['name']} — {ROLE_LABELS.get(u['role'],u['role'])} | {u.get('sector','') or 'Sem setor'}", expanded=False):
                ec1, ec2 = st.columns(2)
                with ec1:
                    st.markdown(f"""
                    <div style="font-size:12px;color:#5e6c84;line-height:2">
                        <b>Login:</b> {u['login']}<br>
                        <b>Setor:</b> {u.get('sector','—')}<br>
                        <b>Cargo:</b> {u.get('position','—')}<br>
                        <b>Último acesso:</b> {u.get('last_login','Nunca') or 'Nunca'}
                    </div>
                    """, unsafe_allow_html=True)

                with ec2:
                    with st.form(f"edit_user_{u['id']}"):
                        en_name = st.text_input("Nome", value=u["name"])
                        en_role = st.selectbox("Perfil", ["colaborador","gestor","leitor","administrador"],
                            index=["colaborador","gestor","leitor","administrador"].index(u["role"]),
                            format_func=lambda x: ROLE_LABELS[x])
                        en_sector = st.text_input("Setor", value=u.get("sector",""))
                        en_position = st.text_input("Cargo", value=u.get("position",""))
                        en_pass = st.text_input("Nova senha (deixe em branco para manter)", type="password")

                        bc1, bc2 = st.columns(2)
                        with bc1:
                            if st.form_submit_button("💾 Salvar", use_container_width=True):
                                update_user(u["id"], en_name, en_role, en_sector, en_position)
                                if en_pass:
                                    change_password(u["id"], en_pass)
                                st.success("Salvo!")
                                st.rerun()
                        with bc2:
                            if u["id"] != user["id"]:
                                if st.form_submit_button("🗑️ Desativar", use_container_width=True):
                                    deactivate_user(u["id"])
                                    st.rerun()

    # ===== BACKUP =====
    with tab2:
        st.markdown("### 💾 Backup do Sistema")

        if st.button("🔄 Criar Backup Agora", use_container_width=False):
            with st.spinner("Criando backup..."):
                path = create_backup()
                st.success(f"✅ Backup criado: {os.path.basename(path)}")

        st.markdown("---")
        st.markdown("**Backups disponíveis:**")
        backups = list_backups()
        if not backups:
            st.info("Nenhum backup encontrado.")
        else:
            for bk in backups:
                bc1, bc2, bc3 = st.columns([4,2,1])
                with bc1:
                    st.markdown(f"📦 **{bk['name']}**")
                with bc2:
                    st.markdown(f"<span style='font-size:12px;color:#5e6c84'>{bk['created']} · {bk['size']//1024}KB</span>",
                                unsafe_allow_html=True)
                with bc3:
                    with open(bk["path"], "rb") as f:
                        st.download_button("⬇️", f, file_name=bk["name"], mime="application/zip",
                                           key=f"dl_{bk['name']}")

    # ===== LOGS =====
    with tab3:
        st.markdown("### 📊 Logs do Sistema")
        conn = get_connection()
        logs = conn.execute("""
            SELECT l.*, u.name as user_name FROM system_logs l
            LEFT JOIN users u ON l.user_id = u.id
            ORDER BY l.created_at DESC LIMIT 200
        """).fetchall()
        conn.close()

        action_filter = st.selectbox("Filtrar ação", ["todas","login","logout","criação de tarefa","alteração","exclusão"])

        action_icons = {"login":"🔐","logout":"🚪","criação":"🆕","alteração":"✏️","exclusão":"🗑️","movimentação":"🔄"}

        for log in logs:
            action = log["action"] or ""
            if action_filter != "todas" and action_filter not in action.lower():
                continue
            icon = action_icons.get(action.lower().split()[0] if action else "", "📌")
            st.markdown(f"""
            <div style="display:flex;gap:10px;align-items:flex-start;padding:8px 0;border-bottom:1px solid #edf0f7;font-size:12px">
                <span style="font-size:14px">{icon}</span>
                <div style="flex:1">
                    <span style="font-weight:600;color:#172b4d">{log.get('user_name','Sistema')}</span>
                    <span style="color:#5e6c84"> — {action}</span>
                    {f'<span style="color:#97a0af"> · {log["detail"][:80]}</span>' if log.get("detail") else ""}
                </div>
                <span style="color:#c1c7d0;white-space:nowrap">{log['created_at'][:16]}</span>
            </div>
            """, unsafe_allow_html=True)

    # ===== SYSTEM =====
    with tab4:
        st.markdown("### 🔧 Informações do Sistema")
        from modules.database import DB_PATH
        db_size = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
        conn2 = get_connection()
        total_cards = conn2.execute("SELECT COUNT(*) FROM cards").fetchone()[0]
        total_users = conn2.execute("SELECT COUNT(*) FROM users WHERE active=1").fetchone()[0]
        total_boards = conn2.execute("SELECT COUNT(*) FROM boards WHERE archived=0").fetchone()[0]
        conn2.close()

        ic1, ic2, ic3, ic4 = st.columns(4)
        with ic1: st.metric("Banco de Dados", f"{db_size//1024}KB")
        with ic2: st.metric("Usuários Ativos", total_users)
        with ic3: st.metric("Quadros", total_boards)
        with ic4: st.metric("Total de Cards", total_cards)

        st.markdown("---")
        st.markdown("**Caminho do banco de dados:**")
        st.code(DB_PATH)
        st.markdown("**Versão:** KanbanPro v1.0.0")
        st.markdown("**Framework:** Streamlit + SQLite")
