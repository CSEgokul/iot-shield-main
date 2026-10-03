"""
ui_components.py — Restrained, Professional B2B Security UI Components for IoT Shield
Following design standards of Cloudflare, Vercel, Linear, and Datadog.
"""

from datetime import datetime
import streamlit as st


# ─────────────────────────────────────────────────────────────
# PALETTE DEFINITIONS (Restrained, Professional Dark Mode)
# ─────────────────────────────────────────────────────────────
PALETTE = {
    "bg": "#0D1117",
    "surface": "#12171D",
    "surface_secondary": "#171D24",
    "border": "#252C35",
    "border_subtle": "#1B222B",
    "text_primary": "#F0F3F6",
    "text_secondary": "#A7B0BA",
    "text_muted": "#727C87",
    "blue": "#4D8DFF",
    "green": "#2FB171",
    "amber": "#D9A441",
    "red": "#E45858",
}

CLASS_COLORS = {
    "benign": PALETTE["green"],
    "portscan": PALETTE["blue"],
    "ddos": PALETTE["red"],
    "malware": PALETTE["amber"],
}

CLASS_LABELS = {
    "benign": "Benign",
    "portscan": "Port scan",
    "ddos": "DDoS",
    "malware": "Malware",
}


def inject_global_styles():
    """Injects refined typography, layout, and component styles."""
    styles = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── App Canvas ── */
html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"] {
    background-color: #0D1117 !important;
    color: #F0F3F6 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

/* ── Container Layout ── */
.block-container {
    max-width: 1380px !important;
    padding-top: 1.25rem !important;
    padding-bottom: 3rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    margin: 0 auto !important;
}

/* ── Chrome Cleanup ── */
#MainMenu, footer, header[data-testid="stHeader"] {
    visibility: hidden !important;
    height: 0 !important;
}

/* ── Typography Resets ── */
h1, h2, h3, h4, p, span, div, label {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
}

/* ── Header ── */
.app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
    padding: 0 0.5rem;
    margin-bottom: 1.25rem;
    border-bottom: 1px solid #252C35;
}
.app-header-left {
    display: flex;
    flex-direction: column;
}
.app-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: #F0F3F6;
    line-height: 1.2;
    letter-spacing: -0.01em;
}
.app-subtitle {
    font-size: 0.8125rem;
    color: #A7B0BA;
    margin-top: 2px;
}
.app-header-right {
    display: flex;
    align-items: center;
    gap: 1.25rem;
    font-size: 0.8125rem;
    color: #A7B0BA;
}
.status-indicator {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
}
.status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    display: inline-block;
}

/* ── Navigation Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
    background: transparent !important;
    border-bottom: 1px solid #252C35 !important;
    gap: 1.5rem !important;
    padding: 0 !important;
    margin-bottom: 1.5rem !important;
}
[data-testid="stTabs"] [role="tab"] {
    background: transparent !important;
    color: #A7B0BA !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    padding: 0.6rem 0.1rem !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    transition: color 0.15s ease !important;
}
[data-testid="stTabs"] [role="tab"]:hover {
    color: #F0F3F6 !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #F0F3F6 !important;
    font-weight: 600 !important;
    border-bottom: 2px solid #4D8DFF !important;
}

/* ── System Status Block (Clean 2-Column Key/Value) ── */
.system-status-container {
    background: #12171D;
    border: 1px solid #252C35;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 1.25rem;
}
.system-status-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: #F0F3F6;
    margin-bottom: 0.75rem;
}
.system-status-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 1.25rem;
}
.status-item-label {
    font-size: 0.75rem;
    color: #727C87;
    margin-bottom: 0.25rem;
}
.status-item-value {
    font-size: 0.875rem;
    font-weight: 500;
    color: #F0F3F6;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

/* ── Metric Cards ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.25rem;
}
.metric-box {
    background: #12171D;
    border: 1px solid #252C35;
    border-radius: 8px;
    padding: 1rem 1.15rem;
    height: 112px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.metric-box-label {
    font-size: 0.8125rem;
    font-weight: 500;
    color: #A7B0BA;
}
.metric-box-value {
    font-size: 1.875rem;
    font-weight: 600;
    color: #F0F3F6;
    line-height: 1.1;
    letter-spacing: -0.02em;
}
.metric-box-context {
    font-size: 0.75rem;
    color: #727C87;
}

/* ── Content Sections & Cards ── */
.content-section {
    background: #12171D;
    border: 1px solid #252C35;
    border-radius: 8px;
    padding: 1.25rem;
    margin-bottom: 1.25rem;
}
.section-title {
    font-size: 0.9375rem;
    font-weight: 600;
    color: #F0F3F6;
    margin-bottom: 0.25rem;
}
.section-subtitle {
    font-size: 0.8125rem;
    color: #727C87;
    margin-bottom: 1rem;
}

/* ── Threat Breakdown Summary ── */
.breakdown-table {
    width: 100%;
    border-collapse: collapse;
}
.breakdown-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.65rem 0;
    border-bottom: 1px solid #1B222B;
    font-size: 0.875rem;
}
.breakdown-row:last-child {
    border-bottom: none;
}
.breakdown-left {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    color: #F0F3F6;
    font-weight: 500;
}
.breakdown-right {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8125rem;
}
.breakdown-count {
    color: #F0F3F6;
}
.breakdown-pct {
    color: #727C87;
    min-width: 48px;
    text-align: right;
}

