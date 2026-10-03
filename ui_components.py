"""
ui_components.py — Light Theme B2B Security UI Components for IoT Shield
Matches the approved clean white/light red SaaS dashboard aesthetic.
"""

from textwrap import dedent
from datetime import datetime
import streamlit as st


# ─────────────────────────────────────────────────────────────
# PALETTE DEFINITIONS (Light Red / White SaaS Design)
# ─────────────────────────────────────────────────────────────
PALETTE = {
    "page_bg": "#FFF8F8",
    "bg_secondary": "#FFF5F5",
    "card_bg": "#FFFFFF",
    "sidebar_bg": "#FFFFFF",
    "primary_red": "#E31B23",
    "dark_red": "#C9141C",
    "soft_red": "#FDEBED",
    "text_primary": "#111827",
    "text_secondary": "#667085",
    "text_muted": "#98A2B3",
    "border": "#E5E7EB",
    "border_subtle": "#F3F4F6",
    "success_green": "#16A34A",
    "soft_green": "#ECFDF3",
    "info_blue": "#2563EB",
    "soft_blue": "#EFF6FF",
    "warning_amber": "#F59E0B",
    "soft_amber": "#FFF7E6",
}

CLASS_COLORS = {
    "benign": PALETTE["success_green"],
    "portscan": PALETTE["info_blue"],
    "ddos": PALETTE["primary_red"],
    "malware": PALETTE["warning_amber"],
}

CLASS_LABELS = {
    "benign": "Benign",
    "portscan": "Port scan",
    "ddos": "DDoS",
    "malware": "Malware",
}


