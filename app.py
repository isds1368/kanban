import streamlit as st
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from modules.database import init_database, seed_default_data
from modules.auth import get_current_user, logout
from modules.ui_components import inject_css, icon, avatar, ICONS, ROLE_LABELS

init_database()
seed_default_data()

st.set_page_config(
    page_title="KanbanPro",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path fill='%23C0392B' d='M4 5h3v14H4zm6 0h3v8h-3zm6 0h3v11h-3z'/></svg>",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

user = get_current_user()

if not user:
    from modules.page_login import show_login_page
    show_login_page()
    st.stop()

# ── init session defaults ──────────────────────────────────────────────────
for k, v in [("page","boards"),("current_board",None),("selected_card",None),
             ("show_card_modal",False),("selected_note",None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown(f"""
    <div class="sb-logo">
        <div style="width:32px;height:32px;background:var(--primary);border-radius:8px;
                    display:flex;align-items:center;justify-content:center">
            {ICONS['logo']}
        </div>
        <span class="sb-logo-text">KanbanPro</span>
    </div>
    """, unsafe_allow_html=True)

    # User chip
    initials = "".join(p[0].upper() for p in user["name"].split()[:2])
    role_label = ROLE_LABELS.get(user["role"], user["role"])
    st.markdown(f"""
    <div class="sb-user">
        <div class="sb-avatar">{initials}</div>
        <div>
            <div class="sb-name">{user['name'].split()[0]}</div>
            <div class="sb-role">{role_label}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Nav
    st.markdown('<div class="sb-section">Navegação</div>', unsafe_allow_html=True)

    from modules.board_ops import count_unread_notifications
    unread = count_unread_notifications(user["id"])

    current_page = st.session_state.page

    nav = [
        ("boards",        "home",     "Quadros",        None),
        ("kanban",        "board",    "Kanban",         None),
        ("dashboard",     "chart",    "Dashboard",      None),
        ("personal",      "lock",     "Área Pessoal",   None),
        ("notifications", "bell",     "Notificações",   unread if unread > 0 else None),
    ]
    if user["role"] == "administrador":
        nav.append(("admin", "settings", "Administração", None))

    for page_key, ico_key, label, badge in nav:
        is_active = current_page == page_key
        badge_html = f'<span class="sb-badge">{badge}</span>' if badge else ""
        active_class = "active" if is_active else ""

        # We render the visual as HTML but use a real button to capture clicks
        st.markdown(f"""
        <div class="sb-nav-item {active_class}" id="nav_{page_key}"
             style="{'pointer-events:none;' if is_active else ''}">
            <span style="opacity:0.8;display:flex;align-items:center">{ICONS[ico_key]}</span>
            <span style="flex:1">{label}</span>
            {badge_html}
        </div>
        """, unsafe_allow_html=True)

        if not is_active:
            if st.button(label, key=f"navbtn_{page_key}", use_container_width=True):
                st.session_state.page = page_key
                st.session_state.show_card_modal = False
                st.session_state.selected_card = None
                st.rerun()

    st.markdown("""
    <style>
    /* hide duplicate button text, show only the HTML nav item */
    [data-testid="stSidebar"] .stButton > button {
        opacity: 0 !important;
        height: 1px !important;
        min-height: 0 !important;
        padding: 0 !important;
        margin: -1px 0 0 !important;
        border: none !important;
        box-shadow: none !important;
        pointer-events: all !important;
        position: relative;
        z-index: 10;
    }
    </style>
    """, unsafe_allow_html=True)

    # Logout & footer stats
    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-section">Sistema</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sb-nav-item" id="nav_logout">
        <span style="opacity:0.8;display:flex;align-items:center">{ICONS['logout']}</span>
        <span>Sair</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Sair", key="navbtn_logout", use_container_width=True):
        logout()
        st.rerun()

    # Footer stats
    from modules.board_ops import get_dashboard_stats
    stats = get_dashboard_stats()
    danger_color = "#E74C3C" if stats["overdue"] > 0 else "#fff"
    st.markdown(f"""
    <div class="sb-footer">
        <div class="sb-section" style="padding:0 0 4px">Status Geral</div>
        <div class="sb-stat-row">
            <div class="sb-stat">
                <div class="sb-stat-n">{stats['open']}</div>
                <div class="sb-stat-l">Abertas</div>
            </div>
            <div class="sb-stat">
                <div class="sb-stat-n" style="color:{danger_color}">{stats['overdue']}</div>
                <div class="sb-stat-l">Atrasadas</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── PAGE ROUTER ────────────────────────────────────────────────────────────
page = st.session_state.page

if page == "boards":
    from modules.page_boards import show_boards_page
    show_boards_page()
elif page == "kanban":
    if not st.session_state.get("current_board"):
        from modules.page_boards import show_boards_page
        show_boards_page()
    else:
        from modules.page_kanban import show_kanban_page
        show_kanban_page()
elif page == "dashboard":
    from modules.page_dashboard import show_dashboard_page
    show_dashboard_page()
elif page == "personal":
    from modules.page_personal import show_personal_page
    show_personal_page()
elif page == "notifications":
    from modules.page_notifications import show_notifications_page
    show_notifications_page()
elif page == "admin":
    from modules.page_admin import show_admin_page
    show_admin_page()
else:
    st.session_state.page = "boards"
    st.rerun()