/* ── Data Tables ── */
.table-container {
    width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}
.data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8125rem;
    text-align: left;
}
.data-table th {
    padding: 0.65rem 0.85rem;
    border-bottom: 1px solid #252C35;
    color: #A7B0BA;
    font-weight: 500;
    font-size: 0.75rem;
    white-space: nowrap;
}
.data-table td {
    padding: 0.65rem 0.85rem;
    border-bottom: 1px solid #1B222B;
    color: #F0F3F6;
    white-space: nowrap;
}
.data-table tr:hover td {
    background-color: #171D24;
}
.data-table tr:last-child td {
    border-bottom: none;
}
.mono-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8125rem;
}
.ip-src {
    color: #4D8DFF;
    font-family: 'JetBrains Mono', monospace;
}
.ip-dst {
    color: #F0F3F6;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Buttons & Form Controls ── */
.stButton > button {
    background: #171D24 !important;
    color: #F0F3F6 !important;
    border: 1px solid #252C35 !important;
    border-radius: 7px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8125rem !important;
    font-weight: 500 !important;
    height: 38px !important;
    padding: 0 1rem !important;
    transition: background-color 0.15s ease, border-color 0.15s ease !important;
}
.stButton > button:hover {
    background: #1E252E !important;
    border-color: #38424F !important;
    color: #FFFFFF !important;
}
.stSelectbox > div > div, .stTextInput > div > div > input {
    background: #12171D !important;
    border: 1px solid #252C35 !important;
    border-radius: 7px !important;
    color: #F0F3F6 !important;
    font-size: 0.8125rem !important;
}

/* ── Empty State ── */
.empty-notice {
    padding: 3rem 1.5rem;
    text-align: center;
    color: #A7B0BA;
}
.empty-notice-title {
    font-size: 0.9375rem;
    font-weight: 500;
    color: #F0F3F6;
    margin-bottom: 0.25rem;
}
.empty-notice-desc {
    font-size: 0.8125rem;
    color: #727C87;
}

/* ── Responsive Breakpoints ── */
@media (max-width: 1024px) {
    .system-status-grid {
        grid-template-columns: repeat(3, 1fr);
    }
    .metric-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}
@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    .app-header {
        flex-direction: column;
        align-items: flex-start;
        height: auto;
        padding-bottom: 0.75rem;
        gap: 0.5rem;
    }
    .app-header-right {
        gap: 0.85rem;
        flex-wrap: wrap;
    }
    .system-status-grid {
        grid-template-columns: 1fr 1fr;
    }
    .metric-grid {
        grid-template-columns: 1fr 1fr;
        gap: 0.75rem;
    }
}
@media (max-width: 480px) {
    .system-status-grid {
        grid-template-columns: 1fr;
    }
    .metric-grid {
        grid-template-columns: 1fr;
    }
}
</style>
    """
    st.html(styles)


def format_relative_time(raw_ts: str) -> str:
    """Calculates concise, human-readable relative time."""
    if not raw_ts:
        return "No telemetry"
    try:
        ts_clean = str(raw_ts)[:19]
        dt = datetime.fromisoformat(ts_clean)
        diff = (datetime.now() - dt).total_seconds()
        diff_utc = (datetime.utcnow() - dt).total_seconds()
        secs = min(abs(diff), abs(diff_utc))
        if secs < 10:
            return "just now"
        elif secs < 60:
            return f"{int(secs)}s ago"
        elif secs < 3600:
            return f"{int(secs // 60)}m ago"
        elif secs < 86400:
            return f"{int(secs // 3600)}h ago"
        else:
            return f"{int(secs // 86400)}d ago"
    except Exception:
        return raw_ts[11:19] if len(raw_ts) >= 19 else str(raw_ts)


def render_app_header(is_detector_live: bool, data_source: str, last_ts: str):
    """Renders the top application header."""
    detector_label = "Detector active" if is_detector_live else "Detector offline"
    detector_dot_color = PALETTE["green"] if is_detector_live else PALETTE["amber"]

    fb_connected = data_source.startswith("Firebase")
    fb_label = "Firebase connected" if fb_connected else "Local cache"
    fb_dot_color = PALETTE["green"] if fb_connected else PALETTE["amber"]

    time_ago = format_relative_time(last_ts)

    html = f"""<div class="app-header">
