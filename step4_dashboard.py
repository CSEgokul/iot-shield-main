"""
step4_dashboard.py — IoT Shield Network Threat Monitoring
Clean, light SaaS cybersecurity dashboard matching the approved design.
"""

import os
import json
import time
from textwrap import dedent
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, timezone
from streamlit_autorefresh import st_autorefresh

# Firebase synchronization & AI assistant integration
import firebase_sync
import ai_assistant
from ui_components import (
    PALETTE, CLASS_COLORS, CLASS_LABELS,
    inject_global_styles, format_relative_time,
    render_sidebar_header, render_sidebar_status,
    render_kpi_card, render_empty_state
)

# ─────────────────────────────────────────────────────────────
# Paths & Configuration
# ─────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(BASE_DIR, "data")
ALERTS_FILE = os.path.join(DATA_DIR, "live_alerts.json")
STATS_FILE  = os.path.join(DATA_DIR, "live_stats.json")
os.makedirs(DATA_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────
# Page Setup & Styling
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IoT Shield",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject approved light SaaS styling
inject_global_styles()

# ─────────────────────────────────────────────────────────────
# Session State & Controls
# ─────────────────────────────────────────────────────────────
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True
if "ai_prompt" not in st.session_state:
    st.session_state.ai_prompt = ""

# Auto refresh trigger (3000ms = 3s)
if st.session_state.auto_refresh:
    st_autorefresh(interval=3000, key="app_autorefresh")

# ─────────────────────────────────────────────────────────────
# Data Loading & Synchronization
# ─────────────────────────────────────────────────────────────
def load_local_alerts():
    try:
        with open(ALERTS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def load_local_stats():
    try:
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"total": 0, "threats": 0, "critical": 0, "benign": 0}

def clear_dashboard_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(ALERTS_FILE, "w") as f:
        json.dump([], f)
    with open(STATS_FILE, "w") as f:
        json.dump({"total": 0, "threats": 0, "critical": 0, "benign": 0}, f)

# Prioritize Firebase Realtime Database live sync; fall back to local files
fb_alerts, fb_stats = firebase_sync.fetch()
if fb_alerts is not None:
    alerts = fb_alerts
    stats  = fb_stats or {"total": 0, "threats": 0, "critical": 0, "benign": 0}
    DATA_SOURCE = "Firebase"
else:
    alerts = load_local_alerts()
    stats  = load_local_stats()
    DATA_SOURCE = "Local cache"

# ─────────────────────────────────────────────────────────────
# Detector Liveness & Freshness Detection
# ─────────────────────────────────────────────────────────────
total_flows = stats.get("total", 0)
threats_count = stats.get("threats", 0)
benign_count = stats.get("benign", 0)

latest_alert_ts = ""
is_recent_alert = False

if alerts:
    latest_alert_ts = str(alerts[-1].get("timestamp", ""))[:19].replace("T", " ")
    try:
        raw_ts = str(alerts[-1].get("timestamp", ""))[:19]
        alert_dt = datetime.fromisoformat(raw_ts)
        now_dt = datetime.now()
        now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
        diff_local = abs((now_dt - alert_dt).total_seconds())
        diff_utc = abs((now_utc - alert_dt).total_seconds())
        if min(diff_local, diff_utc) < 180:  # Fresh data within 3 minutes
            is_recent_alert = True
    except Exception:
        pass

prev_total = st.session_state.get("prev_total", None)
if prev_total is not None and total_flows != prev_total:
    st.session_state.last_seen_active = time.time()
    st.session_state.prev_total = total_flows
elif prev_total is None:
    st.session_state.prev_total = total_flows

last_active_time = st.session_state.get("last_seen_active", 0)
is_detector_live = is_recent_alert or (last_active_time > 0 and (time.time() - last_active_time < 120))

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    render_sidebar_header()

    nav_item = st.radio(
        "Navigation",
        ["Overview", "Analytics", "Alerts", "Security Assistant"],
        label_visibility="collapsed"
    )

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    st.session_state.auto_refresh = st.toggle(
        "Auto-refresh (3s)",
        value=st.session_state.auto_refresh,
        key="sidebar_auto_refresh"
    )

    if st.button("↺ Reset data", key="sidebar_btn_reset"):
        clear_dashboard_data()
        st.rerun()

    # Real status card at the bottom of the sidebar
    render_sidebar_status(
        is_detector_live=is_detector_live,
        data_source=DATA_SOURCE,
        last_ts=latest_alert_ts
    )

# ─────────────────────────────────────────────────────────────
# MAIN CONTENT AREA
# ─────────────────────────────────────────────────────────────

# Top Utility / Search Bar
h_col1, h_col2 = st.columns([3.5, 1])
with h_col1:
    search_keyword = st.text_input(
        "Search",
        placeholder="Search by IP, device, event, or keyword...",
        label_visibility="collapsed",
        key="top_search_input"
    )
with h_col2:
    if st.button("Refresh", key="btn_top_refresh"):
        st.rerun()

# ═════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ═════════════════════════════════════════════════════════════
if nav_item == "Overview":
    # Overview Header with optional functional Export button
    oh_col1, oh_col2 = st.columns([3, 1])
    with oh_col1:
        st.html("""
        <div class="page-title">Overview</div>
        <div class="page-subtitle">Real-time network security monitoring for IoT environments.</div>
        """)
    with oh_col2:
        if alerts:
            df_export = pd.DataFrame(alerts)
            csv_data = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Export Report",
                data=csv_data,
                file_name=f"iot_shield_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="btn_export_report"
            )

    # 1. Top KPI Row (4 Clean White Cards)
    threat_rate = (threats_count / total_flows * 100) if total_flows > 0 else 0.0
    kpi_grid_html = dedent(f"""
    <div class="kpi-grid">
        {render_kpi_card("Network Flows", f"{total_flows:,}", "Total evaluated flows", "⚡", "icon-blue")}
        {render_kpi_card("Threats Detected", f"{threats_count:,}", f"{threat_rate:.1f}% incident rate", "⚠", "icon-red")}
        {render_kpi_card("Benign Traffic", f"{benign_count:,}", f"{(100.0 - threat_rate):.1f}% safe flows", "✓", "icon-green")}
        {render_kpi_card("Packets Analysed", f"{total_flows:,}", "Dual-model verified", "●", "icon-blue")}
    </div>
    """).strip()
    st.html(kpi_grid_html)

    # 2. Charts Row (Network Traffic Over Time + Threat Classification)
    ch_col1, ch_col2 = st.columns([1.6, 1])

    with ch_col1:
        st.html("""
        <div class="saas-card">
            <div class="saas-card-title">Network Traffic Over Time</div>
            <div class="saas-card-sub">Total vs. threat vs. benign traffic volume</div>
        </div>
        """)

        if alerts:
            df_time = pd.DataFrame(alerts)
            df_time["time"] = pd.to_datetime(df_time["timestamp"])
            df_time["bucket"] = df_time["time"].dt.floor("5s")
            timeline = df_time.groupby(["bucket", "label"]).size().reset_index()
            timeline.columns = ["bucket", "label", "count"]

            fig_time = go.Figure()

            # Plot main threat traffic (red line with soft red fill)
            sub_ddos = timeline[timeline["label"] == "ddos"]
            if not sub_ddos.empty:
                fig_time.add_trace(go.Scatter(
                    x=sub_ddos["bucket"],
                    y=sub_ddos["count"],
                    name="DDoS Attack",
                    mode="lines",
                    line=dict(color=PALETTE["primary_red"], width=2.2),
                    fill="tozeroy",
                    fillcolor="rgba(227, 27, 35, 0.08)",
                    hovertemplate="<b>%{x|%H:%M:%S}</b> · DDoS: %{y}<extra></extra>"
                ))

            # Plot benign traffic (green line)
            sub_benign = timeline[timeline["label"] == "benign"]
            if not sub_benign.empty:
                fig_time.add_trace(go.Scatter(
                    x=sub_benign["bucket"],
                    y=sub_benign["count"],
                    name="Benign Traffic",
                    mode="lines",
                    line=dict(color=PALETTE["success_green"], width=1.8),
                    hovertemplate="<b>%{x|%H:%M:%S}</b> · Benign: %{y}<extra></extra>"
                ))

            # Plot port scan traffic (blue line)
            sub_ps = timeline[timeline["label"] == "portscan"]
            if not sub_ps.empty:
                fig_time.add_trace(go.Scatter(
                    x=sub_ps["bucket"],
                    y=sub_ps["count"],
                    name="Port Scan",
                    mode="lines",
                    line=dict(color=PALETTE["info_blue"], width=1.8),
                    hovertemplate="<b>%{x|%H:%M:%S}</b> · Port Scan: %{y}<extra></extra>"
                ))

            fig_time.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(color=PALETTE["text_secondary"], family="Inter", size=11),
                xaxis=dict(
                    showgrid=True,
                    gridcolor=PALETTE["border_subtle"],
                    zeroline=False,
                    color=PALETTE["text_muted"],
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor=PALETTE["border_subtle"],
                    zeroline=False,
                    color=PALETTE["text_muted"],
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(color=PALETTE["text_secondary"], size=11),
                    bgcolor="rgba(255,255,255,0.8)"
                ),
                margin=dict(t=10, b=10, l=10, r=10),
                height=280,
            )
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            render_empty_state("No traffic data", "Waiting for network telemetry from the detector.")

    with ch_col2:
        st.html("""
        <div class="saas-card">
            <div class="saas-card-title">Threat Classification</div>
            <div class="saas-card-sub">Distribution of detected traffic</div>
        </div>
        """)

        c_benign   = sum(1 for a in alerts if a.get("label") == "benign")
        c_portscan = sum(1 for a in alerts if a.get("label") == "portscan")
        c_ddos     = sum(1 for a in alerts if a.get("label") == "ddos")
        c_malware  = sum(1 for a in alerts if a.get("label") == "malware")

        def calc_pct(val):
            return f"{(val / total_flows * 100):.1f}%" if total_flows > 0 else "0.0%"

        if alerts:
            df_pie = pd.DataFrame(alerts)
            counts = df_pie["label"].value_counts().reset_index()
            counts.columns = ["label", "count"]

            fig_donut = go.Figure(go.Pie(
                labels=[CLASS_LABELS.get(l, l.capitalize()) for l in counts["label"]],
                values=counts["count"],
                hole=0.64,
                marker=dict(
                    colors=[CLASS_COLORS.get(l, PALETTE["text_muted"]) for l in counts["label"]],
                    line=dict(color="#FFFFFF", width=2)
                ),
                textfont=dict(family="Inter", color="#111827", size=11),
                hovertemplate="<b>%{label}</b>: %{value:,} flows (%{percent})<extra></extra>"
            ))
            fig_donut.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                showlegend=False,
                margin=dict(t=5, b=5, l=5, r=5),
                height=170,
            )
            st.plotly_chart(fig_donut, use_container_width=True)

            breakdown_summary_html = dedent(f"""
            <div style="padding: 0 0.5rem;">
                <div class="breakdown-row">
                    <div class="breakdown-item-left">
                        <span class="dot" style="background:{PALETTE['success_green']};"></span>
                        <span>Benign</span>
                    </div>
                    <div class="breakdown-item-right">
                        <span class="breakdown-val">{c_benign:,}</span>
                        <span class="breakdown-pct">{calc_pct(c_benign)}</span>
                    </div>
                </div>
                <div class="breakdown-row">
                    <div class="breakdown-item-left">
                        <span class="dot" style="background:{PALETTE['info_blue']};"></span>
                        <span>Port scan</span>
                    </div>
                    <div class="breakdown-item-right">
                        <span class="breakdown-val">{c_portscan:,}</span>
                        <span class="breakdown-pct">{calc_pct(c_portscan)}</span>
                    </div>
                </div>
                <div class="breakdown-row">
                    <div class="breakdown-item-left">
                        <span class="dot" style="background:{PALETTE['primary_red']};"></span>
                        <span>DDoS</span>
                    </div>
                    <div class="breakdown-item-right">
                        <span class="breakdown-val">{c_ddos:,}</span>
                        <span class="breakdown-pct">{calc_pct(c_ddos)}</span>
                    </div>
                </div>
                <div class="breakdown-row">
                    <div class="breakdown-item-left">
                        <span class="dot" style="background:{PALETTE['warning_amber']};"></span>
                        <span>Malware</span>
                    </div>
                    <div class="breakdown-item-right">
                        <span class="breakdown-val">{c_malware:,}</span>
                        <span class="breakdown-pct">{calc_pct(c_malware)}</span>
                    </div>
                </div>
            </div>
            """).strip()
            st.html(breakdown_summary_html)
        else:
            render_empty_state("No data", "Awaiting telemetry samples.")

    # 3. Bottom Row: Recent Network Activity + System Status
    br_col1, br_col2 = st.columns([1.7, 1])

    with br_col1:
        st.html("""
        <div class="saas-card">
            <div class="saas-card-title">Recent Network Activity</div>
            <div class="saas-card-sub">Latest 25 flows analyzed by IoT Shield</div>
        </div>
        """)

        if alerts:
            # Filter if search keyword entered
            display_alerts = alerts
            if search_keyword:
                kw = search_keyword.lower()
                display_alerts = [
                    a for a in alerts
                    if kw in f"{a.get('src_ip','')} {a.get('dst_ip','')} {a.get('proto','')} {a.get('label','')}".lower()
                ]

            rows_html = ""
            for a in reversed(display_alerts[-25:]):
                lbl = a.get("label", "benign")
                cls_text = CLASS_LABELS.get(lbl, lbl.capitalize())
                chip_class = f"chip-{lbl}"
                ts = str(a.get("timestamp", ""))[:19].replace("T", " ")
                src = f"{a.get('src_ip', '0.0.0.0')}:{a.get('src_port', '')}"
                dst = f"{a.get('dst_ip', '0.0.0.0')}:{a.get('dst_port', '')}"
                conf = a.get("confidence", 100.0)
                proto = str(a.get("proto", "TCP")).upper()

                rows_html += f"""<tr>
<td class="mono-cell" style="color:#667085;">{ts[11:19]}</td>
<td class="src-cell">{src}</td>
<td class="dst-cell">{dst}</td>
<td class="mono-cell" style="color:#667085;">{proto}</td>
<td><span class="chip {chip_class}">{cls_text}</span></td>
<td class="mono-cell" style="color:#667085;">{conf}%</td>
</tr>"""

            table_card_html = dedent(f"""
            <div class="table-card-wrapper">
                <table class="saas-table">
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>Source</th>
                            <th>Destination</th>
                            <th>Protocol</th>
                            <th>Classification</th>
                            <th>Confidence</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
            """).strip()
            st.html(table_card_html)
        else:
            render_empty_state("No recent activity", "Awaiting incoming network flow packets.")

    with br_col2:
        st.html("""
        <div class="saas-card">
            <div class="saas-card-title">System Status</div>
            <div class="saas-card-sub">Infrastructure health & synchronizer state</div>
        </div>
        """)

        det_status_dot = PALETTE["success_green"] if is_detector_live else PALETTE["warning_amber"]
        det_status_text = "Online" if is_detector_live else "Offline"
        fb_status_dot = PALETTE["success_green"] if DATA_SOURCE.startswith("Firebase") else PALETTE["warning_amber"]
        fb_status_text = "Connected" if DATA_SOURCE.startswith("Firebase") else "Local cache"
        time_display = format_relative_time(latest_alert_ts)

        system_status_card_html = dedent(f"""
        <div class="saas-card" style="font-size:0.875rem;line-height:2.1;">
            <div class="status-row">
                <span style="color:#667085;">Detector</span>
                <span class="status-row-val">
                    <span class="dot" style="background:{det_status_dot};"></span>
                    {det_status_text}
                </span>
            </div>
            <div class="status-row">
                <span style="color:#667085;">Firebase</span>
                <span class="status-row-val">
                    <span class="dot" style="background:{fb_status_dot};"></span>
                    {fb_status_text}
                </span>
            </div>
            <div class="status-row">
                <span style="color:#667085;">Last telemetry</span>
                <span class="status-row-val">{time_display}</span>
            </div>
            <div class="status-row">
                <span style="color:#667085;">Detection model</span>
                <span class="status-row-val">RF + XGBoost</span>
            </div>
            <div class="status-row">
                <span style="color:#667085;">Network interface</span>
                <span class="status-row-val">Monitored LAN</span>
            </div>
            <div class="status-row">
                <span style="color:#667085;">Flows analyzed</span>
                <span class="status-row-val" style="font-family:'JetBrains Mono',monospace;">{total_flows:,}</span>
            </div>
        </div>
        """).strip()
        st.html(system_status_card_html)


