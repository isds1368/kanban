import streamlit as st
from datetime import datetime, date
from modules.auth import get_current_user, require_role
from modules.board_ops import (
    get_board, get_columns, get_cards_by_column, create_column, update_column, delete_column,
    create_card, move_card, archive_card, get_card, update_card,
    get_comments, add_comment, get_checklists, add_checklist, add_checklist_item,
    toggle_checklist_item, delete_checklist_item, get_card_history, get_card_labels,
    set_card_labels, get_labels, add_label, get_all_cards_filtered
)
from modules.auth import get_all_users
from modules.ui_components import (
    page_header, priority_badge, label_badge, avatar_html,
    PRIORITY_COLORS, PRIORITY_ICONS
)
import os, uuid

UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")

def show_kanban_page():
    user = get_current_user()
    board_id = st.session_state.get("current_board")
    if not board_id:
        st.warning("Nenhum quadro selecionado.")
        if st.button("← Voltar aos Quadros"):
            st.session_state.page = "boards"
            st.rerun()
        return

    board = get_board(board_id)
    if not board:
        st.error("Quadro não encontrado.")
        return

    # Header
    col_title, col_back, col_filter = st.columns([4, 1, 1])
    with col_title:
        st.markdown(f'<div class="page-title">📋 {board["name"]}</div>', unsafe_allow_html=True)
        if board.get("description"):
            st.markdown(f'<div class="page-subtitle">{board["description"]}</div>', unsafe_allow_html=True)
    with col_back:
        if st.button("← Quadros", use_container_width=True):
            st.session_state.page = "boards"
            st.rerun()
    with col_filter:
        show_filter = st.toggle("🔍 Filtros", key="show_filter_toggle")

    # Filters
    if show_filter:
        with st.expander("🔍 Filtros e Busca", expanded=True):
            fc1, fc2, fc3, fc4, fc5 = st.columns(5)
            all_users = get_all_users()
            user_opts = {u["id"]: u["name"] for u in all_users}
            with fc1:
                f_search = st.text_input("🔎 Buscar", key="f_search", placeholder="Título...")
            with fc2:
                f_resp = st.selectbox("Responsável", [None]+list(user_opts.keys()),
                    format_func=lambda x: "Todos" if x is None else user_opts.get(x,""), key="f_resp")
            with fc3:
                f_priority = st.selectbox("Prioridade", [None,"crítica","alta","média","baixa"],
                    format_func=lambda x: "Todas" if x is None else x.capitalize(), key="f_prio")
            with fc4:
                f_sector = st.text_input("Setor", key="f_sector", placeholder="Setor...")
            with fc5:
                f_overdue = st.checkbox("⚠️ Só atrasadas", key="f_overdue")

            filtered_cards = get_all_cards_filtered(
                board_id=board_id,
                responsible_id=f_resp if f_resp else None,
                sector=f_sector if f_sector else None,
                priority=f_priority if f_priority else None,
                search=f_search if f_search else None,
                overdue_only=f_overdue
            )
            st.markdown(f"**{len(filtered_cards)} tarefas encontradas**")
            for fc in filtered_cards:
                pcolor = PRIORITY_COLORS.get(fc.get("priority","média"), "#97a0af")
                overdue = fc.get("due_date") and fc["due_date"] < str(date.today()) and fc["status"] != "concluído"
                st.markdown(f"""
                <div class="k-card" style="border-left:4px solid {pcolor}">
                    <div class="k-card-title">{fc['title']}</div>
                    <div class="k-card-meta">
                        <span style="font-size:11px;color:#5e6c84">📍 {fc.get('column_name','')}</span>
                        {f'<span style="font-size:11px;color:#5e6c84">👤 {fc.get("responsible_name","")}</span>' if fc.get("responsible_name") else ""}
                        {'<span class="overdue-badge">⚠️ ATRASADA</span>' if overdue else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Abrir card #{fc['id']}", key=f"fcard_{fc['id']}"):
                    st.session_state.selected_card = fc["id"]
                    st.session_state.show_card_modal = True
                    st.rerun()
            st.markdown("---")

    # Show card detail if selected
    if st.session_state.get("show_card_modal") and st.session_state.get("selected_card"):
        _show_card_detail(st.session_state.selected_card, board_id, user)

    # Column management
    if require_role("administrador", "gestor"):
        with st.expander("⚙️ Gerenciar Colunas", expanded=False):
            cols_data = get_columns(board_id)
            st.markdown("**Colunas existentes:**")
            for col in cols_data:
                cc1, cc2, cc3, cc4 = st.columns([3,2,1,1])
                with cc1:
                    new_name = st.text_input("", value=col["name"], key=f"colname_{col['id']}", label_visibility="collapsed")
                with cc2:
                    new_color = st.color_picker("", value=col.get("color","#e2e8f0"), key=f"colcolor_{col['id']}", label_visibility="collapsed")
                with cc3:
                    if st.button("💾", key=f"savecol_{col['id']}", help="Salvar"):
                        update_column(col["id"], new_name, new_color)
                        st.rerun()
                with cc4:
                    if st.button("🗑️", key=f"delcol_{col['id']}", help="Excluir"):
                        delete_column(col["id"])
                        st.rerun()

            st.markdown("**Adicionar coluna:**")
            nc1, nc2, nc3 = st.columns([3,1,1])
            with nc1:
                new_col_name = st.text_input("Nome da nova coluna", key="new_col_name", label_visibility="collapsed", placeholder="Nome da coluna...")
            with nc3:
                if st.button("➕ Adicionar", key="add_col"):
                    if new_col_name:
                        create_column(board_id, new_col_name)
                        st.rerun()

    st.markdown("---")

    # ===== KANBAN BOARD =====
    columns = get_columns(board_id)
    all_users = get_all_users()
    user_map = {u["id"]: u["name"] for u in all_users}

    if not columns:
        st.info("Nenhuma coluna criada ainda. Use 'Gerenciar Colunas' acima.")
        return

    # Render columns horizontally
    board_cols = st.columns(len(columns))

    for idx, col in enumerate(columns):
        cards = get_cards_by_column(col["id"])

        with board_cols[idx]:
            # Column header
            col_color = col.get("color","#e2e8f0")
            st.markdown(f"""
            <div class="k-column">
                <div class="k-column-header">
                    <span class="k-column-title" style="color:{col_color if col_color != '#e2e8f0' else '#5e6c84'}">
                        {col['name']}
                    </span>
                    <span class="k-count-badge">{len(cards)}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Cards
            for card in cards:
                _render_card_mini(card, col, columns, user, user_map, board_id)

            # Add card button
            if require_role("administrador", "gestor", "colaborador"):
                with st.expander(f"➕ Adicionar em {col['name']}", expanded=False):
                    with st.form(f"new_card_{col['id']}"):
                        ct = st.text_input("Título*", key=f"ct_{col['id']}")
                        cd = st.text_area("Descrição", key=f"cd_{col['id']}", height=80)
                        resp_opts = [None] + [u["id"] for u in all_users]
                        cr = st.selectbox("Responsável", resp_opts,
                            format_func=lambda x: "Nenhum" if x is None else user_map.get(x,""),
                            key=f"cr_{col['id']}")
                        cp = st.selectbox("Prioridade", ["média","alta","crítica","baixa"], key=f"cp_{col['id']}")
                        cdate = st.date_input("Prazo", value=None, key=f"cdate_{col['id']}")
                        if st.form_submit_button("Criar Card", use_container_width=True):
                            if ct:
                                create_card(col["id"], board_id, ct, cd, cr, user["id"],
                                            None, cp, str(cdate) if cdate else None, user["id"])
                                st.rerun()
                            else:
                                st.error("Título obrigatório")


def _render_card_mini(card, current_col, all_columns, user, user_map, board_id):
    pcolor = PRIORITY_COLORS.get(card.get("priority","média"), "#97a0af")
    card_id = card["id"]
    today_str = str(date.today())
    due = card.get("due_date")
    overdue = due and due < today_str and card.get("status") != "concluído"
    due_soon = due and today_str <= due <= today_str and not overdue

    labels = get_card_labels(card_id)
    label_html = " ".join(label_badge(l["name"], l["color"]) for l in labels)

    responsible = card.get("responsible_name","")
    pct = card.get("completion_percent", 0)

    st.markdown(f"""
    <div class="k-card" style="padding-left:18px">
        <div class="k-priority-bar" style="background:{pcolor}"></div>
        <div class="k-card-title">{card['title']}</div>
        {f'<div style="font-size:11px;color:#5e6c84;margin-bottom:4px">{card["description"][:60]}...</div>' if card.get("description") and len(card.get("description","")) > 30 else ""}
        {f'<div style="margin:4px 0">{label_html}</div>' if labels else ""}
        <div class="k-card-meta">
            {f'<span style="font-size:11px;color:#5e6c84">👤 {responsible}</span>' if responsible else ""}
            {f'<span class="overdue-badge">⚠️ {due}</span>' if overdue else ""}
            {f'<span class="due-badge">📅 {due}</span>' if due and not overdue else ""}
        </div>
        {f'<div class="k-progress-bar" style="margin-top:8px"><div class="k-progress-fill" style="width:{pct}%"></div></div>' if pct > 0 else ""}
    </div>
    """, unsafe_allow_html=True)

    # Action row
    ac1, ac2, ac3 = st.columns([2,2,1])
    with ac1:
        if st.button("✏️ Abrir", key=f"open_card_{card_id}", use_container_width=True):
            st.session_state.selected_card = card_id
            st.session_state.show_card_modal = True
            st.rerun()
    with ac2:
        move_opts = [c for c in all_columns if c["id"] != current_col["id"]]
        if move_opts:
            dest = st.selectbox("Mover →", [None]+[c["id"] for c in move_opts],
                format_func=lambda x: "Mover..." if x is None else next((c["name"] for c in all_columns if c["id"]==x),""),
                key=f"move_{card_id}", label_visibility="collapsed")
            if dest:
                move_card(card_id, dest, user["id"])
                st.rerun()
    with ac3:
        if require_role("administrador","gestor") and st.button("🗄️", key=f"arch_card_{card_id}", help="Arquivar"):
            archive_card(card_id, user["id"])
            st.rerun()


def _show_card_detail(card_id, board_id, user):
    card = get_card(card_id)
    if not card:
        st.session_state.show_card_modal = False
        return

    all_users = get_all_users()
    user_map = {u["id"]: u["name"] for u in all_users}
    labels = get_labels(board_id)
    card_labels = get_card_labels(card_id)
    card_label_ids = [l["id"] for l in card_labels]

    with st.expander(f"📝 {card['title']} — Detalhes", expanded=True):
        if st.button("✖️ Fechar Card", key="close_card_modal"):
            st.session_state.show_card_modal = False
            st.session_state.selected_card = None
            st.rerun()

        tabs = st.tabs(["📋 Detalhes", "✅ Checklist", "💬 Comentários", "📎 Etiquetas", "📜 Histórico"])

        # === TAB 1: DETAILS ===
        with tabs[0]:
            can_edit = require_role("administrador","gestor","colaborador")
            with st.form(f"edit_card_{card_id}"):
                r1c1, r1c2 = st.columns([3,1])
                with r1c1:
                    new_title = st.text_input("Título", value=card["title"])
                with r1c2:
                    prio_opts = ["crítica","alta","média","baixa"]
                    new_prio = st.selectbox("Prioridade", prio_opts,
                        index=prio_opts.index(card.get("priority","média")))

                new_desc = st.text_area("Descrição", value=card.get("description",""), height=100)

                r2c1, r2c2, r2c3 = st.columns(3)
                with r2c1:
                    resp_opts = [None]+[u["id"] for u in all_users]
                    cur_resp_idx = resp_opts.index(card.get("responsible_id")) if card.get("responsible_id") in resp_opts else 0
                    new_resp = st.selectbox("Responsável", resp_opts, index=cur_resp_idx,
                        format_func=lambda x: "Nenhum" if x is None else user_map.get(x,""))
                with r2c2:
                    new_sector = st.text_input("Setor", value=card.get("sector",""))
                with r2c3:
                    status_opts = ["aberto","em andamento","aguardando","concluído","cancelado"]
                    cur_status = card.get("status","aberto")
                    st.write("Status")
                    new_status = st.selectbox("Status", status_opts,
                        index=status_opts.index(cur_status) if cur_status in status_opts else 0,
                        label_visibility="collapsed")

                r3c1, r3c2 = st.columns(2)
                with r3c1:
                    due_val = None
                    if card.get("due_date"):
                        try: due_val = datetime.strptime(card["due_date"], "%Y-%m-%d").date()
                        except: pass
                    new_due = st.date_input("Prazo", value=due_val)
                with r3c2:
                    new_pct = st.slider("% Conclusão", 0, 100, int(card.get("completion_percent",0)))

                if can_edit and st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                    update_card(card_id, title=new_title, description=new_desc,
                                responsible_id=new_resp, sector=new_sector,
                                priority=new_prio, status=new_status,
                                due_date=str(new_due) if new_due else None,
                                completion_percent=new_pct)
                    st.success("Salvo!")
                    st.rerun()

        # === TAB 2: CHECKLIST ===
        with tabs[1]:
            checklists = get_checklists(card_id)
            for cl in checklists:
                st.markdown(f"**{cl['title']}**")
                total = len(cl["items"])
                done = sum(1 for i in cl["items"] if i["completed"])
                if total > 0:
                    st.progress(done/total, text=f"{done}/{total} concluídos")

                for item in cl["items"]:
                    ic1, ic2 = st.columns([8,1])
                    with ic1:
                        if st.checkbox(item["text"], value=bool(item["completed"]),
                                       key=f"chk_{item['id']}"):
                            if not item["completed"]:
                                toggle_checklist_item(item["id"]); st.rerun()
                        else:
                            if item["completed"]:
                                toggle_checklist_item(item["id"]); st.rerun()
                    with ic2:
                        if st.button("🗑️", key=f"del_chk_{item['id']}", help="Remover"):
                            delete_checklist_item(item["id"]); st.rerun()

                # Add item
                with st.form(f"add_item_{cl['id']}"):
                    new_item = st.text_input("Novo item", key=f"ni_{cl['id']}", label_visibility="collapsed", placeholder="Adicionar item...")
                    if st.form_submit_button("➕"):
                        if new_item:
                            add_checklist_item(cl["id"], new_item); st.rerun()
                st.markdown("---")

            # Add checklist
            if require_role("administrador","gestor","colaborador"):
                with st.form("add_checklist"):
                    cl_title = st.text_input("Nome do checklist", placeholder="Ex: Etapas da tarefa")
                    if st.form_submit_button("➕ Novo Checklist"):
                        if cl_title:
                            add_checklist(card_id, cl_title); st.rerun()

        # === TAB 3: COMMENTS ===
        with tabs[2]:
            comments = get_comments(card_id)
            for cm in comments:
                uname = cm.get("user_name","?")
                initials = "".join(p[0].upper() for p in uname.split()[:2])
                st.markdown(f"""
                <div style="display:flex;gap:10px;margin-bottom:14px">
                    <div class="k-avatar">{initials}</div>
                    <div style="flex:1">
                        <div style="font-size:12px;font-weight:700;color:#172b4d">{uname}
                            <span style="font-weight:400;color:#97a0af;margin-left:8px">{cm['created_at'][:16]}</span>
                        </div>
                        <div style="font-size:13px;color:#344563;margin-top:2px;background:#f7f8fc;padding:8px 12px;border-radius:8px">{cm['message']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with st.form("add_comment_form"):
                new_msg = st.text_area("Novo comentário", height=80, label_visibility="collapsed",
                                       placeholder="Escreva um comentário...")
                if st.form_submit_button("💬 Comentar", use_container_width=True):
                    if new_msg.strip():
                        add_comment(card_id, user["id"], new_msg.strip()); st.rerun()

        # === TAB 4: LABELS ===
        with tabs[3]:
            st.markdown("**Etiquetas do card:**")
            if labels:
                selected_ids = []
                for lbl in labels:
                    checked = lbl["id"] in card_label_ids
                    col_a, col_b = st.columns([1, 6])
                    with col_a:
                        new_check = st.checkbox("", value=checked, key=f"lbl_{lbl['id']}_{card_id}")
                    with col_b:
                        st.markdown(f'<div style="margin-top:4px">{label_badge(lbl["name"], lbl["color"])}</div>',
                                    unsafe_allow_html=True)
                    if new_check:
                        selected_ids.append(lbl["id"])

                if st.button("💾 Salvar Etiquetas", key="save_labels"):
                    set_card_labels(card_id, selected_ids); st.success("Etiquetas salvas!"); st.rerun()
            else:
                st.info("Nenhuma etiqueta criada para este quadro.")

            st.markdown("---")
            st.markdown("**Criar nova etiqueta:**")
            with st.form("new_label_form"):
                lc1, lc2 = st.columns([3,1])
                with lc1: lbl_name = st.text_input("Nome", placeholder="Ex: Urgente")
                with lc2: lbl_color = st.color_picker("Cor", "#0052cc")
                if st.form_submit_button("➕ Criar"):
                    if lbl_name:
                        add_label(board_id, lbl_name, lbl_color); st.rerun()

        # === TAB 5: HISTORY ===
        with tabs[4]:
            history = get_card_history(card_id)
            if not history:
                st.info("Nenhum histórico registrado.")
            else:
                for h in history:
                    action_icons = {"criação":"🆕","movimentação":"🔄","comentário":"💬",
                                    "arquivamento":"🗄️","alteração":"✏️"}
                    icon = action_icons.get(h.get("action",""),"📌")
                    uname = h.get("user_name","Sistema")
                    st.markdown(f"""
                    <div class="k-history-item">
                        <span style="font-size:16px">{icon}</span>
                        <div>
                            <span style="font-weight:600;color:#172b4d">{uname}</span>
                            <span style="color:#5e6c84"> — {h.get('action','')}</span>
                            {f'<div style="font-size:12px;color:#97a0af">{h.get("detail","")}</div>' if h.get("detail") else ""}
                            <div style="font-size:11px;color:#c1c7d0">{h.get("created_at","")[:16]}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