<div class="app-header-left">
<div class="app-title">IoT Shield</div>
<div class="app-subtitle">Network threat monitoring</div>
</div>
<div class="app-header-right">
<div class="status-indicator">
<span class="status-dot" style="background-color: {detector_dot_color};"></span>
<span>{detector_label}</span>
</div>
<div class="status-indicator">
<span class="status-dot" style="background-color: {fb_dot_color};"></span>
<span>{fb_label}</span>
</div>
<div>Last update {time_ago}</div>
</div>
</div>"""
    st.html(html)


def render_system_status(is_detector_live: bool, data_source: str, last_ts: str):
    """Renders clean 2-column/multi-column system status without unnecessary boxing."""
    detector_label = "Active" if is_detector_live else "Offline"
    detector_dot_color = PALETTE["green"] if is_detector_live else PALETTE["amber"]

    fb_connected = data_source.startswith("Firebase")
    fb_label = "Connected" if fb_connected else "Local fallback"
    fb_dot_color = PALETTE["green"] if fb_connected else PALETTE["amber"]

    time_ago = format_relative_time(last_ts)

    html = f"""<div class="system-status-container">
<div class="system-status-title">System status</div>
<div class="system-status-grid">
<div>
<div class="status-item-label">Detector</div>
<div class="status-item-value">
<span class="status-dot" style="background-color: {detector_dot_color};"></span>
<span>{detector_label}</span>
</div>
</div>
<div>
<div class="status-item-label">Firebase</div>
<div class="status-item-value">
<span class="status-dot" style="background-color: {fb_dot_color};"></span>
<span>{fb_label}</span>
</div>
</div>
<div>
<div class="status-item-label">Detection model</div>
<div class="status-item-value">Random Forest + XGBoost</div>
</div>
<div>
<div class="status-item-label">Last telemetry</div>
<div class="status-item-value">{time_ago}</div>
</div>
<div>
<div class="status-item-label">Network interface</div>
<div class="status-item-value">Monitored LAN</div>
</div>
</div>
</div>"""
    st.html(html)


def render_metric_card(label: str, value: str, context: str = ""):
    """Returns clean HTML string for a metric card."""
    return f"""<div class="metric-box">
<div class="metric-box-label">{label}</div>
<div class="metric-box-value">{value}</div>
<div class="metric-box-context">{context}</div>
</div>"""


def render_empty_state(title: str, description: str):
    """Renders an understated empty state notice."""
    html = f"""<div class="empty-notice">
<div class="empty-notice-title">{title}</div>
<div class="empty-notice-desc">{description}</div>
</div>"""
    st.html(html)
