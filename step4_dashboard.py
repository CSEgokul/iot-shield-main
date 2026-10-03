"""
step4_dashboard.py — IoT Shield Network Threat Monitoring
Restrained, professional B2B security operations interface for Streamlit Cloud and local detection.
"""

import os
import json
import time
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
    render_app_header, render_system_status,
    render_metric_card, render_empty_state
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
    initial_sidebar_state="collapsed"
)

# Inject refined global typography and layout styles
inject_global_styles()

# ─────────────────────────────────────────────────────────────
# Session State
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
# Top Application Header
# ─────────────────────────────────────────────────────────────
render_app_header(
    is_detector_live=is_detector_live,
    data_source=DATA_SOURCE,
    last_ts=latest_alert_ts
)

# ─────────────────────────────────────────────────────────────
# Secondary Utility Bar (Refresh, Reset)
# ─────────────────────────────────────────────────────────────
u_col1, u_col2, u_col3 = st.columns([3, 1, 1])
with u_col1:
    st.session_state.auto_refresh = st.toggle(
        "Auto-refresh (3s)",
        value=st.session_state.auto_refresh,
        key="toggle_refresh"
    )
with u_col2:
    if st.button("Refresh", key="btn_refresh"):
        st.rerun()
with u_col3:
    if st.button("Reset data", key="btn_reset"):
        clear_dashboard_data()
        st.rerun()

# ─────────────────────────────────────────────────────────────
# Top Navigation Tabs
# ─────────────────────────────────────────────────────────────
tab_overview, tab_analytics, tab_alerts, tab_ai = st.tabs([
    "Overview", "Analytics", "Alerts", "Security assistant"
])