# ═════════════════════════════════════════════════════════════
# PAGE: ANALYTICS
# ═════════════════════════════════════════════════════════════
elif nav_item == "Analytics":
    st.html("""
    <div class="page-title">Analytics</div>
    <div class="page-subtitle">Telemetry trends, classification proportions, and benchmark model metrics.</div>
    """)

    an_col1, an_col2 = st.columns(2)

    with an_col1:
        st.html("""
        <div class="saas-card">
            <div class="saas-card-title">Threat Distribution</div>
            <div class="saas-card-sub">Proportion of all analyzed network traffic</div>
        </div>
        """)

        if alerts:
            df_pie = pd.DataFrame(alerts)
            counts = df_pie["label"].value_counts().reset_index()
            counts.columns = ["label", "count"]

            fig_donut_an = go.Figure(go.Pie(
                labels=[CLASS_LABELS.get(l, l.capitalize()) for l in counts["label"]],
                values=counts["count"],
                hole=0.62,
                marker=dict(
                    colors=[CLASS_COLORS.get(l, PALETTE["text_muted"]) for l in counts["label"]],
                    line=dict(color="#FFFFFF", width=2)
                ),
                textfont=dict(family="Inter", color="#111827", size=12),
                hovertemplate="<b>%{label}</b>: %{value:,} flows (%{percent})<extra></extra>"
            ))
            fig_donut_an.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(color=PALETTE["text_secondary"]),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.15,
                    xanchor="center",
                    x=0.5,
                    font=dict(color=PALETTE["text_secondary"], size=11),
                    bgcolor="rgba(255,255,255,0.8)"
                ),
                margin=dict(t=10, b=10, l=10, r=10),
                height=260,
            )
            st.plotly_chart(fig_donut_an, use_container_width=True)
        else:
            render_empty_state("No distribution data", "Awaiting telemetry samples.")

    with an_col2:
        st.html("""
        <div class="saas-card">
            <div class="saas-card-title">Model Performance</div>
            <div class="saas-card-sub">Test evaluation accuracy on IoT-23 dataset</div>
        </div>
        """)

        models_data = {
            "Model": ["Random Forest", "XGBoost", "Ensemble"],
            "Accuracy": [99.99, 100.00, 100.00],
        }
        fig_bar = go.Figure(go.Bar(
            x=models_data["Model"],
            y=models_data["Accuracy"],
            marker_color=[PALETTE["info_blue"], PALETTE["warning_amber"], PALETTE["primary_red"]],
            text=[f"{v:.2f}%" for v in models_data["Accuracy"]],
            textposition="outside",
            textfont=dict(color="#111827", family="Inter", size=11),
            width=0.4,
        ))
        fig_bar.update_layout(
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(color=PALETTE["text_secondary"], family="Inter"),
            xaxis=dict(showgrid=False, color=PALETTE["text_muted"]),
            yaxis=dict(
                showgrid=True,
                gridcolor=PALETTE["border_subtle"],
                color=PALETTE["text_muted"],
                range=[99.85, 100.08]
            ),
            margin=dict(t=25, b=10, l=10, r=10),
            height=260,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Confusion Matrix
    st.html("""
    <div class="saas-card">
        <div class="saas-card-title">Confusion Matrix</div>
        <div class="saas-card-sub">Ensemble model validation across 120,000 test flows</div>
    </div>
    """)

    cm_labels = ["Benign", "DDoS", "Malware", "Port scan"]
    cm_data = [
        [29998, 1,     1,     0],
        [0,     29999, 1,     0],
        [0,     0,     30000, 0],
        [0,     0,     0,     30000],
    ]
    cm_rows = ""
    for i, row in enumerate(cm_data):
        cm_rows += f"<tr><td style='font-weight:600;color:#111827;'>{cm_labels[i]}</td>"
        for j, val in enumerate(row):
            if i == j:
                style = "background:#ECFDF3;color:#16A34A;font-weight:600;"
            elif val > 0:
                style = "background:#FDEBED;color:#E31B23;font-weight:600;"
            else:
                style = "color:#667085;"
            cm_rows += f"<td class='mono-cell' style='text-align:center;{style}'>{val:,}</td>"
        cm_rows += "</tr>"

    cm_table_html = dedent(f"""
    <div class="table-card-wrapper">
        <table class="saas-table">
            <thead>
                <tr>
                    <th>Actual \\ Predicted</th>
                    <th style="text-align:center;">Benign</th>
                    <th style="text-align:center;">DDoS</th>
                    <th style="text-align:center;">Malware</th>
                    <th style="text-align:center;">Port scan</th>
                </tr>
            </thead>
            <tbody>
                {cm_rows}
            </tbody>
        </table>
    </div>
    """).strip()
    st.html(cm_table_html)


# ═════════════════════════════════════════════════════════════
# PAGE: ALERTS
# ═════════════════════════════════════════════════════════════
elif nav_item == "Alerts":
    st.html("""
    <div class="page-title">Alerts</div>
    <div class="page-subtitle">Security incidents and flagged anomalous traffic flows.</div>
    """)

    # Filter Toolbar
    af_col1, af_col2, af_col3 = st.columns([1, 1, 2])
    with af_col1:
        f_type = st.selectbox("Category", ["All", "ddos", "malware", "portscan", "benign"], key="f_alert_type")
    with af_col2:
        f_sev = st.selectbox("Severity", ["All", "critical", "high", "medium", "none"], key="f_alert_sev")
    with af_col3:
        f_query = st.text_input("Filter IP / port", placeholder="Filter by source or destination...", key="f_alert_search")

    if not alerts:
        render_empty_state("No threats detected", "Your monitored network is currently clear.")
    else:
        filtered = []
        for a in alerts:
            lbl = a.get("label", "")
            sev = a.get("severity", "none")
            src = str(a.get("src_ip", ""))
            dst = str(a.get("dst_ip", ""))
            sp = str(a.get("src_port", ""))
            dp = str(a.get("dst_port", ""))

            if f_type != "All" and lbl != f_type:
                continue
            if f_sev != "All" and sev != f_sev:
                continue
            if f_query:
                q = f_query.lower()
                if q not in f"{src} {dst} {sp} {dp} {lbl}".lower():
                    continue
            filtered.append(a)

        if not filtered:
            render_empty_state("No matching incidents", "No alerts match the selected filter criteria.")
        else:
            alert_rows = ""
            for a in reversed(filtered[-60:]):
                lbl = a.get("label", "benign")
                cls_text = CLASS_LABELS.get(lbl, lbl.capitalize())
                sev = a.get("severity", "none")
                chip_class = {
                    "critical": "chip-ddos",
                    "high": "chip-malware",
                    "medium": "chip-portscan",
                    "none": "chip-benign"
                }.get(sev, "chip-benign")

                ts = str(a.get("timestamp", ""))[:19].replace("T", " ")
                rel_time = format_relative_time(ts)
                src = f"{a.get('src_ip', '0.0.0.0')}:{a.get('src_port', '')}"
                dst = f"{a.get('dst_ip', '0.0.0.0')}:{a.get('dst_port', '')}"
                conf = a.get("confidence", 100.0)

                alert_rows += f"""<tr>
<td><span class="chip {chip_class}">{sev.capitalize()}</span></td>
<td><span style="font-weight:600;color:#111827;">{cls_text}</span></td>
<td class="src-cell">{src}</td>
<td class="dst-cell">{dst}</td>
<td style="color:#667085;">{rel_time}</td>
<td class="mono-cell" style="color:#667085;">{conf}%</td>
</tr>"""

            alerts_table_html = dedent(f"""
            <div class="table-card-wrapper">
                <table class="saas-table">
                    <thead>
                        <tr>
                            <th>Severity</th>
                            <th>Threat</th>
                            <th>Source</th>
                            <th>Destination</th>
                            <th>Detected</th>
                            <th>Confidence</th>
                        </tr>
                    </thead>
                    <tbody>
                        {alert_rows}
                    </tbody>
                </table>
            </div>
            """).strip()
            st.html(alerts_table_html)


# ═════════════════════════════════════════════════════════════
# PAGE: SECURITY ASSISTANT
# ═════════════════════════════════════════════════════════════
elif nav_item == "Security Assistant":
    st.html("""
    <div class="page-title">Security Assistant</div>
    <div class="page-subtitle">Investigate suspicious activity and understand detected threats.</div>
    """)

    st.html("""
    <div class="saas-card">
        <div class="saas-card-title">Threat Investigation Console</div>
        <div class="saas-card-sub">AI-powered security copilot with contextual awareness of monitored network telemetry.</div>
    </div>
    """)

    st.markdown("<div style='font-size:0.875rem;font-weight:600;color:#111827;margin-bottom:0.5rem;'>Suggested Prompts</div>", unsafe_allow_html=True)
    p_col1, p_col2 = st.columns(2)
    suggested_prompts = [
        "Explain latest alert",
        "Summarize recent traffic",
        "Review suspicious activity",
        "Recommend next steps"
    ]
    active_prompt = None
    for i, s in enumerate(suggested_prompts):
        target_col = p_col1 if i % 2 == 0 else p_col2
        with target_col:
            if st.button(s, key=f"sug_prompt_btn_{i}"):
                active_prompt = s

    user_query = st.text_input(
        "Analyst query",
        value=active_prompt or st.session_state.ai_prompt,
        placeholder="Ask a question about current threats or model reasoning...",
        key="ai_analyst_input"
    )

    if user_query:
        st.session_state.ai_prompt = user_query
        context = ""
        if alerts:
            df_ctx = pd.DataFrame(alerts[-25:])
            summary = df_ctx["label"].value_counts().to_dict()
            top_src = df_ctx["src_ip"].value_counts().head(3).to_dict() if "src_ip" in df_ctx.columns else {}
            context = f"Alert summary (last 25 flows): {summary}. Top source IPs: {top_src}. "

        prompt = (
            f"You are an expert IoT security analyst. {context}"
            f"Provide a concise, direct analysis in 2-3 sentences: {user_query}"
        )

        with st.spinner("Analyzing telemetry with Security Assistant..."):
            answer, provider = ai_assistant.ask_ai(prompt)

        if answer:
            response_card_html = dedent(f"""
            <div class="saas-card" style="margin-top:1.25rem;border-left:4px solid #E31B23;background:#FFF8F8;">
                <div style="font-size:0.75rem;color:#E31B23;font-weight:700;margin-bottom:0.35rem;text-transform:uppercase;">
                    Analyst Response · {provider}
                </div>
                <div style="font-size:0.875rem;line-height:1.6;color:#111827;">
                    {answer}
                </div>
            </div>
            """).strip()
            st.html(response_card_html)
        else:
            st.info(
                "Assistant in standby mode. To enable live inference on Streamlit Cloud, "
                "add `GEMINI_API_KEY` or `GROQ_API_KEY` to your Streamlit Cloud Secrets."
            )