import streamlit as st
import os, sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from modules.database import init_database, seed_default_data
from modules.auth import get_current_user, logout
from modules.ui_components import inject_css
from modules.board_ops import count_unread_notifications

# ===== INIT =====
init_database()
seed_default_data()

st.set_page_config(
    page_title="KanbanPro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ===== AUTH CHECK =====
user = get_current_user()

if not user:
    from modules.page_login import show_login_page
    show_login_page()
    st.stop()

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        ⚡ KanbanPro
    </div>
    """, unsafe_allow_html=True)

    # User info
    initials = "".join(p[0].upper() for p in user["name"].split()[:2])
    from modules.ui_components import ROLE_LABELS
    role_label = ROLE_LABELS.get(user["role"], user["role"])
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;padding:8px;background:rgba(255,255,255,0.1);
                border-radius:10px;margin-bottom:16px">
        <div style="width:36px;height:36px;background:rgba(255,255,255,0.2);border-radius:50%;
                    display:flex;align-items:center;justify-content:center;font-weight:700;
                    font-size:13px;color:#fff;flex-shrink:0">{initials}</div>
        <div>
            <div style="font-weight:700;font-size:13px;color:#fff">{user['name'].split()[0]}</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.6)">{role_label}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    st.markdown('<div class="sidebar-section">Navegação</div>', unsafe_allow_html=True)

    current_page = st.session_state.get("page", "boards")

    nav_items = [
        ("boards", "🏠 Quadros", "boards"),
        ("kanban", "📋 Kanban", "kanban"),
        ("dashboard", "📊 Dashboard", "dashboard"),
        ("personal", "🔒 Área Pessoal", "personal"),
        ("notifications", "🔔 Notificações", "notifications"),
    ]

    if user["role"] == "administrador":
        nav_items.append(("admin", "⚙️ Administração", "admin"))

    for page_key, label, target in nav_items:
        # Show unread count on notifications
        display_label = label
        if page_key == "notifications":
            unread = count_unread_notifications(user["id"])
            if unread > 0:
                display_label = f"{label} ({unread})"

        is_active = current_page == page_key
        btn_style = "background:rgba(255,255,255,0.25)!important;border-color:rgba(255,255,255,0.4)!important;" if is_active else ""

        if st.button(display_label, key=f"nav_{page_key}",
                     use_container_width=True):
            st.session_state.page = target
            # Clear card modal when navigating
            st.session_state.show_card_modal = False
            st.session_state.selected_card = None
            st.rerun()

    st.markdown("---")
    st.markdown('<div class="sidebar-section">Sistema</div>', unsafe_allow_html=True)

    if st.button("🚪 Sair", use_container_width=True, key="logout_btn"):
        logout()
        st.rerun()

    # Quick stats at bottom
    from modules.board_ops import get_dashboard_stats
    stats = get_dashboard_stats()
    st.markdown(f"""
    <div style="position:absolute;bottom:20px;left:16px;right:16px">
        <div style="font-size:10px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;margin-bottom:6px">
            Status Geral
        </div>
        <div style="display:flex;gap:6px">
            <div style="flex:1;background:rgba(255,255,255,0.1);border-radius:8px;padding:6px;text-align:center">
                <div style="font-size:14px;font-weight:800;color:#fff">{stats['open']}</div>
                <div style="font-size:9px;color:rgba(255,255,255,0.5)">ABERTAS</div>
            </div>
            <div style="flex:1;background:rgba(255,255,255,0.1);border-radius:8px;padding:6px;text-align:center">
                <div style="font-size:14px;font-weight:800;color:{'#ff6b6b' if stats['overdue'] > 0 else '#fff'}">{stats['overdue']}</div>
                <div style="font-size:9px;color:rgba(255,255,255,0.5)">ATRASADAS</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ===== PAGE ROUTING =====
page = st.session_state.get("page", "boards")

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