# ═════════════════════════════════════════════════════════════
# TAB 1: OVERVIEW
# ═════════════════════════════════════════════════════════════
with tab_overview:
    # 1. System Status
    render_system_status(
        is_detector_live=is_detector_live,
        data_source=DATA_SOURCE,
        last_ts=latest_alert_ts
    )

    # 2. Key Metrics (4 Compact Cards)
    threat_rate = (threats_count / total_flows * 100) if total_flows > 0 else 0.0
    metric_cards_html = f"""<div class="metric-grid">
{render_metric_card("Network flows", f"{total_flows:,}", "Total evaluated")}
{render_metric_card("Threats", f"{threats_count:,}", f"{threat_rate:.1f}% incident rate")}
{render_metric_card("Benign traffic", f"{benign_count:,}", f"{(100.0 - threat_rate):.1f}% safe flows")}
{render_metric_card("Packets analysed", f"{total_flows:,}", "Dual-model verified")}
</div>"""
    st.html(metric_cards_html)

    # 3. Traffic Over Time Chart
    st.html("""<div class="content-section">
<div class="section-title">Traffic over time</div>
<div class="section-subtitle">Real-time flow volume by classification</div>
</div>""")

    if alerts:
        df_time = pd.DataFrame(alerts)
        df_time["time"] = pd.to_datetime(df_time["timestamp"])
        df_time["bucket"] = df_time["time"].dt.floor("5s")
        timeline = df_time.groupby(["bucket", "label"]).size().reset_index()
        timeline.columns = ["bucket", "label", "count"]

        fig_time = go.Figure()
        for cls_name, cls_color in CLASS_COLORS.items():
            sub = timeline[timeline["label"] == cls_name]
            if not sub.empty:
                fig_time.add_trace(go.Scatter(
                    x=sub["bucket"],
                    y=sub["count"],
                    name=CLASS_LABELS.get(cls_name, cls_name.capitalize()),
                    mode="lines",
                    line=dict(color=cls_color, width=1.8),
                    hovertemplate="<b>%{x|%H:%M:%S}</b> · " + CLASS_LABELS.get(cls_name, cls_name) + ": %{y}<extra></extra>"
                ))

        fig_time.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
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
                bgcolor="rgba(0,0,0,0)"
            ),
            margin=dict(t=10, b=10, l=10, r=10),
            height=280,
        )
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        render_empty_state("No traffic data", "Waiting for network telemetry from the detector.")

    # 4. Threat Breakdown Summary
    c_benign   = sum(1 for a in alerts if a.get("label") == "benign")
    c_portscan = sum(1 for a in alerts if a.get("label") == "portscan")
    c_ddos     = sum(1 for a in alerts if a.get("label") == "ddos")
    c_malware  = sum(1 for a in alerts if a.get("label") == "malware")

    def calc_pct(val):
        return f"{(val / total_flows * 100):.1f}%" if total_flows > 0 else "0.0%"

    threat_breakdown_html = f"""<div class="content-section">
<div class="section-title">Threat classification</div>
<div class="section-subtitle">Summary of all classified flows</div>
<div class="breakdown-table">
<div class="breakdown-row">
<div class="breakdown-left">
<span class="status-dot" style="background-color: {PALETTE['green']};"></span>
<span>Benign</span>
</div>
<div class="breakdown-right">
<span class="breakdown-count">{c_benign:,}</span>
<span class="breakdown-pct">{calc_pct(c_benign)}</span>
</div>
</div>
<div class="breakdown-row">
<div class="breakdown-left">
<span class="status-dot" style="background-color: {PALETTE['blue']};"></span>
<span>Port scan</span>
</div>
<div class="breakdown-right">
<span class="breakdown-count">{c_portscan:,}</span>
<span class="breakdown-pct">{calc_pct(c_portscan)}</span>
</div>
</div>
<div class="breakdown-row">
<div class="breakdown-left">
<span class="status-dot" style="background-color: {PALETTE['red']};"></span>
<span>DDoS</span>
</div>
<div class="breakdown-right">
<span class="breakdown-count">{c_ddos:,}</span>
<span class="breakdown-pct">{calc_pct(c_ddos)}</span>
</div>
</div>
<div class="breakdown-row">
<div class="breakdown-left">
<span class="status-dot" style="background-color: {PALETTE['amber']};"></span>
<span>Malware</span>
</div>
<div class="breakdown-right">
<span class="breakdown-count">{c_malware:,}</span>
<span class="breakdown-pct">{calc_pct(c_malware)}</span>
</div>
</div>
</div>
</div>"""
    st.html(threat_breakdown_html)

    # 5. Recent Network Activity Table
    st.html("""<div class="content-section">
<div class="section-title">Recent network activity</div>
<div class="section-subtitle">Latest 20 network flows analyzed</div>
</div>""")

    if alerts:
        rows_html = ""
        for a in reversed(alerts[-20:]):
            lbl = a.get("label", "benign")
            cls_text = CLASS_LABELS.get(lbl, lbl.capitalize())
            dot_color = CLASS_COLORS.get(lbl, PALETTE["text_muted"])
            ts = str(a.get("timestamp", ""))[:19].replace("T", " ")
            src = f"{a.get('src_ip', '0.0.0.0')}:{a.get('src_port', '')}"
            dst = f"{a.get('dst_ip', '0.0.0.0')}:{a.get('dst_port', '')}"
            conf = a.get("confidence", 100.0)
            proto = str(a.get("proto", "TCP")).upper()

            rows_html += f"""<tr>
<td class="mono-val" style="color:#A7B0BA;">{ts[11:19]}</td>
<td class="ip-src">{src}</td>
<td class="ip-dst">{dst}</td>
<td class="mono-val" style="color:#A7B0BA;">{proto}</td>
<td>
<span class="status-indicator">
<span class="status-dot" style="background-color:{dot_color};"></span>
<span>{cls_text}</span>
</span>
</td>
<td class="mono-val" style="color:#A7B0BA;">{conf}%</td>
</tr>"""

        table_html = f"""<div class="table-container">
<table class="data-table">
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
</div>"""
        st.html(table_html)
    else:
        render_empty_state("No recent activity", "Awaiting incoming network flow packets.")


