import streamlit as st
from modules.auth import get_current_user, require_role
from modules.board_ops import (get_boards_for_user, create_board, archive_board, get_dashboard_stats)
from modules.ui_components import page_header, icon, ICONS

BOARD_COLORS = ["#C0392B","#E67E22","#27AE60","#2980B9","#8E44AD","#16A085","#2C3E50","#D35400"]

def show_boards_page():
    user = get_current_user()
    boards = get_boards_for_user(user["id"], user["role"])
    stats = get_dashboard_stats()

    page_header("Meus Quadros", f"Bem-vindo, {user['name'].split()[0]}! Selecione um quadro para continuar.")

    # KPI row
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total de Tarefas", stats["total"])
    with c2: st.metric("Em Aberto", stats["open"])
    with c3: st.metric("Concluídas", stats["done"])
    with c4: st.metric("Atrasadas", stats["overdue"])

    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    # Create board
    if require_role("administrador", "gestor"):
        with st.expander("Criar Novo Quadro", expanded=False):
            with st.form("new_board_form"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    bname = st.text_input("Nome do Quadro")
                    bdesc = st.text_area("Descrição", height=72)
                with col2:
                    bcolor = st.selectbox("Cor de Destaque", BOARD_COLORS,
                        format_func=lambda c: c)
                if st.form_submit_button("Criar Quadro", use_container_width=True):
                    if bname:
                        create_board(bname.strip(), bdesc.strip(), bcolor, user["id"])
                        st.success(f"Quadro '{bname}' criado com sucesso.")
                        st.rerun()
                    else:
                        st.error("Nome é obrigatório.")

    st.markdown('<div class="section-title">Quadros Disponíveis</div>', unsafe_allow_html=True)

    if not boards:
        st.markdown("""
        <div class="empty-state">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" viewBox="0 0 24 24"><path d="M4 5h3v14H4zm6 0h3v8h-3zm6 0h3v11h-3z"/></svg>
            <div class="empty-state-title">Nenhum quadro disponível</div>
            <div class="empty-state-sub">Crie um novo quadro acima para começar</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Board grid — 3 per row
    for i in range(0, len(boards), 3):
        cols = st.columns(3, gap="medium")
        for j, board in enumerate(boards[i:i+3]):
            with cols[j]:
                bstats = get_dashboard_stats(board["id"])
                bcolor = board.get("color","#C0392B")
                desc = (board.get("description") or "Sem descrição")[:60]

                st.markdown(f"""
                <div class="board-card">
                    <div class="board-card-header" style="background:{bcolor}"></div>
                    <div class="board-card-body">
                        <div class="board-card-name">{board['name']}</div>
                        <div class="board-card-desc">{desc}</div>
                        <div class="board-card-stats">
                            <span>{ICONS['board']} {bstats['total']} tarefas</span>
                            <span style="color:#27AE60">{ICONS['check']} {bstats['done']}</span>
                            {'<span style="color:#C0392B">' + ICONS['warning'] + ' ' + str(bstats['overdue']) + ' atrasadas</span>' if bstats['overdue'] else ''}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                bc1, bc2 = st.columns([4, 1])
                with bc1:
                    if st.button("Abrir Quadro", key=f"open_{board['id']}", use_container_width=True):
                        st.session_state.current_board = board["id"]
                        st.session_state.page = "kanban"
                        st.rerun()
                with bc2:
                    if require_role("administrador"):
                        if st.button(ICONS["archive"], key=f"arch_{board['id']}", help="Arquivar quadro"):
                            archive_board(board["id"])
                            st.rerun()
