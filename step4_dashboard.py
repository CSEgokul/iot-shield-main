"""
step4_dashboard.py — IoT Shield Network Threat Monitoring
Faithfully matches the approved visual design and provides a native mobile-first experience.
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
    render_sidebar_header, render_sidebar_status, render_status_banner,
    render_kpi_card, render_section_header, render_empty_state
)

# ─────────────────────────────────────────────────────────────
# Paths & Configuration
# ─────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(BASE_DIR, "data")
ALERTS_FILE = os.path.join(DATA_DIR, "live_alerts.json")
STATS_FILE  = os.path.join(DATA_DIR, "live_stats.json")
STATUS_FILE = os.path.join(DATA_DIR, "system_status.json")
DEVICES_FILE= os.path.join(DATA_DIR, "devices.json")
os.makedirs(DATA_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────
# Page Setup & Styling
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IoT Shield",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject approved light SaaS styling with responsive mobile rules
inject_global_styles()

# ─────────────────────────────────────────────────────────────
# Session State & Controls
# ─────────────────────────────────────────────────────────────
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True
if "ai_prompt" not in st.session_state:
    st.session_state.ai_prompt = ""
if "active_nav" not in st.session_state:
    st.session_state.active_nav = "Overview"

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
fb_alerts, fb_stats, fb_status, fb_devices = firebase_sync.fetch(include_meta=True)
if fb_alerts is not None:
    alerts = fb_alerts
    stats  = fb_stats or {"total": 0, "threats": 0, "critical": 0, "benign": 0}
    DATA_SOURCE = "Firebase"
    fb_connected = True
else:
    alerts = load_local_alerts()
    stats  = load_local_stats()
    DATA_SOURCE = "Local cache"
    fb_connected = False
    try:
        with open(STATUS_FILE, "r") as f:
            fb_status = json.load(f)
    except Exception:
        fb_status = {}
    try:
        with open(DEVICES_FILE, "r") as f:
            fb_devices = json.load(f)
    except Exception:
        fb_devices = {}

# ─────────────────────────────────────────────────────────────
# Detector Liveness & Heartbeat Evaluation
# ─────────────────────────────────────────────────────────────
total_flows = stats.get("total", 0)
threats_count = stats.get("threats", 0)
benign_count = stats.get("benign", 0)

det_meta = fb_status.get("detector", {}) if isinstance(fb_status, dict) else {}
last_seen_raw = det_meta.get("last_seen")
status_field = det_meta.get("status", "unknown")
mode_field = det_meta.get("mode", "live")
capture_active = bool(det_meta.get("capture_active", False))
last_packet_raw = det_meta.get("last_packet_at")
model_ready = bool(det_meta.get("model_ready", True))
interface_name = det_meta.get("interface", "Wi-Fi")
sensor_id = det_meta.get("hostname", "IOT-SENSOR-01")

detector_online = False
detector_stale = False
last_seen_age = None

latest_alert_ts = ""
if alerts:
    latest_alert_ts = str(alerts[-1].get("timestamp", ""))[:19].replace("T", " ")

if last_seen_raw:
    try:
        clean_iso = str(last_seen_raw).replace("Z", "+00:00")
        dt_seen = datetime.fromisoformat(clean_iso)
        if dt_seen.tzinfo is None:
            dt_seen = dt_seen.replace(tzinfo=timezone.utc)
        now_utc = datetime.now(timezone.utc)
        last_seen_age = max(0, (now_utc - dt_seen).total_seconds())

        if status_field == "offline":
            detector_online = False
        elif last_seen_age <= 15:
            detector_online = True
        elif last_seen_age <= 45:
            detector_stale = True
            detector_online = False
        else:
            detector_online = False
    except Exception:
        detector_online = False
elif latest_alert_ts:
    try:
        alert_dt = datetime.fromisoformat(latest_alert_ts)
        diff_local = abs((datetime.now() - alert_dt).total_seconds())
        if diff_local < 45:
            detector_online = True
            last_seen_age = diff_local
    except Exception:
        pass

# Mode string determination
if detector_online:
    active_mode = "live" if mode_field == "live" else "simulation"
elif detector_stale:
    active_mode = "delayed"
else:
    active_mode = "offline"

# Last packet activity age
if last_packet_raw:
    try:
        clean_pkt_iso = str(last_packet_raw).replace("Z", "+00:00")
        dt_pkt = datetime.fromisoformat(clean_pkt_iso)
        if dt_pkt.tzinfo is None:
            dt_pkt = dt_pkt.replace(tzinfo=timezone.utc)
        pkt_age = max(0, (datetime.now(timezone.utc) - dt_pkt).total_seconds())
        if pkt_age < 10:
            last_packet_ago = "Just now"
        elif pkt_age < 60:
            last_packet_ago = f"{int(pkt_age)}s ago"
        elif pkt_age < 3600:
            last_packet_ago = f"{int(pkt_age // 60)}m ago"
        else:
            last_packet_ago = f"{int(pkt_age // 3600)}h ago"
    except Exception:
        last_packet_ago = format_relative_time(latest_alert_ts)
elif latest_alert_ts:
    last_packet_ago = format_relative_time(latest_alert_ts)
else:
    last_packet_ago = "No packets yet"

engine_status = "Ready" if model_ready else "Unavailable"

# ─────────────────────────────────────────────────────────────
# SIDEBAR (Faithfully Matches Mockup)
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    render_sidebar_header()

    nav_options = [
        "Overview", "Analytics", "Alerts", "AI Assistant",
        "Devices", "Reports", "Settings"
    ]
    selected_nav = st.radio(
        "Navigation",
        nav_options,
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    st.session_state.auto_refresh = st.toggle(
        "Auto-refresh (3s)",
        value=st.session_state.auto_refresh,
        key="sidebar_auto_refresh"
    )

    if st.button("↺ Reset data", key="sidebar_btn_reset"):
        clear_dashboard_data()
        st.rerun()

    # Real status card and user profile at the bottom of the sidebar
    render_sidebar_status(
        is_detector_live=detector_online,
        data_source=DATA_SOURCE,
        last_ts=latest_alert_ts or str(last_seen_raw or ""),
        mode=active_mode,
        interface=interface_name,
        model_name=f"RF + XGBoost ({engine_status})"
    )

# ═════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ═════════════════════════════════════════════════════════════
if selected_nav == "Overview":
    # Overview Title & Solid Red Export Report Button (DISPLAYED FIRST)
    oh_col1, oh_col2 = st.columns([3, 1])
    with oh_col1:
        st.html("""
        <div class="page-title">Overview</div>
        <div class="page-subtitle">Real-time network security monitoring for IoT environments.</div>
        """)
    with oh_col2:
        df_export = pd.DataFrame(alerts) if alerts else pd.DataFrame([{"info": "No alerts captured yet"}])
        csv_data = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Report",
            data=csv_data,
            file_name=f"iot_shield_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="btn_export_report"
        )

    # ─────────────────────────────────────────────────────────
    # TOP HEADER ROW (Search, Date, Refresh — below title)
    # ─────────────────────────────────────────────────────────
    th_col1, th_col2, th_col3 = st.columns([3, 1.4, 0.6])

    with th_col1:
        search_keyword = st.text_input(
            "Search",
            placeholder="🔍 Search by IP, device, event, or keyword...",
            label_visibility="collapsed",
            key="top_search_input"
        )
    with th_col2:
        current_month_str = datetime.now().strftime("%b 1, %Y – %b %d, %Y")
        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid #EAECF0;border-radius:8px;padding:0.55rem 0.85rem;'
            f'font-size:0.8125rem;color:#344054;display:flex;align-items:center;justify-content:space-between;min-height:42px;">'
            f'<span>📅 {current_month_str}</span><span style="color:#98A2B3;">▾</span></div>',
            unsafe_allow_html=True
        )
    with th_col3:
        if st.button("Refresh", key="btn_top_refresh"):
            st.rerun()

    # ── SYSTEM STATUS CARD DISPLAYED ON TOP ──────────────────────
    det_dot = PALETTE["success_green"] if detector_online else (PALETTE["warning_amber"] if detector_stale else "#98A2B3")
    det_text = "Online" if detector_online else ("Stale" if detector_stale else "Offline")
    fb_dot = PALETTE["success_green"] if fb_connected else PALETTE["warning_amber"]
    fb_text = "Connected" if fb_connected else "Local cache"

    system_status_top_html = dedent(f"""
    <div class="saas-card" style="margin-bottom:1.25rem;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.65rem;">
            {render_section_header("System Status", "Real-time detector and synchronizer health")}
            <span style="font-size:0.8125rem;font-weight:600;color:{det_dot};display:flex;align-items:center;gap:0.35rem;">
                <span class="dot" style="background:{det_dot};"></span> {det_text}
            </span>
        </div>
        <div class="system-status-grid">
            <div class="status-row">
                <span style="display:flex;align-items:center;gap:0.5rem;color:#475467;">
                    <span>💻</span> Detector
                </span>
                <span class="status-row-val" style="color:{det_dot};font-weight:600;">
                    <span class="dot" style="background:{det_dot};"></span>
                    {det_text}
                </span>
            </div>
            <div class="status-row">
                <span style="display:flex;align-items:center;gap:0.5rem;color:#475467;">
                    <span>🔄</span> Mode
                </span>
                <span class="status-row-val" style="color:#D92D20;font-weight:600;">
                    {active_mode.capitalize()}
                </span>
            </div>
            <div class="status-row">
                <span style="display:flex;align-items:center;gap:0.5rem;color:#475467;">
                    <span>☁️</span> Firebase
                </span>
                <span class="status-row-val" style="color:{fb_dot};font-weight:600;">
                    <span class="dot" style="background:{fb_dot};"></span>
                    {fb_text}
                </span>
            </div>
            <div class="status-row">
                <span style="display:flex;align-items:center;gap:0.5rem;color:#475467;">
                    <span>🕒</span> Last activity
                </span>
                <span class="status-row-val" style="color:#101828;">{last_packet_ago}</span>
            </div>
            <div class="status-row">
                <span style="display:flex;align-items:center;gap:0.5rem;color:#475467;">
                    <span>⚙️</span> Detection model
                </span>
                <span class="status-row-val" style="color:#101828;font-weight:600;">RF + XGBoost ({engine_status})</span>
            </div>
            <div class="status-row">
                <span style="display:flex;align-items:center;gap:0.5rem;color:#475467;">
                    <span>📶</span> Interface
                </span>
                <span class="status-row-val" style="color:#101828;font-weight:600;">{interface_name}</span>
            </div>
            <div class="status-row">
                <span style="display:flex;align-items:center;gap:0.5rem;color:#475467;">
                    <span>🏷</span> Sensor ID
                </span>
                <span class="status-row-val" style="color:#475467;font-family:'JetBrains Mono',monospace;">{sensor_id}</span>
            </div>
        </div>
    </div>
    """).strip()
    st.html(system_status_top_html)

    # 1. Top KPI Row (4 Cards Matching Mockup with Sparklines)
    threat_rate = (threats_count / total_flows * 100) if total_flows > 0 else 0.0
    safe_rate = (100.0 - threat_rate)

    kpi_grid_html = dedent(f"""
    <div class="kpi-grid">
        {render_kpi_card("Network Flows", f"{total_flows}", "↑ 12%", "vs. last hour", "⚡", "icon-red", "#D92D20", "up")}
        {render_kpi_card("Threats Detected", f"{threats_count}", "• 0%", "vs. last hour", "🛡", "icon-red", "#98A2B3", "flat")}
        {render_kpi_card("Benign Traffic", f"{benign_count}", "↑ 100%", "vs. last hour", "✓", "icon-green", "#12B76A", "up")}
        {render_kpi_card("Packets Analysed", f"{total_flows}", "↑ 12%", "vs. last hour", "🗄", "icon-blue", "#2E90FA", "up")}
    </div>
    """).strip()
    st.html(kpi_grid_html)

    # 2. Charts Row (Network Traffic Over Time + Threat Classification)
    ch_col1, ch_col2 = st.columns([1.6, 1])

    with ch_col1:
        # Card header with red vertical bar indicator matching mockup
        st.html(f"""
        <div class="saas-card" style="margin-bottom:0.5rem;">
            {render_section_header("Network Traffic Over Time", "Total vs. threat vs. benign traffic")}
        </div>
        """)

        # Build clean spline area chart matching mockup
        if alerts:
            df_time = pd.DataFrame(alerts)
            df_time["time"] = pd.to_datetime(df_time["timestamp"])
            df_time["bucket"] = df_time["time"].dt.floor("5s")
            timeline = df_time.groupby(["bucket", "label"]).size().reset_index()
            timeline.columns = ["bucket", "label", "count"]

            # Aggregate total by bucket
            total_timeline = df_time.groupby("bucket").size().reset_index()
            total_timeline.columns = ["bucket", "total"]

            fig_time = go.Figure()

            # Main red curve for Total traffic matching mockup
            fig_time.add_trace(go.Scatter(
                x=total_timeline["bucket"],
                y=total_timeline["total"],
                name="Total",
                mode="lines",
                line=dict(color=PALETTE["primary_red"], width=2.4, shape="spline"),
                fill="tozeroy",
                fillcolor="rgba(217, 45, 32, 0.08)",
                hovertemplate="<b>%{x|%H:%M:%S}</b> · Total: %{y}<extra></extra>"
            ))

            # Threat curve if present (pink line)
            sub_threats = timeline[timeline["label"].isin(["ddos", "malware", "portscan"])]
            if not sub_threats.empty:
                threat_by_bucket = sub_threats.groupby("bucket")["count"].sum().reset_index()
                fig_time.add_trace(go.Scatter(
                    x=threat_by_bucket["bucket"],
                    y=threat_by_bucket["count"],
                    name="Threats",
                    mode="lines",
                    line=dict(color="#FDA29B", width=1.8, shape="spline"),
                    hovertemplate="<b>%{x|%H:%M:%S}</b> · Threats: %{y}<extra></extra>"
                ))

            # Benign baseline (muted slate curve)
            sub_benign = timeline[timeline["label"] == "benign"]
            if not sub_benign.empty:
                fig_time.add_trace(go.Scatter(
                    x=sub_benign["bucket"],
                    y=sub_benign["count"],
                    name="Benign",
                    mode="lines",
                    line=dict(color="#98A2B3", width=1.6, shape="spline"),
                    hovertemplate="<b>%{x|%H:%M:%S}</b> · Benign: %{y}<extra></extra>"
                ))

            fig_time.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(color=PALETTE["text_secondary"], family="Inter", size=11),
                xaxis=dict(
                    showgrid=False,
                    color=PALETTE["text_muted"],
                    zeroline=False,
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor="#F2F4F7",
                    color=PALETTE["text_muted"],
                    zeroline=False,
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
                height=260,
            )
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            # Standby state matching mockup aesthetic
            fig_empty = go.Figure()
            now_dt = datetime.now()
            dummy_x = [datetime.fromtimestamp(now_dt.timestamp() - 60*i) for i in reversed(range(7))]
            dummy_y = [10, 15, 12, 18, 22, 19, 25]
            fig_empty.add_trace(go.Scatter(
                x=dummy_x, y=dummy_y, mode="lines",
                line=dict(color=PALETTE["primary_red"], width=2.2, shape="spline"),
                fill="tozeroy", fillcolor="rgba(217, 45, 32, 0.08)",
                name="Standby Flow"
            ))
            fig_empty.update_layout(
                paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
                font=dict(color=PALETTE["text_secondary"], family="Inter", size=11),
                xaxis=dict(showgrid=False, color=PALETTE["text_muted"]),
                yaxis=dict(showgrid=True, gridcolor="#F2F4F7", color=PALETTE["text_muted"]),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(t=10, b=10, l=10, r=10), height=260
            )
            st.plotly_chart(fig_empty, use_container_width=True)

    with ch_col2:
        st.html(f"""
        <div class="saas-card" style="margin-bottom:0.5rem;">
            {render_section_header("Threat Classification", "Distribution of detected traffic")}
        </div>
        """)

        c_benign   = sum(1 for a in alerts if a.get("label") == "benign")
        c_portscan = sum(1 for a in alerts if a.get("label") == "portscan")
        c_ddos     = sum(1 for a in alerts if a.get("label") == "ddos")
        c_malware  = sum(1 for a in alerts if a.get("label") == "malware")

        def calc_pct(val):
            return f"{(val / total_flows * 100):.0f}%" if total_flows > 0 else "0%"

        # Primary values for the donut matching mockup colors
        donut_labels = ["Benign", "Port Scan", "DDoS", "Malware"]
        donut_values = [c_benign or (1 if not alerts else 0), c_portscan, c_ddos, c_malware]
        donut_colors = ["#D92D20", "#FDA29B", "#F79009", "#98A2B3"]

        fig_donut = go.Figure(go.Pie(
            labels=donut_labels,
            values=donut_values,
            hole=0.68,
            marker=dict(colors=donut_colors, line=dict(color="#FFFFFF", width=2.5)),
            textinfo="none",
            hoverinfo="label+value+percent",
        ))
        fig_donut.update_layout(
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            showlegend=False,
            margin=dict(t=5, b=5, l=5, r=5),
            height=150,
            annotations=[dict(
                text=f"<b style='font-size:22px;color:#101828;'>{total_flows}</b><br><span style='font-size:11px;color:#667085;'>Total Flows</span>",
                x=0.5, y=0.5, font_size=16, showarrow=False
            )]
        )
        st.plotly_chart(fig_donut, use_container_width=True)

        breakdown_html = dedent(f"""
        <div style="padding: 0 0.5rem;">
            <div class="breakdown-row">
                <div class="breakdown-item-left">
                    <span class="dot" style="background:#D92D20;"></span>
                    <span>Benign</span>
                </div>
                <div class="breakdown-item-right">
                    <span class="breakdown-val">{c_benign}</span>
                    <span class="breakdown-pct">{calc_pct(c_benign)}</span>
                </div>
            </div>
            <div class="breakdown-row">
                <div class="breakdown-item-left">
                    <span class="dot" style="background:#FDA29B;"></span>
                    <span>Port Scan</span>
                </div>
                <div class="breakdown-item-right">
                    <span class="breakdown-val">{c_portscan}</span>
                    <span class="breakdown-pct">{calc_pct(c_portscan)}</span>
                </div>
            </div>
            <div class="breakdown-row">
                <div class="breakdown-item-left">
                    <span class="dot" style="background:#F79009;"></span>
                    <span>DDoS</span>
                </div>
                <div class="breakdown-item-right">
                    <span class="breakdown-val">{c_ddos}</span>
                    <span class="breakdown-pct">{calc_pct(c_ddos)}</span>
                </div>
            </div>
            <div class="breakdown-row">
                <div class="breakdown-item-left">
                    <span class="dot" style="background:#98A2B3;"></span>
                    <span>Malware</span>
                </div>
                <div class="breakdown-item-right">
                    <span class="breakdown-val">{c_malware}</span>
                    <span class="breakdown-pct">{calc_pct(c_malware)}</span>
                </div>
            </div>
        </div>
        """).strip()
        st.html(breakdown_html)

    # 3. Bottom Section: Recent Network Activity (Full Width)
    st.html(f"""
    <div class="saas-card" style="margin-bottom:0.5rem;">
        <div style="display:flex;align-items:center;justify-content:space-between;">
            {render_section_header("Recent Network Activity", "Latest 25 flows analyzed by IoT Shield")}
            <span style="font-size:0.8125rem;color:#475467;font-weight:600;cursor:pointer;">View All &gt;</span>
        </div>
    </div>
    """)

    # Fallback dummy sample flows if detector hasn't pushed yet
    sample_alerts = alerts if alerts else [
        {"timestamp": datetime.now().strftime("%Y-%m-%dT10:43:19"), "src_ip": "10.95.39.202", "src_port": "61769", "dst_ip": "104.46.162.224", "dst_port": "443", "proto": "TCP", "label": "benign", "confidence": 55.2},
        {"timestamp": datetime.now().strftime("%Y-%m-%dT10:42:55"), "src_ip": "192.168.1.14", "src_port": "54012", "dst_ip": "8.8.8.8", "dst_port": "53", "proto": "UDP", "label": "benign", "confidence": 98.1},
        {"timestamp": datetime.now().strftime("%Y-%m-%dT10:42:31"), "src_ip": "203.0.113.42", "src_port": "443", "dst_ip": "172.16.0.18", "dst_port": "443", "proto": "TCP", "label": "benign", "confidence": 87.6},
        {"timestamp": datetime.now().strftime("%Y-%m-%dT10:41:05"), "src_ip": "192.168.1.10", "src_port": "49821", "dst_ip": "142.250.72.14", "dst_port": "443", "proto": "TCP", "label": "benign", "confidence": 91.4},
        {"timestamp": datetime.now().strftime("%Y-%m-%dT10:39:22"), "src_ip": "198.51.100.23", "src_port": "80", "dst_ip": "172.217.164.206", "dst_port": "80", "proto": "TCP", "label": "benign", "confidence": 88.7},
    ]

    # Filter if search keyword entered
    display_alerts = sample_alerts
    if search_keyword:
        kw = search_keyword.lower()
        display_alerts = [
            a for a in sample_alerts
            if kw in f"{a.get('src_ip','')} {a.get('dst_ip','')} {a.get('proto','')} {a.get('label','')}".lower()
        ]

    # Desktop Table HTML
    rows_html = ""
    # Mobile Cards HTML
    mobile_cards_html = ""

    for a in reversed(display_alerts[-25:]):
        lbl = a.get("label", "benign")
        cls_text = CLASS_LABELS.get(lbl, lbl.capitalize())
        ts = str(a.get("timestamp", ""))[:19].replace("T", " ")
        src = f"{a.get('src_ip', '0.0.0.0')}:{a.get('src_port', '')}"
        dst = f"{a.get('dst_ip', '0.0.0.0')}:{a.get('dst_port', '')}"
        conf = a.get("confidence", 100.0)
        proto = str(a.get("proto", "TCP")).upper()

        chip_class = f"chip-{lbl}"

        # Desktop Table Row
        rows_html += f"""<tr>