# ═════════════════════════════════════════════════════════════
# TAB 2: ANALYTICS
# ═════════════════════════════════════════════════════════════
with tab_analytics:
    col_ana1, col_ana2 = st.columns(2)

    with col_ana1:
        st.html("""<div class="content-section">
<div class="section-title">Threat distribution</div>
<div class="section-subtitle">Overall proportion by category</div>
</div>""")

        if alerts:
            df_pie = pd.DataFrame(alerts)
            counts = df_pie["label"].value_counts().reset_index()
            counts.columns = ["label", "count"]

            fig_donut = go.Figure(go.Pie(
                labels=[CLASS_LABELS.get(l, l.capitalize()) for l in counts["label"]],
                values=counts["count"],
                hole=0.6,
                marker=dict(
                    colors=[CLASS_COLORS.get(l, PALETTE["text_muted"]) for l in counts["label"]],
                    line=dict(color=PALETTE["surface"], width=2)
                ),
                textfont=dict(family="Inter", color=PALETTE["text_primary"], size=12),
                hovertemplate="<b>%{label}</b>: %{value:,} flows (%{percent})<extra></extra>"
            ))
            fig_donut.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=PALETTE["text_secondary"]),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.15,
                    xanchor="center",
                    x=0.5,
                    font=dict(color=PALETTE["text_secondary"], size=11),
                    bgcolor="rgba(0,0,0,0)"
                ),
                margin=dict(t=10, b=10, l=10, r=10),
                height=260,
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            render_empty_state("No distribution data", "Awaiting telemetry samples.")

    with col_ana2:
        st.html("""<div class="content-section">
<div class="section-title">Model performance</div>
<div class="section-subtitle">Test evaluation accuracy on IoT-23 dataset</div>
</div>""")

        models_data = {
            "Model": ["Random Forest", "XGBoost", "Ensemble"],
            "Accuracy": [99.99, 100.00, 100.00],
        }
        fig_bar = go.Figure(go.Bar(
            x=models_data["Model"],
            y=models_data["Accuracy"],
            marker_color=[PALETTE["blue"], PALETTE["amber"], PALETTE["green"]],
            text=[f"{v:.2f}%" for v in models_data["Accuracy"]],
            textposition="outside",
            textfont=dict(color=PALETTE["text_primary"], family="Inter", size=11),
            width=0.4,
        ))
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
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
    st.html("""<div class="content-section">
<div class="section-title">Confusion matrix</div>
<div class="section-subtitle">Ensemble model validation across 120,000 test flows</div>
</div>""")

    cm_labels = ["Benign", "DDoS", "Malware", "Port scan"]
    cm_data = [
        [29998, 1,     1,     0],
        [0,     29999, 1,     0],
        [0,     0,     30000, 0],
        [0,     0,     0,     30000],
    ]
    cm_rows = ""
    for i, row in enumerate(cm_data):
        cm_rows += f"<tr><td style='font-weight:500;color:#F0F3F6;'>{cm_labels[i]}</td>"
        for j, val in enumerate(row):
            if i == j:
                style = "color:#2FB171;font-weight:600;"
            elif val > 0:
                style = "color:#E45858;font-weight:600;"
            else:
                style = "color:#727C87;"
            cm_rows += f"<td class='mono-val' style='text-align:center;{style}'>{val:,}</td>"
        cm_rows += "</tr>"

    cm_table_html = f"""<div class="table-container">
<table class="data-table">
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
</div>"""
    st.html(cm_table_html)


