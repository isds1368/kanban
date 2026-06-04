import streamlit as st
import json
from datetime import date, timedelta
from modules.auth import get_current_user
from modules.board_ops import get_dashboard_stats, get_boards_for_user, get_all_cards_filtered
from modules.ui_components import page_header, PRIORITY_COLORS

def show_dashboard_page():
    user = get_current_user()
    page_header("📊 Dashboard Executivo", "Indicadores de produtividade e desempenho operacional")

    boards = get_boards_for_user(user["id"], user["role"])

    # Board selector
    board_opts = {None: "Todos os Quadros"}
    board_opts.update({b["id"]: b["name"] for b in boards})
    selected_board = st.selectbox("Filtrar por Quadro", list(board_opts.keys()),
        format_func=lambda x: board_opts[x])

    stats = get_dashboard_stats(selected_board)

    # ===== KPI CARDS =====
    st.markdown("### 📈 Indicadores Gerais")
    c1, c2, c3, c4, c5 = st.columns(5)

    total_rate = round(stats["done"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0

    with c1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number" style="color:#0052cc">{stats['total']}</div>
            <div class="stat-label">Total de Tarefas</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number" style="color:#ff991f">{stats['open']}</div>
            <div class="stat-label">Em Aberto</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number" style="color:#00875a">{stats['done']}</div>
            <div class="stat-label">Concluídas</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number" style="color:#de350b">{stats['overdue']}</div>
            <div class="stat-label">Atrasadas</div>
        </div>
        """, unsafe_allow_html=True)
    with c5:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number" style="color:#6554c0">{total_rate}%</div>
            <div class="stat-label">Taxa de Conclusão</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ===== CHARTS =====
    st.markdown("### 📊 Análise Visual")
    ch1, ch2 = st.columns(2)

    with ch1:
        _render_priority_chart(stats["by_priority"])

    with ch2:
        _render_sector_chart(stats["by_sector"])

    # Weekly evolution
    st.markdown("### 📅 Evolução Temporal")
    wc1, wc2 = st.columns(2)
    with wc1:
        _render_weekly_chart(stats["weekly"])
    with wc2:
        _render_monthly_chart(stats["monthly"])

    # Responsible table
    st.markdown("### 👥 Produtividade por Colaborador")
    _render_responsible_table(stats["by_responsible"])

    # Overdue cards list
    if stats["overdue"] > 0:
        st.markdown("### ⚠️ Tarefas Atrasadas")
        overdue_cards = get_all_cards_filtered(board_id=selected_board, overdue_only=True)
        for card in overdue_cards[:20]:
            days_late = (date.today() - date.fromisoformat(card["due_date"])).days if card.get("due_date") else 0
            st.markdown(f"""
            <div style="background:#fff5f5;border:1px solid #ffcdd2;border-radius:8px;
                        padding:12px 16px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center">
                <div>
                    <span style="font-weight:600;color:#172b4d">{card['title']}</span>
                    <span style="font-size:12px;color:#5e6c84;margin-left:8px">— {card.get('responsible_name','Sem responsável')}</span>
                </div>
                <span style="color:#de350b;font-size:12px;font-weight:600">
                    ⚠️ {days_late} dia{'s' if days_late != 1 else ''} atrasada
                </span>
            </div>
            """, unsafe_allow_html=True)


def _render_priority_chart(by_priority):
    st.markdown("**Tarefas por Prioridade**")
    if not by_priority:
        st.info("Sem dados")
        return

    total = sum(r["cnt"] for r in by_priority)
    for row in by_priority:
        prio = row.get("priority", "?") or "?"
        cnt = row["cnt"]
        pct = round(cnt / total * 100) if total > 0 else 0
        color = PRIORITY_COLORS.get(prio, "#97a0af")
        st.markdown(f"""
        <div style="margin-bottom:10px">
            <div style="display:flex;justify-content:space-between;font-size:12px;color:#5e6c84;margin-bottom:4px">
                <span style="font-weight:600">{prio.capitalize()}</span>
                <span>{cnt} ({pct}%)</span>
            </div>
            <div style="background:#edf0f7;border-radius:100px;height:10px">
                <div style="width:{pct}%;background:{color};height:10px;border-radius:100px;transition:width 0.6s"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_sector_chart(by_sector):
    st.markdown("**Tarefas por Setor**")
    if not by_sector:
        st.info("Sem dados de setor")
        return

    total = sum(r["cnt"] for r in by_sector)
    colors = ["#0052cc","#00875a","#ff5630","#6554c0","#ff991f","#00b8d9","#de350b","#403294"]
    for i, row in enumerate(by_sector):
        sector = row.get("sector","Não definido") or "Não definido"
        cnt = row["cnt"]
        pct = round(cnt / total * 100) if total > 0 else 0
        color = colors[i % len(colors)]
        st.markdown(f"""
        <div style="margin-bottom:10px">
            <div style="display:flex;justify-content:space-between;font-size:12px;color:#5e6c84;margin-bottom:4px">
                <span style="font-weight:600">{sector}</span>
                <span>{cnt} ({pct}%)</span>
            </div>
            <div style="background:#edf0f7;border-radius:100px;height:10px">
                <div style="width:{pct}%;background:{color};height:10px;border-radius:100px"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_weekly_chart(weekly):
    st.markdown("**Conclusões nos Últimos 7 Dias**")
    if not weekly:
        st.info("Nenhuma tarefa concluída nos últimos 7 dias")
        return

    # Ensure all 7 days appear
    today = date.today()
    day_map = {(today - timedelta(days=i)).isoformat(): 0 for i in range(6,-1,-1)}
    for row in weekly:
        if row["day"] in day_map:
            day_map[row["day"]] = row["cnt"]

    max_val = max(day_map.values()) if day_map else 1
    bar_html = '<div style="display:flex;align-items:flex-end;gap:6px;height:120px;padding-bottom:20px;position:relative">'
    for day_str, cnt in day_map.items():
        h_pct = int((cnt / max(max_val,1)) * 100)
        bar_html += f"""
        <div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:2px">
            <span style="font-size:10px;font-weight:700;color:#0052cc">{cnt if cnt else ''}</span>
            <div style="width:100%;background:#0052cc;border-radius:4px 4px 0 0;height:{max(h_pct,2)}px;min-height:4px;
                        transition:height 0.5s"></div>
            <span style="font-size:10px;color:#97a0af">{day_str[-5:]}</span>
        </div>"""
    bar_html += "</div>"
    st.markdown(bar_html, unsafe_allow_html=True)


def _render_monthly_chart(monthly):
    st.markdown("**Conclusões Mensais (12 meses)**")
    if not monthly:
        st.info("Sem dados mensais")
        return

    max_val = max(r["cnt"] for r in monthly) if monthly else 1
    bar_html = '<div style="display:flex;align-items:flex-end;gap:4px;height:120px;padding-bottom:20px">'
    for row in monthly:
        h_pct = int((row["cnt"] / max(max_val,1)) * 100)
        bar_html += f"""
        <div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:2px">
            <span style="font-size:9px;font-weight:700;color:#00875a">{row['cnt'] if row['cnt'] else ''}</span>
            <div style="width:100%;background:#00875a;border-radius:4px 4px 0 0;height:{max(h_pct,2)}px;min-height:4px"></div>
            <span style="font-size:9px;color:#97a0af">{row['month'][5:]}</span>
        </div>"""
    bar_html += "</div>"
    st.markdown(bar_html, unsafe_allow_html=True)


def _render_responsible_table(by_responsible):
    if not by_responsible:
        st.info("Sem dados por responsável")
        return

    max_val = max(r["cnt"] for r in by_responsible) if by_responsible else 1
    table_html = """
    <div style="background:#fff;border-radius:12px;border:1px solid #dde2f0;overflow:hidden">
        <table style="width:100%;border-collapse:collapse">
            <thead>
                <tr style="background:#f7f8fc;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#5e6c84">
                    <th style="padding:10px 16px;text-align:left">Colaborador</th>
                    <th style="padding:10px 16px;text-align:center">Tarefas</th>
                    <th style="padding:10px 16px;text-align:left">Distribuição</th>
                </tr>
            </thead>
            <tbody>
    """
    colors = ["#0052cc","#00875a","#6554c0","#ff991f","#de350b","#00b8d9"]
    for i, row in enumerate(by_responsible):
        name = row.get("name","?") or "?"
        cnt = row["cnt"]
        pct = int((cnt / max_val) * 100)
        color = colors[i % len(colors)]
        initials = "".join(p[0].upper() for p in name.split()[:2])
        table_html += f"""
        <tr style="border-top:1px solid #edf0f7">
            <td style="padding:10px 16px">
                <div style="display:flex;align-items:center;gap:8px">
                    <div class="k-avatar" style="width:28px;height:28px;font-size:11px;background:{color}">{initials}</div>
                    <span style="font-weight:600;color:#172b4d;font-size:13px">{name}</span>
                </div>
            </td>
            <td style="padding:10px 16px;text-align:center;font-weight:700;color:{color}">{cnt}</td>
            <td style="padding:10px 16px">
                <div style="background:#edf0f7;border-radius:100px;height:8px;width:100%">
                    <div style="width:{pct}%;background:{color};height:8px;border-radius:100px"></div>
                </div>
            </td>
        </tr>"""
    table_html += "</tbody></table></div>"
    st.markdown(table_html, unsafe_allow_html=True)
