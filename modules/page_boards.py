import streamlit as st
from modules.auth import get_current_user, require_role
from modules.board_ops import get_boards_for_user, create_board, archive_board, get_dashboard_stats
from modules.ui_components import page_header, inject_css

BOARD_COLORS = ["#0052cc","#00875a","#ff5630","#6554c0","#ff991f","#00b8d9","#172b4d","#de350b"]

def show_boards_page():
    user = get_current_user()
    boards = get_boards_for_user(user["id"], user["role"])

    page_header("Meus Quadros", f"Bem-vindo, {user['name'].split()[0]}! Selecione um quadro para continuar.")

    # Stats quick view
    stats = get_dashboard_stats()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total de Tarefas", stats["total"])
    with c2:
        st.metric("Em Aberto", stats["open"])
    with c3:
        st.metric("Concluídas", stats["done"])
    with c4:
        st.metric("⚠️ Atrasadas", stats["overdue"])

    st.markdown("---")

    # Create board button
    if require_role("administrador", "gestor"):
        with st.expander("➕ Criar Novo Quadro", expanded=False):
            with st.form("new_board_form"):
                col1, col2 = st.columns([3,1])
                with col1:
                    bname = st.text_input("Nome do Quadro*")
                    bdesc = st.text_area("Descrição", height=80)
                with col2:
                    bcolor = st.selectbox("Cor", BOARD_COLORS,
                        format_func=lambda c: c)
                if st.form_submit_button("Criar Quadro", use_container_width=True):
                    if bname:
                        board_id = create_board(bname, bdesc, bcolor, user["id"])
                        st.success(f"Quadro '{bname}' criado!")
                        st.rerun()
                    else:
                        st.error("Nome é obrigatório.")

    st.markdown("### 📋 Quadros Disponíveis")

    if not boards:
        st.info("Nenhum quadro disponível. Crie um novo quadro acima.")
        return

    # Board grid
    cols_per_row = 3
    for i in range(0, len(boards), cols_per_row):
        row_boards = boards[i:i+cols_per_row]
        cols = st.columns(cols_per_row)
        for j, board in enumerate(row_boards):
            with cols[j]:
                board_stats = get_dashboard_stats(board["id"])
                bcolor = board.get("color", "#0052cc")

                st.markdown(f"""
                <div style="
                    background:#fff;
                    border-radius:16px;
                    overflow:hidden;
                    box-shadow:0 2px 8px rgba(9,30,66,0.12);
                    border:1px solid #dde2f0;
                    margin-bottom:16px;
                    transition:all 0.2s;
                ">
                    <div style="background:{bcolor};height:8px;"></div>
                    <div style="padding:20px">
                        <div style="font-size:16px;font-weight:800;color:#172b4d;margin-bottom:4px">{board['name']}</div>
                        <div style="font-size:12px;color:#5e6c84;margin-bottom:16px;min-height:18px">
                            {board.get('description') or 'Sem descrição'}
                        </div>
                        <div style="display:flex;gap:12px;font-size:12px;color:#5e6c84">
                            <span>📋 {board_stats['total']} tarefas</span>
                            <span style="color:#00875a">✅ {board_stats['done']}</span>
                            {'<span style="color:#de350b">⚠️ ' + str(board_stats['overdue']) + ' atrasadas</span>' if board_stats['overdue'] else ''}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                btn_col1, btn_col2 = st.columns([3,1])
                with btn_col1:
                    if st.button(f"📂 Abrir", key=f"open_{board['id']}", use_container_width=True):
                        st.session_state.current_board = board["id"]
                        st.session_state.page = "kanban"
                        st.rerun()
                with btn_col2:
                    if require_role("administrador") and st.button("🗄️", key=f"arch_{board['id']}", help="Arquivar"):
                        archive_board(board["id"])
                        st.rerun()