def inject_global_styles():
    """Injects light SaaS styling, typography, cards, tables, and sidebar overrides."""
    css = dedent("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── App Canvas ── */
    html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #FFF8F8 0%, #FFFFFF 45%, #F8FAFC 100%) !important;
        background-color: #FFF8F8 !important;
        color: #111827 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }

    /* ── Streamlit Chrome Adjustments ── */
    #MainMenu, footer, header[data-testid="stHeader"] {
        visibility: hidden !important;
        height: 0 !important;
    }

    .block-container {
        max-width: 1400px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        margin: 0 auto !important;
    }

    /* ── Sidebar Overrides ── */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E5E7EB !important;
        box-shadow: 1px 0 3px rgba(0, 0, 0, 0.02) !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.25rem !important;
        padding-left: 1.25rem !important;
        padding-right: 1.25rem !important;
    }
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.25rem !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        color: #667085 !important;
        padding: 0.5rem 0.75rem !important;
        border-radius: 8px !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background-color: #FFF5F5 !important;
        color: #E31B23 !important;
    }

    /* ── Brand Logo Header ── */
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding-bottom: 1.25rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid #E5E7EB;
    }
    .brand-icon-box {
        width: 38px;
        height: 38px;
        background: #FDEBED;
        border: 1px solid #FECDCA;
        border-radius: 9px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #E31B23;
        font-weight: 700;
        font-size: 1.1rem;
        flex-shrink: 0;
    }
    .brand-name {
        font-size: 1.125rem;
        font-weight: 700;
        color: #111827;
        line-height: 1.2;
        letter-spacing: -0.02em;
    }
    .brand-sub {
        font-size: 0.75rem;
        color: #667085;
        margin-top: 1px;
    }

    /* ── Sidebar System Status Footer ── */
    .sidebar-status-box {
        background: #FFF8F8;
        border: 1px solid #FDEBED;
        border-radius: 10px;
        padding: 0.9rem 1rem;
        margin-top: 1.5rem;
        font-size: 0.8125rem;
        line-height: 1.7;
    }
    .sidebar-status-title {
        font-size: 0.75rem;
        font-weight: 600;
        color: #98A2B3;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.4rem;
    }
    .status-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: #667085;
    }
    .status-row-val {
        font-weight: 500;
        color: #111827;
        display: flex;
        align-items: center;
        gap: 0.35rem;
    }

    /* ── Typography & Page Title ── */
    .page-title {
        font-size: 2rem;
        font-weight: 700;
        color: #111827;
        letter-spacing: -0.025em;
        line-height: 1.2;
    }
    .page-subtitle {
        font-size: 0.9rem;
        color: #667085;
        margin-top: 0.25rem;
        margin-bottom: 1.5rem;
    }

    /* ── Clean White Cards ── */
    .saas-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1.25rem 1.4rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
        margin-bottom: 1.25rem;
    }
    .saas-card-title {
        font-size: 1rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 0.2rem;
    }
    .saas-card-sub {
        font-size: 0.8125rem;
        color: #667085;
        margin-bottom: 1rem;
    }

    /* ── KPI Cards Grid ── */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.15rem;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 124px;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .kpi-card:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    }
    .kpi-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.5rem;
    }
    .kpi-label {
        font-size: 0.875rem;
        font-weight: 500;
        color: #667085;
    }
    .kpi-icon-circle {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.875rem;
        flex-shrink: 0;
    }
    .icon-red   { background: #FDEBED; color: #E31B23; }
    .icon-green { background: #ECFDF3; color: #16A34A; }
    .icon-blue  { background: #EFF6FF; color: #2563EB; }
    .icon-amber { background: #FFF7E6; color: #F59E0B; }

    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #111827;
        letter-spacing: -0.025em;
        line-height: 1.1;
        margin-bottom: 0.35rem;
    }
    .kpi-footer {
        font-size: 0.78rem;
        color: #98A2B3;
    }

    /* ── Threat Breakdown Summary Table ── */
    .breakdown-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem 0;
        border-bottom: 1px solid #F3F4F6;
        font-size: 0.875rem;
    }
    .breakdown-row:last-child {
        border-bottom: none;
    }
    .breakdown-item-left {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-weight: 500;
        color: #111827;
    }
    .breakdown-item-right {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        font-size: 0.8125rem;
    }
    .breakdown-val {
        font-weight: 600;
        color: #111827;
        font-family: 'JetBrains Mono', monospace;
    }
    .breakdown-pct {
        color: #667085;
        font-family: 'JetBrains Mono', monospace;
        min-width: 44px;
        text-align: right;
    }

    /* ── Data Tables ── */
    .table-card-wrapper {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        margin-bottom: 1.5rem;
    }
    .saas-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.8125rem;
        text-align: left;
    }
    .saas-table th {
        background-color: #F9FAFB;
        color: #667085;
        font-weight: 600;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #E5E7EB;
        white-space: nowrap;
    }
    .saas-table td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #F3F4F6;
        color: #111827;
        white-space: nowrap;
    }
    .saas-table tr:hover td {
        background-color: #FFFDFD;
    }
    .saas-table tr:last-child td {
        border-bottom: none;
    }
    .mono-cell {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8125rem;
    }
    .src-cell {
        color: #2563EB;
        font-family: 'JetBrains Mono', monospace;
    }
    .dst-cell {
        color: #111827;
        font-family: 'JetBrains Mono', monospace;
    }

    /* ── Status Chips / Badges ── */
    .chip {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.22rem 0.55rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .chip-benign {
        background: #ECFDF3;
        color: #16A34A;
        border: 1px solid #D1FADF;
    }
    .chip-ddos {
        background: #FDEBED;
        color: #E31B23;
        border: 1px solid #FECDCA;
    }
    .chip-portscan {
        background: #EFF6FF;
        color: #2563EB;
        border: 1px solid #D1E9FF;
    }
    .chip-malware {
        background: #FFF7E6;
        color: #D97706;
        border: 1px solid #FEDF89;
    }

    /* ── Status Indicators ── */
    .dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        display: inline-block;
    }

    /* ── Buttons & Inputs ── */
    .stButton > button {
        background: #FFFFFF !important;
        color: #111827 !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.8125rem !important;
        font-weight: 500 !important;
        height: 38px !important;
        padding: 0 1rem !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03) !important;
        transition: all 0.15s ease !important;
    }
    .stButton > button:hover {
        background: #FFF5F5 !important;
        border-color: #E31B23 !important;
        color: #E31B23 !important;
    }
    .stSelectbox > div > div, .stTextInput > div > div > input {
        background: #FFFFFF !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 8px !important;
        color: #111827 !important;
        font-size: 0.8125rem !important;
    }
    .stSelectbox > div > div:hover, .stTextInput > div > div > input:focus {
        border-color: #E31B23 !important;
        box-shadow: 0 0 0 1px #E31B23 !important;
    }

    /* ── Empty State ── */
    .empty-box {
        text-align: center;
        padding: 3.5rem 1.5rem;
        background: #FFFFFF;
        border: 1px dashed #E5E7EB;
        border-radius: 12px;
        margin: 1.25rem 0;
    }
    .empty-title {
        font-size: 1rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 0.35rem;
    }
    .empty-desc {
        font-size: 0.8125rem;
        color: #667085;
    }

    /* ── Responsive Rules ── */
    @media (max-width: 1024px) {
        .kpi-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1rem !important;
        }
        .page-title {
            font-size: 1.5rem;
        }
        .kpi-grid {
            grid-template-columns: 1fr;
            gap: 0.85rem;
        }
    }
    </style>
    """).strip()
    st.html(css)


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


def render_sidebar_header():
    """Renders the top branding inside the sidebar."""
    html = dedent("""
    <div class="sidebar-brand">
        <div class="brand-icon-box">🛡</div>
        <div>
            <div class="brand-name">IoT Shield</div>
            <div class="brand-sub">Network Threat Intelligence</div>
        </div>
    </div>
    """).strip()
    st.html(html)


def render_sidebar_status(is_detector_live: bool, data_source: str, last_ts: str):
    """Renders the real system status card at the bottom of the sidebar."""
    det_dot = PALETTE["success_green"] if is_detector_live else PALETTE["warning_amber"]
    det_text = "Online" if is_detector_live else "Offline"

    fb_dot = PALETTE["success_green"] if data_source.startswith("Firebase") else PALETTE["warning_amber"]
    fb_text = "Connected" if data_source.startswith("Firebase") else "Local cache"

    time_ago = format_relative_time(last_ts)

    html = dedent(f"""
    <div class="sidebar-status-box">
        <div class="sidebar-status-title">System Status</div>
        <div class="status-row">
            <span>Detector</span>
            <span class="status-row-val">
                <span class="dot" style="background:{det_dot};"></span>
                {det_text}
            </span>
        </div>
        <div class="status-row">
            <span>Firebase</span>
            <span class="status-row-val">
                <span class="dot" style="background:{fb_dot};"></span>
                {fb_text}
            </span>
        </div>
        <div class="status-row">
            <span>Last telemetry</span>
            <span class="status-row-val">{time_ago}</span>
        </div>
        <div class="status-row">
            <span>Model</span>
            <span class="status-row-val">RF + XGBoost</span>
        </div>
        <div class="status-row">
            <span>Interface</span>
            <span class="status-row-val">Monitored LAN</span>
        </div>
    </div>
    """).strip()
    st.html(html)


def render_kpi_card(label: str, value: str, footer: str, icon_symbol: str, icon_class: str):
    """Renders a single clean white KPI metric card."""
    return dedent(f"""
    <div class="kpi-card">
        <div class="kpi-top">
            <span class="kpi-label">{label}</span>
            <div class="kpi-icon-circle {icon_class}">{icon_symbol}</div>
        </div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-footer">{footer}</div>
    </div>
    """).strip()


def render_empty_state(title: str, description: str):
    """Renders a clean white empty state card."""
    html = dedent(f"""
    <div class="empty-box">
        <div class="empty-title">{title}</div>
        <div class="empty-desc">{description}</div>
    </div>
    """).strip()
    st.html(html)