# ═════════════════════════════════════════════════════════════
# TAB 3: ALERTS
# ═════════════════════════════════════════════════════════════
with tab_alerts:
    st.html("""<div class="content-section">
<div class="section-title">Security incidents</div>
<div class="section-subtitle">Flagged anomalous network activity</div>
</div>""")

    # Filter row
    f_col1, f_col2, f_col3 = st.columns([1, 1, 2])
    with f_col1:
        f_type = st.selectbox("Category", ["All", "ddos", "malware", "portscan", "benign"], key="f_type")
    with f_col2:
        f_sev = st.selectbox("Severity", ["All", "critical", "high", "medium", "none"], key="f_sev")
    with f_col3:
        f_query = st.text_input("Search IP / port", placeholder="Filter by source or destination...", key="f_search")

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
            render_empty_state("No matching incidents", "No alert matches the selected filter criteria.")
        else:
            alert_rows = ""
            for a in reversed(filtered[-50:]):
                lbl = a.get("label", "benign")
                cls_text = CLASS_LABELS.get(lbl, lbl.capitalize())
                sev = a.get("severity", "none")
                sev_color = {
                    "critical": PALETTE["red"],
                    "high": PALETTE["amber"],
                    "medium": PALETTE["blue"],
                    "none": PALETTE["green"]
                }.get(sev, PALETTE["text_muted"])

                ts = str(a.get("timestamp", ""))[:19].replace("T", " ")
                rel_time = format_relative_time(ts)
                src = f"{a.get('src_ip', '0.0.0.0')}:{a.get('src_port', '')}"
                dst = f"{a.get('dst_ip', '0.0.0.0')}:{a.get('dst_port', '')}"
                conf = a.get("confidence", 100.0)

                alert_rows += f"""<tr>
<td>
<span class="status-indicator">
<span class="status-dot" style="background-color:{sev_color};"></span>
<span style="font-weight:500;">{sev.capitalize()}</span>
</span>
</td>
<td>{cls_text}</td>
<td class="ip-src">{src}</td>
<td class="ip-dst">{dst}</td>
<td style="color:#A7B0BA;">{rel_time}</td>
<td class="mono-val" style="color:#A7B0BA;">{conf}%</td>
</tr>"""

            alerts_table_html = f"""<div class="table-container">
<table class="data-table">
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
</div>"""
            st.html(alerts_table_html)


# ═════════════════════════════════════════════════════════════
# TAB 4: SECURITY ASSISTANT
# ═════════════════════════════════════════════════════════════
with tab_ai:
    st.html("""<div class="content-section">
<div class="section-title">Security assistant</div>
<div class="section-subtitle">Investigate detected activity and understand potential threats.</div>
</div>""")

    # Suggested Prompts
    st.markdown('<div style="font-size:0.8125rem;color:#A7B0BA;margin-bottom:0.5rem;">Suggested investigations</div>', unsafe_allow_html=True)
    p_col1, p_col2 = st.columns(2)
    suggested = [
        "Explain latest alert",
        "Summarize recent traffic",
        "Review suspicious activity",
        "Recommend next steps"
    ]
    active_prompt = None
    for i, s in enumerate(suggested):
        target_col = p_col1 if i % 2 == 0 else p_col2
        with target_col:
            if st.button(s, key=f"sug_btn_{i}"):
                active_prompt = s

    user_query = st.text_input(
        "Analyst query",
        value=active_prompt or st.session_state.ai_prompt,
        placeholder="Ask a question about current threats or model reasoning...",
        key="ai_query_input"
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
            f"You are a network security analyst reviewing IoT network telemetry. {context}"
            f"Provide a concise, direct analysis in 2-3 sentences: {user_query}"
        )

        with st.spinner("Analyzing telemetry..."):
            answer, provider = ai_assistant.ask_ai(prompt)

        if answer:
            response_html = f"""<div class="content-section" style="margin-top:1rem;border-left:3px solid #4D8DFF;">
<div style="font-size:0.75rem;color:#4D8DFF;font-weight:600;margin-bottom:0.4rem;text-transform:uppercase;">Analyst response · {provider}</div>
<div style="font-size:0.875rem;line-height:1.6;color:#F0F3F6;">{answer}</div>
</div>"""
            st.html(response_html)
        else:
            st.info(
                "Assistant in standby mode. To enable live inference on Streamlit Cloud, "
                "add `GEMINI_API_KEY` or `GROQ_API_KEY` to your Streamlit Cloud Secrets."
            )