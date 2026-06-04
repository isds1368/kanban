import streamlit as st

PRIORITY_COLORS = {
    "crítica": "#ff2d55",
    "alta": "#ff6b35",
    "média": "#ffcc00",
    "baixa": "#34c759",
}

PRIORITY_ICONS = {
    "crítica": "🔴",
    "alta": "🟠",
    "média": "🟡",
    "baixa": "🟢",
}

ROLE_LABELS = {
    "administrador": "Administrador",
    "gestor": "Gestor",
    "colaborador": "Colaborador",
    "leitor": "Leitor",
}

def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --primary: #0052cc;
    --primary-light: #4c9aff;
    --primary-dark: #003884;
    --surface: #ffffff;
    --surface-2: #f7f8fc;
    --surface-3: #edf0f7;
    --border: #dde2f0;
    --text-primary: #172b4d;
    --text-secondary: #5e6c84;
    --text-muted: #97a0af;
    --success: #00875a;
    --warning: #ff991f;
    --danger: #de350b;
    --info: #0065ff;
    --shadow-sm: 0 1px 3px rgba(9,30,66,0.12), 0 0 0 1px rgba(9,30,66,0.08);
    --shadow-md: 0 4px 12px rgba(9,30,66,0.15), 0 0 0 1px rgba(9,30,66,0.06);
    --shadow-lg: 0 8px 24px rgba(9,30,66,0.2);
    --radius: 8px;
    --radius-lg: 12px;
    --radius-xl: 16px;
}

* { font-family: 'Plus Jakarta Sans', sans-serif !important; }
code, pre { font-family: 'JetBrains Mono', monospace !important; }

html, body, [class*="css"] {
    background: #f0f2f7 !important;
    color: var(--text-primary) !important;
}