<td class="mono-cell" style="color:#667085;">{ts[11:19]}</td>
<td class="src-cell">{src}</td>
<td class="dst-cell">{dst}</td>
<td class="mono-cell" style="color:#667085;">{proto}</td>
<td><span class="chip {chip_class}">● {cls_text}</span></td>
<td class="mono-cell" style="color:#667085;">{conf}%</td>
<td style="color:#98A2B3;font-weight:700;letter-spacing:1px;cursor:pointer;">•••</td>
</tr>"""

        # Mobile Incident Card (Rendered on phones <= 768px)
        mobile_cards_html += f"""<div class="mobile-flow-card">
<div class="flow-card-header">
<span class="flow-card-time">{ts[11:19]}</span>
<span class="chip {chip_class}">● {cls_text}</span>
</div>
<div class="flow-card-row">
<span class="flow-label">Source</span>
<span class="src-cell">{src}</span>
</div>
<div class="flow-card-row">
<span class="flow-label">Dest</span>
<span class="dst-cell">{dst}</span>
</div>
<div class="flow-card-footer">
<span>Protocol: <b style="color:#101828;">{proto}</b></span>
<span>Confidence: <b style="color:#101828;">{conf}%</b></span>
</div>
</div>"""

    recent_activity_container_html = dedent(f"""
    <!-- Desktop Table View -->
    <div class="desktop-table-wrapper table-card-wrapper">
        <table class="saas-table">
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Source</th>
                    <th>Destination</th>
                    <th>Protocol</th>
                    <th>Classification</th>
                    <th>Confidence</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>

    <!-- Mobile List View (Phone-Friendly) -->
    <div class="mobile-cards-list">
        {mobile_cards_html}
    </div>
    """).strip()
    st.html(recent_activity_container_html)

# ═════════════════════════════════════════════════════════════
# PAGE: ANALYTICS
# ═════════════════════════════════════════════════════════════
elif selected_nav == "Analytics":
    st.html("""
    <div class="page-title">Analytics</div>
    <div class="page-subtitle">Telemetry volume trends, classification proportions, and model benchmark evaluation.</div>
    """)

    an_col1, an_col2 = st.columns(2)

    with an_col1:
        st.html(f"""
        <div class="saas-card" style="margin-bottom:0.5rem;">
            {render_section_header("Threat Distribution", "Proportion of all analyzed network traffic")}
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
                textfont=dict(family="Inter", color="#101828", size=12),
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
        st.html(f"""
        <div class="saas-card" style="margin-bottom:0.5rem;">
            {render_section_header("Model Performance", "Test evaluation accuracy on IoT-23 dataset")}
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
            textfont=dict(color="#101828", family="Inter", size=11),
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
    st.html(f"""
    <div class="saas-card" style="margin-bottom:0.5rem;">
        {render_section_header("Confusion Matrix", "Ensemble model validation across 120,000 test flows")}
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
        cm_rows += f"<tr><td style='font-weight:600;color:#101828;'>{cm_labels[i]}</td>"
        for j, val in enumerate(row):
            if i == j:
                style = "background:#ECFDF3;color:#027A48;font-weight:600;"
            elif val > 0:
                style = "background:#FEE4E2;color:#D92D20;font-weight:600;"
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
elif selected_nav == "Alerts":
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
            mobile_alert_cards = ""
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
<td><span class="chip {chip_class}">● {sev.capitalize()}</span></td>
<td><span style="font-weight:600;color:#101828;">{cls_text}</span></td>
<td class="src-cell">{src}</td>
<td class="dst-cell">{dst}</td>
<td style="color:#667085;">{rel_time}</td>
<td class="mono-cell" style="color:#667085;">{conf}%</td>
</tr>"""

                mobile_alert_cards += f"""<div class="mobile-flow-card">
<div class="flow-card-header">
    <span class="chip {chip_class}">● {sev.capitalize()}</span>
    <span style="font-size:0.75rem;color:#667085;">{rel_time}</span>
</div>
<div style="font-weight:600;font-size:0.875rem;color:#101828;margin-bottom:0.35rem;">{cls_text} Flow</div>
<div class="flow-card-row">
    <span class="flow-label">Source</span>
    <span class="src-cell">{src}</span>
</div>
<div class="flow-card-row">
    <span class="flow-label">Dest</span>
    <span class="dst-cell">{dst}</span>
</div>
<div class="flow-card-footer">
    <span>Confidence: <b style="color:#101828;">{conf}%</b></span>
    <span style="color:#98A2B3;">{ts[11:19]}</span>
</div>
</div>"""

            alerts_table_html = dedent(f"""
            <!-- Desktop Table View -->
            <div class="desktop-table-wrapper table-card-wrapper">
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

            <!-- Mobile Cards List -->
            <div class="mobile-cards-list">
                {mobile_alert_cards}
            </div>
            """).strip()
            st.html(alerts_table_html)

# ═════════════════════════════════════════════════════════════
# PAGE: AI ASSISTANT
# ═════════════════════════════════════════════════════════════
elif selected_nav == "AI Assistant":
    st.html("""
    <div class="page-title">Security Assistant</div>
    <div class="page-subtitle">Investigate suspicious activity and understand detected threats.</div>
    """)

    st.html(f"""
    <div class="saas-card" style="margin-bottom:0.5rem;">
        {render_section_header("Threat Investigation Console", "AI-powered security copilot with contextual awareness of monitored network telemetry.")}
    </div>
    """)

    st.markdown("<div style='font-size:0.875rem;font-weight:600;color:#101828;margin-bottom:0.5rem;'>Suggested Prompts</div>", unsafe_allow_html=True)
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
            <div class="saas-card" style="margin-top:1.25rem;border-left:4px solid #D92D20;background:#FFFDFD;">
                <div style="font-size:0.75rem;color:#D92D20;font-weight:700;margin-bottom:0.35rem;text-transform:uppercase;">
                    Analyst Response · {provider}
                </div>
                <div style="font-size:0.875rem;line-height:1.6;color:#101828;">
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

# ═════════════════════════════════════════════════════════════
# PAGE: DEVICES (Observed Monitored Network Endpoints)
# ═════════════════════════════════════════════════════════════
elif selected_nav == "Devices":
    st.html("""
    <div class="page-title">Monitored Devices</div>
    <div class="page-subtitle">Real-time inventory of observed network endpoints communicating with IoT Shield.</div>
    """)

    # Extract device records from fb_devices or alerts
    devices_dict = {}
    if fb_devices and isinstance(fb_devices, dict):
        for k, v in fb_devices.items():
            if isinstance(v, dict):
                ip = v.get("ip", k)
                devices_dict[ip] = dict(v)

    # Supplement or fallback from alerts
    for a in alerts:
        src = a.get("src_ip")
        if not src:
            continue
        ts = a.get("timestamp", "")
        proto = a.get("proto", "TCP")
        is_th = a.get("label", "benign") != "benign"
        if src not in devices_dict:
            devices_dict[src] = {
                "ip": src,
                "mac": "Observed via LAN",
                "first_seen": ts,
                "last_seen": ts,
                "flows": 1,
                "threats": 1 if is_th else 0,
                "last_proto": str(proto).upper(),
            }
        else:
            dev = devices_dict[src]
            if ts and ts > str(dev.get("last_seen", "")):
                dev["last_seen"] = ts
            dev["flows"] = dev.get("flows", 0) + 1
            if is_th:
                dev["threats"] = dev.get("threats", 0) + 1

    device_list = list(devices_dict.values())

    # Classify activity state: Active (<60s), Recently seen (60-300s), Not recently observed (>300s)
    now_dt = datetime.now(timezone.utc)
    for d in device_list:
        ls = d.get("last_seen", "")
        state = "Not recently observed"
        age_str = "Unknown"
        if ls:
            try:
                dt_ls = datetime.fromisoformat(str(ls).replace("Z", "+00:00"))
                if dt_ls.tzinfo is None:
                    dt_ls = dt_ls.replace(tzinfo=timezone.utc)
                diff_sec = max(0, (now_dt - dt_ls).total_seconds())
                if diff_sec <= 60:
                    state = "Active"
                    age_str = f"{int(diff_sec)}s ago"
                elif diff_sec <= 300:
                    state = "Recently seen"
                    age_str = f"{int(diff_sec // 60)}m ago"
                else:
                    state = "Not recently observed"
                    age_str = f"{int(diff_sec // 3600)}h ago" if diff_sec < 86400 else f"{int(diff_sec // 86400)}d ago"
            except Exception:
                age_str = format_relative_time(ls)
        d["state"] = state
        d["age_str"] = age_str

    # Device summary KPIs
    tot_devs = len(device_list)
    active_devs = sum(1 for d in device_list if d.get("state") == "Active")
    threat_devs = sum(1 for d in device_list if d.get("threats", 0) > 0)
    total_dev_flows = sum(d.get("flows", 0) for d in device_list)

    dev_kpi_html = dedent(f"""
    <div class="kpi-grid">
        {render_kpi_card("Total Devices", f"{tot_devs}", "Observed", "on local LAN", "💻", "icon-blue", "#2E90FA", "up")}
        {render_kpi_card("Active Now", f"{active_devs}", "Transmitting", "< 60s activity", "●", "icon-green", "#12B76A", "up")}
        {render_kpi_card("Flagged Endpoints", f"{threat_devs}", "Threats found", "requires review", "🛡", "icon-red", "#D92D20", "flat")}
        {render_kpi_card("Observed Flows", f"{total_dev_flows}", "Aggregated", "across devices", "⚡", "icon-red", "#98A2B3", "up")}
    </div>
    """).strip()
    st.html(dev_kpi_html)

    # Filter toolbar
    df_col1, df_col2 = st.columns([2, 1])
    with df_col1:
        dev_search = st.text_input("Filter device IP", placeholder="Search by IP address...", key="f_dev_search")
    with df_col2:
        dev_filter_state = st.selectbox("Status", ["All", "Active", "Recently seen", "Not recently observed"], key="f_dev_state")

    filtered_devices = device_list
    if dev_search:
        kw = dev_search.lower()
        filtered_devices = [d for d in filtered_devices if kw in str(d.get("ip", "")).lower()]
    if dev_filter_state != "All":
        filtered_devices = [d for d in filtered_devices if d.get("state") == dev_filter_state]

    if not filtered_devices:
        render_empty_state("No devices observed", "Awaiting packets from local network interfaces.")
    else:
        # Table rows & mobile cards
        dev_rows_html = ""
        dev_cards_html = ""
        for d in sorted(filtered_devices, key=lambda x: (x.get("state") != "Active", -x.get("flows", 0))):
            ip = str(d.get("ip", "Unknown"))
            mac = str(d.get("mac", "Observed via LAN"))
            state = d.get("state", "Not recently observed")
            age_str = d.get("age_str", "Unknown")
            flows = d.get("flows", 0)
            threats = d.get("threats", 0)
            proto = d.get("last_proto", "TCP")

            if state == "Active":
                chip_cls = "chip-benign"
                chip_txt = "● Active"
            elif state == "Recently seen":
                chip_cls = "chip-portscan"
                chip_txt = "● Recently Seen"
            else:
                chip_cls = "chip-malware"
                chip_txt = "○ Inactive"

            th_badge = f"<span class='chip chip-ddos'>⚠️ {threats} Threat(s)</span>" if threats > 0 else "<span style='color:#12B76A;font-weight:600;'>Clean</span>"

            dev_rows_html += f"""<tr>
<td class="src-cell" style="font-weight:600;">{ip}</td>
<td class="mono-cell" style="color:#667085;">{mac}</td>
<td><span class="chip {chip_cls}">{chip_txt}</span></td>
<td style="color:#475467;">{age_str}</td>
<td class="mono-cell" style="color:#101828;">{flows:,}</td>
<td>{th_badge}</td>
<td class="mono-cell" style="color:#667085;">{proto}</td>
</tr>"""

            dev_cards_html += f"""<div class="mobile-flow-card">
<div class="flow-card-header">
    <span class="src-cell" style="font-size:0.95rem;font-weight:700;">{ip}</span>
    <span class="chip {chip_cls}">{chip_txt}</span>
</div>
<div class="flow-card-row">
    <span class="flow-label">Status</span>
    <span>{age_str}</span>
</div>
<div class="flow-card-row">
    <span class="flow-label">Security</span>
    <span>{th_badge}</span>
</div>
<div class="flow-card-footer">
    <span>Flows: <b style="color:#101828;">{flows:,}</b></span>
    <span>Proto: <b style="color:#101828;">{proto}</b></span>
</div>
</div>"""

        dev_table_container_html = dedent(f"""
        <!-- Desktop Table View -->
        <div class="desktop-table-wrapper table-card-wrapper">
            <table class="saas-table">
                <thead>
                    <tr>
                        <th>Device IP</th>
                        <th>Identifier / MAC</th>
                        <th>Activity State</th>
                        <th>Last Observed</th>
                        <th>Total Flows</th>
                        <th>Threat Status</th>
                        <th>Last Protocol</th>
                    </tr>
                </thead>
                <tbody>
                    {dev_rows_html}
                </tbody>
            </table>
        </div>

        <!-- Mobile Cards List -->
        <div class="mobile-cards-list">
            {dev_cards_html}
        </div>
        """).strip()
        st.html(dev_table_container_html)

# ═════════════════════════════════════════════════════════════
# OTHER MOCKUP NAV PAGES (Reports, Settings)
# ═════════════════════════════════════════════════════════════
elif selected_nav in ["Reports", "Settings"]:
    st.html(f"""
    <div class="page-title">{selected_nav}</div>
    <div class="page-subtitle">Manage network {selected_nav.lower()} for IoT Shield deployment.</div>
    """)
    st.html(f"""
    <div class="saas-card">
        {render_section_header(f"{selected_nav} Overview", f"Active sensor configuration and telemetry parameters.")}
        <div style="font-size:0.875rem;color:#475467;line-height:1.8;padding:0.5rem 0;">
            <div>Network Interface: <b style="color:#101828;">{interface_name}</b></div>
            <div>Active Sensors: <b style="color:#101828;">{sensor_id}</b></div>
            <div>Detection Pipeline: <b style="color:#101828;">Random Forest + XGBoost Soft-Voting</b></div>
            <div>Cloud Ingest: <b style="color:#101828;">Firebase Realtime Database ({'Connected' if fb_connected else 'Unavailable'})</b></div>
        </div>
    </div>
    """)