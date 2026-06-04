import streamlit as st
from datetime import date
from modules.auth import get_current_user
from modules.board_ops import (
    get_personal_tasks, create_personal_task, toggle_personal_task, delete_personal_task,
    add_personal_checklist_item, toggle_personal_checklist_item,
    get_personal_notes, save_personal_note, delete_personal_note
)
from modules.ui_components import page_header, PRIORITY_COLORS, PRIORITY_ICONS

def show_personal_page():
    user = get_current_user()
    page_header("🔒 Área Pessoal", f"Sua área privada, {user['name'].split()[0]}. Apenas você pode ver isso.")

    tab1, tab2 = st.tabs(["✅ Minhas Tarefas", "📝 Notas & Anotações"])

    # ===== TASKS =====
    with tab1:
        with st.expander("➕ Nova Tarefa Pessoal", expanded=False):
            with st.form("new_personal_task"):
                pt_title = st.text_input("Título da tarefa*")
                pt_desc = st.text_area("Descrição", height=80)
                pc1, pc2 = st.columns(2)
                with pc1:
                    pt_due = st.date_input("Prazo", value=None)
                with pc2:
                    pt_prio = st.selectbox("Prioridade", ["média","alta","crítica","baixa"])
                if st.form_submit_button("✅ Criar Tarefa", use_container_width=True):
                    if pt_title:
                        create_personal_task(user["id"], pt_title, pt_desc,
                                             str(pt_due) if pt_due else None, pt_prio)
                        st.rerun()
                    else:
                        st.error("Título obrigatório")

        tasks = get_personal_tasks(user["id"])
        pending = [t for t in tasks if not t["completed"]]
        done = [t for t in tasks if t["completed"]]

        if not tasks:
            st.markdown("""
            <div style="text-align:center;padding:40px;color:#97a0af">
                <div style="font-size:48px;margin-bottom:12px">📋</div>
                <div style="font-weight:600">Nenhuma tarefa pessoal ainda</div>
                <div style="font-size:13px;margin-top:6px">Crie sua primeira tarefa acima</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            if pending:
                st.markdown(f"**⏳ Pendentes ({len(pending)})**")
                for task in pending:
                    _render_personal_task(task, user["id"])

            if done:
                with st.expander(f"✅ Concluídas ({len(done)})", expanded=False):
                    for task in done:
                        _render_personal_task(task, user["id"])

    # ===== NOTES =====
    with tab2:
        nc1, nc2 = st.columns([2, 3])

        with nc1:
            st.markdown("**📚 Minhas Notas**")
            notes = get_personal_notes(user["id"])

            with st.expander("➕ Nova Nota", expanded=False):
                with st.form("new_note_form"):
                    note_title = st.text_input("Título*", placeholder="Título da nota...")
                    note_content = st.text_area("Conteúdo", height=120, placeholder="Escreva aqui...")
                    if st.form_submit_button("💾 Salvar"):
                        if note_title:
                            save_personal_note(user["id"], note_title, note_content)
                            st.rerun()

            if not notes:
                st.info("Nenhuma nota criada.")
            else:
                for note in notes:
                    nc_btn, nc_del = st.columns([4,1])
                    with nc_btn:
                        if st.button(f"📝 {note['title'][:28]}...", key=f"sel_note_{note['id']}",
                                     use_container_width=True):
                            st.session_state.selected_note = note["id"]
                    with nc_del:
                        if st.button("🗑️", key=f"del_note_{note['id']}", help="Excluir"):
                            delete_personal_note(note["id"], user["id"])
                            if st.session_state.get("selected_note") == note["id"]:
                                st.session_state.selected_note = None
                            st.rerun()

        with nc2:
            selected_note_id = st.session_state.get("selected_note")
            if selected_note_id:
                notes_map = {n["id"]: n for n in get_personal_notes(user["id"])}
                note = notes_map.get(selected_note_id)
                if note:
                    st.markdown(f"**✏️ Editando: {note['title']}**")
                    with st.form(f"edit_note_{selected_note_id}"):
                        en_title = st.text_input("Título", value=note["title"])
                        en_content = st.text_area("Conteúdo", value=note.get("content",""), height=300)
                        if st.form_submit_button("💾 Salvar Nota", use_container_width=True):
                            save_personal_note(user["id"], en_title, en_content, selected_note_id)
                            st.success("Nota salva!")
                            st.rerun()
                    st.markdown(f'<div style="font-size:11px;color:#97a0af">Atualizado: {note.get("updated_at","")[:16]}</div>',
                                unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align:center;padding:60px;color:#97a0af">
                    <div style="font-size:48px;margin-bottom:12px">📝</div>
                    <div style="font-weight:600">Selecione uma nota para editar</div>
                </div>
                """, unsafe_allow_html=True)


def _render_personal_task(task, user_id):
    pcolor = PRIORITY_COLORS.get(task.get("priority","média"), "#97a0af")
    today_str = str(date.today())
    due = task.get("due_date")
    overdue = due and due < today_str and not task["completed"]
    checklist = task.get("checklist", [])
    done_chk = sum(1 for c in checklist if c["completed"])

    st.markdown(f"""
    <div class="personal-task" style="border-left:4px solid {pcolor};
         {'opacity:0.6;' if task['completed'] else ''}">
        <div style="flex:1">
            <div style="font-weight:600;color:#172b4d;font-size:13px;
                        {'text-decoration:line-through;color:#97a0af' if task['completed'] else ''}">
                {task['title']}
            </div>
            {f'<div style="font-size:12px;color:#5e6c84;margin-top:2px">{task["description"]}</div>' if task.get("description") else ""}
            <div style="display:flex;gap:10px;margin-top:6px;align-items:center">
                {f'<span style="color:#de350b;font-size:11px;font-weight:600">⚠️ {due}</span>' if overdue else (f'<span style="font-size:11px;color:#5e6c84">📅 {due}</span>' if due else '')}
                {f'<span style="font-size:11px;color:#5e6c84">✅ {done_chk}/{len(checklist)}</span>' if checklist else ''}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        done_label = "↩️ Reabrir" if task["completed"] else "✅ Concluir"
        if st.button(done_label, key=f"tog_task_{task['id']}", use_container_width=True):
            toggle_personal_task(task["id"]); st.rerun()
    with c2:
        if not task["completed"]:
            with st.popover("➕ Item"):
                new_item = st.text_input("Novo item", key=f"ni_pt_{task['id']}", label_visibility="collapsed",
                                          placeholder="Adicionar item ao checklist...")
                if st.button("Adicionar", key=f"add_pti_{task['id']}"):
                    if new_item:
                        add_personal_checklist_item(task["id"], new_item); st.rerun()
    with c3:
        if st.button("🗑️", key=f"del_task_{task['id']}", use_container_width=True):
            delete_personal_task(task["id"]); st.rerun()

    # Show checklist items
    if checklist:
        for item in checklist:
            ci1, ci2 = st.columns([8,1])
            with ci1:
                new_val = st.checkbox(item["text"], value=bool(item["completed"]),
                                      key=f"pchk_{item['id']}")
                if new_val != bool(item["completed"]):
                    toggle_personal_checklist_item(item["id"]); st.rerun()