.stApp { background: #f0f2f7 !important; }

/* Hide default streamlit elements */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
.stDeployButton { display: none; }
div[data-testid="stToolbar"] { visibility: hidden; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #c1c7d0; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #97a0af; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--primary-dark) !important;
    border-right: none !important;
}
[data-testid="stSidebar"] * { color: #fff !important; }
[data-testid="stSidebar"] .stButton button {
    background: rgba(255,255,255,0.1) !important;
    color: #fff !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: var(--radius) !important;
    font-weight: 500 !important;
    text-align: left !important;
    width: 100% !important;
    transition: all 0.15s ease !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(255,255,255,0.2) !important;
    border-color: rgba(255,255,255,0.3) !important;
}

/* Main buttons */
.stButton button {
    background: var(--primary) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 8px 16px !important;
    transition: all 0.15s ease !important;
    box-shadow: var(--shadow-sm) !important;
}
.stButton button:hover {
    background: var(--primary-dark) !important;
    box-shadow: var(--shadow-md) !important;
    transform: translateY(-1px) !important;
}

/* Inputs */
.stTextInput input, .stTextArea textarea, .stSelectbox select,
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text-primary) !important;
    font-size: 14px !important;
    transition: border-color 0.15s !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(0,82,204,0.15) !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border-radius: var(--radius-lg) !important;
    padding: 16px 20px !important;
    box-shadow: var(--shadow-sm) !important;
    border: 1px solid var(--border) !important;
}
[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: var(--primary) !important;
}
[data-testid="stMetricLabel"] {
    font-size: 12px !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

/* Tabs */
[data-baseweb="tab-list"] {
    background: var(--surface-2) !important;
    border-radius: var(--radius) !important;
    padding: 4px !important;
    gap: 2px !important;
}
[data-baseweb="tab"] {
    border-radius: 6px !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    color: var(--text-secondary) !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    background: var(--surface) !important;
    color: var(--primary) !important;
    font-weight: 600 !important;
    box-shadow: var(--shadow-sm) !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    box-shadow: var(--shadow-sm) !important;
    overflow: hidden !important;
}

/* Divider */
hr { border-color: var(--border) !important; margin: 12px 0 !important; }

/* Cards */
.k-card {
    background: #ffffff;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border);
    padding: 14px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
}
.k-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
    border-color: var(--primary-light);
}
.k-card-title {
    font-size: 13.5px;
    font-weight: 600;
    color: var(--text-primary);
    line-height: 1.4;
    margin-bottom: 6px;
}
.k-card-meta {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
    margin-top: 8px;
}
.k-tag {
    display: inline-flex;
    align-items: center;
    padding: 2px 8px;
    border-radius: 100px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.2px;
}
.k-column {
    background: var(--surface-3);
    border-radius: var(--radius-xl);
    padding: 12px;
    min-width: 280px;
    max-width: 300px;
    border: 1px solid var(--border);
}
.k-column-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
}
.k-column-title {
    font-size: 13px;
    font-weight: 700;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.6px;
}
.k-count-badge {
    background: var(--border);
    color: var(--text-secondary);
    border-radius: 100px;
    padding: 1px 7px;
    font-size: 11px;
    font-weight: 700;
}
.k-priority-bar {
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 4px;
    border-radius: 12px 0 0 12px;
}
.k-board-card {
    background: var(--surface);
    border-radius: var(--radius-xl);
    padding: 20px;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border);
    cursor: pointer;
    transition: all 0.2s ease;
    text-align: center;
}
.k-board-card:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-3px);
}
.k-notification {
    background: var(--surface);
    border-radius: var(--radius);
    padding: 12px 14px;
    margin-bottom: 8px;
    border: 1px solid var(--border);
    border-left: 3px solid var(--primary);
}
.k-notification.unread {
    background: #e8f0ff;
    border-left-color: var(--primary);
}
.k-history-item {
    display: flex;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
    font-size: 13px;
}
.k-avatar {
    width: 28px; height: 28px;
    border-radius: 50%;
    background: var(--primary);
    color: #fff;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    flex-shrink: 0;
}
.k-progress-bar {
    background: var(--border);
    border-radius: 100px;
    height: 6px;
    overflow: hidden;
}
.k-progress-fill {
    height: 100%;
    border-radius: 100px;
    background: linear-gradient(90deg, var(--primary), var(--primary-light));
    transition: width 0.4s ease;
}
.sidebar-logo {
    font-size: 22px;
    font-weight: 800;
    color: #fff;
    letter-spacing: -0.5px;
    padding: 8px 0 16px;
    border-bottom: 1px solid rgba(255,255,255,0.15);
    margin-bottom: 16px;
}
.sidebar-section {
    font-size: 10px;
    font-weight: 700;
    color: rgba(255,255,255,0.5) !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 16px 0 6px;
    padding: 0 4px;
}
.page-title {
    font-size: 26px;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.5px;
    margin-bottom: 4px;
}
.page-subtitle {
    font-size: 14px;
    color: var(--text-secondary);
    margin-bottom: 24px;
}
.stat-card {
    background: var(--surface);
    border-radius: var(--radius-lg);
    padding: 20px;
    border: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
    text-align: center;
}
.stat-number {
    font-size: 2.5rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 4px;
}
.stat-label {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-secondary);
}
.overdue-badge {
    background: #fff0f0;
    color: var(--danger);
    border: 1px solid #ffcdd2;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
}
.due-badge {
    background: #fff8e1;
    color: #f57c00;
    border: 1px solid #ffe082;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
}
.personal-task {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    background: var(--surface);
    border-radius: var(--radius);
    padding: 12px 14px;
    border: 1px solid var(--border);
    margin-bottom: 8px;
    transition: all 0.15s;
}
.personal-task:hover { box-shadow: var(--shadow-sm); }
.note-card {
    background: var(--surface);
    border-radius: var(--radius-lg);
    padding: 16px;
    border: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
    margin-bottom: 12px;
    cursor: pointer;
    transition: all 0.15s;
}
.note-card:hover { box-shadow: var(--shadow-md); }
.user-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--surface-3);
    border: 1px solid var(--border);
    border-radius: 100px;
    padding: 4px 10px 4px 6px;
    font-size: 12px;
    font-weight: 500;
    color: var(--text-secondary);
}
</style>
""", unsafe_allow_html=True)

def page_header(title, subtitle=""):
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)

def priority_badge(priority):
    color = PRIORITY_COLORS.get(priority, "#97a0af")
    icon = PRIORITY_ICONS.get(priority, "⚪")
    return f'<span class="k-tag" style="background:{color}20;color:{color}">{icon} {priority.capitalize()}</span>'

def label_badge(name, color):
    return f'<span class="k-tag" style="background:{color}25;color:{color};border:1px solid {color}40">{name}</span>'

def avatar_html(name, size=28):
    initials = "".join(p[0].upper() for p in name.split()[:2]) if name else "?"
    return f'<span class="k-avatar" style="width:{size}px;height:{size}px;font-size:{int(size*0.4)}px">{initials}</span>'
