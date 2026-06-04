import streamlit as st
from modules.auth import get_current_user
from modules.board_ops import get_notifications, mark_notification_read, mark_all_notifications_read, count_unread_notifications
from modules.ui_components import page_header

TYPE_ICONS = {
    "info": "ℹ️",
    "warning": "⚠️",
    "success": "✅",
    "danger": "🚨",
    "comment": "💬",
    "task": "📋",
}

TYPE_COLORS = {
    "info": "#0052cc",
    "warning": "#ff991f",
    "success": "#00875a",
    "danger": "#de350b",
    "comment": "#6554c0",
    "task": "#00b8d9",
}

def show_notifications_page():
    user = get_current_user()
    page_header("🔔 Notificações", "Central de alertas e avisos do sistema")

    unread_count = count_unread_notifications(user["id"])

    if unread_count > 0:
        col1, col2 = st.columns([3,1])
        with col2:
            if st.button("✅ Marcar todas como lidas", use_container_width=True):
                mark_all_notifications_read(user["id"])
                st.rerun()
        with col1:
            st.markdown(f'<div style="font-size:14px;color:#ff991f;font-weight:600;padding:8px 0">🔔 {unread_count} notificação(ões) não lida(s)</div>',
                        unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:14px;color:#00875a;font-weight:600;padding:8px 0">✅ Todas as notificações foram lidas</div>',
                    unsafe_allow_html=True)

    notifs = get_notifications(user["id"])

    if not notifs:
        st.markdown("""
        <div style="text-align:center;padding:60px;color:#97a0af">
            <div style="font-size:48px;margin-bottom:12px">🔔</div>
            <div style="font-weight:600;font-size:16px">Nenhuma notificação</div>
            <div style="font-size:13px;margin-top:6px">Você está em dia!</div>
        </div>
        """, unsafe_allow_html=True)
        return

    for notif in notifs:
        ntype = notif.get("type","info")
        icon = TYPE_ICONS.get(ntype,"ℹ️")
        color = TYPE_COLORS.get(ntype,"#0052cc")
        is_unread = not notif.get("read", False)

        bg = "#e8f0ff" if is_unread else "#ffffff"
        border = color if is_unread else "#dde2f0"

        nc1, nc2 = st.columns([8, 1])
        with nc1:
            st.markdown(f"""
            <div class="k-notification {'unread' if is_unread else ''}"
                 style="background:{bg};border-left:3px solid {border}">
                <div style="display:flex;align-items:flex-start;gap:10px">
                    <span style="font-size:18px;margin-top:1px">{icon}</span>
                    <div style="flex:1">
                        <div style="font-weight:700;color:#172b4d;font-size:13px">
                            {notif['title']}
                            {f'<span style="background:{color};color:#fff;font-size:9px;padding:1px 6px;border-radius:100px;margin-left:6px;font-weight:600">NOVO</span>' if is_unread else ''}
                        </div>
                        <div style="font-size:12px;color:#5e6c84;margin-top:2px">{notif['message']}</div>
                        <div style="font-size:11px;color:#c1c7d0;margin-top:4px">{notif.get('created_at','')[:16]}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with nc2:
            if is_unread:
                if st.button("👁️", key=f"read_{notif['id']}", help="Marcar como lida"):
                    mark_notification_read(notif["id"])
                    st.rerun()
