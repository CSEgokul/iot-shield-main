"""
ui_components.py — Light SaaS UI Components for IoT Shield
Faithfully matches the approved IoT Shield mockup and provides a native mobile-first experience.
"""

from textwrap import dedent
from datetime import datetime
import streamlit as st


# ─────────────────────────────────────────────────────────────
# PALETTE DEFINITIONS (Approved Mockup: Warm Soft Red / White SaaS)
# ─────────────────────────────────────────────────────────────
PALETTE = {
    "page_bg": "#FFF8F8",
    "card_bg": "#FFFFFF",
    "sidebar_bg": "#FFFFFF",
    "primary_red": "#D92D20",
    "dark_red": "#B42318",
    "soft_red": "#FEE4E2",
    "soft_red_subtle": "#FEF3F2",
    "text_primary": "#101828",
    "text_secondary": "#475467",
    "text_muted": "#98A2B3",
    "border": "#EAECF0",
    "border_subtle": "#F2F4F7",
    "success_green": "#12B76A",
    "soft_green": "#ECFDF3",
    "info_blue": "#2E90FA",
    "soft_blue": "#EFF8FF",
    "warning_amber": "#F79009",
    "soft_amber": "#FEF0C7",
}

CLASS_COLORS = {
    "benign": PALETTE["primary_red"],   # Matches mockup donut (Benign is prominent red)
    "portscan": "#F97066",              # Light red/salmon in mockup
    "ddos": "#F79009",                  # Orange in mockup
    "malware": "#98A2B3",               # Muted slate in mockup
}

CLASS_LABELS = {
    "benign": "Benign",
    "portscan": "Port Scan",
    "ddos": "DDoS",
    "malware": "Malware",
}


def inject_global_styles():
    """Injects responsive light SaaS styling matching the approved mockup."""
    css = dedent("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── App Canvas ── */
    html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #FFF8F8 0%, #FFFFFF 40%, #F8FAFC 100%) !important;
        background-color: #FFF8F8 !important;
        color: #101828 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif !important;
        -webkit-font-smoothing: antialiased;
        overflow-x: hidden !important;
    }

    /* ── Streamlit Header / Hamburger Styling ── */
    #MainMenu, footer {
        visibility: hidden !important;
        height: 0 !important;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    /* Mobile sidebar toggle button */
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        color: #D92D20 !important;
        z-index: 9999 !important;
    }

    .block-container {
        max-width: 1400px !important;
        padding-top: 1.25rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        margin: 0 auto !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }

    /* ── Sidebar Overrides (Matches Mockup) ── */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #EAECF0 !important;
        box-shadow: 1px 0 3px rgba(16, 24, 40, 0.02) !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.25rem !important;
        padding-left: 1.25rem !important;
        padding-right: 1.25rem !important;
    }
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.35rem !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        color: #475467 !important;
        padding: 0.55rem 0.85rem !important;
        border-radius: 8px !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background-color: #FEF3F2 !important;
        color: #D92D20 !important;
    }

    /* ── Mockup Brand Logo ── */
    .mockup-brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding-bottom: 1.25rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid #EAECF0;
    }
    .mockup-brand-logo {
        width: 36px;
        height: 36px;
        background: #D92D20;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        font-size: 1.15rem;
        flex-shrink: 0;
        box-shadow: 0 2px 4px rgba(217, 45, 32, 0.2);
    }
    .mockup-brand-name {
        font-size: 1.125rem;
        font-weight: 700;
        color: #101828;
        letter-spacing: -0.02em;
        line-height: 1.15;
    }
    .mockup-brand-sub {
        font-size: 0.72rem;
        color: #667085;
        margin-top: 1px;
    }

    /* ── Mockup Sidebar Status & Profile ── */
    .sidebar-status-box {
        background: #FFFDFD;
        border: 1px solid #FEE4E2;
        border-radius: 10px;
        padding: 0.9rem 1rem;
        margin-top: 1.25rem;
        font-size: 0.8125rem;
        line-height: 1.7;
    }
    .sidebar-status-title {
        font-size: 0.75rem;
        font-weight: 600;
        color: #98A2B3;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 0.35rem;
    }
    .status-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: #475467;
    }
    .status-row-val {
        font-weight: 500;
        color: #101828;
        display: flex;
        align-items: center;
        gap: 0.35rem;
    }

    .sidebar-profile {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding-top: 1.25rem;
        margin-top: 1.25rem;
        border-top: 1px solid #EAECF0;
    }
    .profile-avatar {
        width: 36px;
        height: 36px;
        background: #EAECF0;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 700;
        color: #344054;
        flex-shrink: 0;
    }
    .profile-info {
        line-height: 1.25;
    }
    .profile-name {
        font-size: 0.8125rem;
        font-weight: 600;
        color: #101828;
    }
    .profile-role {
        font-size: 0.72rem;
        color: #667085;
    }

    /* ── Page Header & Titles ── */
    .page-title {
        font-size: 2rem;
        font-weight: 700;
        color: #101828;
        letter-spacing: -0.025em;
        line-height: 1.2;
    }
    .page-subtitle {
        font-size: 0.875rem;
        color: #475467;
        margin-top: 0.25rem;
        margin-bottom: 1.25rem;
    }

    /* ── White Cards with Red Vertical Stripe Accent ── */
    .saas-card {
        background: #FFFFFF;
        border: 1px solid #EAECF0;
        border-radius: 12px;
        padding: 1.25rem 1.4rem;
        box-shadow: 0 1px 3px rgba(16, 24, 40, 0.04);
        margin-bottom: 1.25rem;
        box-sizing: border-box;
    }
    .section-header-wrap {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin-bottom: 0.85rem;
    }
    .red-accent-bar {
        width: 3.5px;
        height: 18px;
        background: #D92D20;
        border-radius: 2px;
        flex-shrink: 0;
    }
    .saas-card-title {
        font-size: 0.9375rem;
        font-weight: 700;
        color: #101828;
        line-height: 1.2;
    }
    .saas-card-sub {
        font-size: 0.78rem;
        color: #475467;
        margin-top: 2px;
    }

    /* ── KPI Cards Grid (Matches Mockup with Mini Sparklines) ── */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 1.25rem;
        width: 100%;
        box-sizing: border-box;
    }
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #EAECF0;
        border-radius: 12px;
        padding: 1.15rem 1.25rem;
        box-shadow: 0 1px 3px rgba(16, 24, 40, 0.04);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 122px;
        box-sizing: border-box;
        position: relative;
        overflow: hidden;
    }
    .kpi-top {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.4rem;
    }
    .kpi-icon-circle {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.95rem;
        flex-shrink: 0;
    }
    .icon-red   { background: #FEE4E2; color: #D92D20; }
    .icon-green { background: #ECFDF3; color: #12B76A; }
    .icon-blue  { background: #EFF8FF; color: #2E90FA; }

    .kpi-label {
        font-size: 0.8125rem;
        font-weight: 500;
        color: #475467;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #101828;
        letter-spacing: -0.03em;
        line-height: 1.1;
        margin-bottom: 0.25rem;
        white-space: nowrap;
    }
    .kpi-bottom-row {
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        margin-top: auto;
    }
    .kpi-trend {
        font-size: 0.75rem;
        color: #12B76A;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    .kpi-trend.neutral { color: #98A2B3; }
    .kpi-trend-sub {
        font-size: 0.72rem;
        color: #667085;
        font-weight: 400;
        margin-left: 0.2rem;
    }
    .kpi-sparkline {
        width: 68px;
        height: 24px;
        flex-shrink: 0;
    }

    /* ── Mockup Donut Breakdown Summary ── */
    .breakdown-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.55rem 0;
        border-bottom: 1px solid #F2F4F7;
        font-size: 0.8125rem;
    }
    .breakdown-row:last-child {
        border-bottom: none;
    }
    .breakdown-item-left {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-weight: 500;
        color: #344054;
    }
    .breakdown-item-right {
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }
    .breakdown-val {
        font-weight: 600;
        color: #101828;
        font-family: 'JetBrains Mono', monospace;
    }
    .breakdown-pct {
        color: #475467;
        font-family: 'JetBrains Mono', monospace;
        min-width: 40px;
        text-align: right;
    }

    /* ── Desktop Table & Mobile Incident List ── */
    .table-card-wrapper {
        background: #FFFFFF;
        border: 1px solid #EAECF0;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(16, 24, 40, 0.04);
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        margin-bottom: 1.25rem;
        width: 100%;
        box-sizing: border-box;
    }
    .saas-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.8125rem;
        text-align: left;
    }
    .saas-table th {
        background-color: #F9FAFB;
        color: #475467;
        font-weight: 600;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        padding: 0.7rem 0.9rem;
        border-bottom: 1px solid #EAECF0;
        white-space: nowrap;
    }
    .saas-table td {
        padding: 0.65rem 0.9rem;
        border-bottom: 1px solid #F2F4F7;
        color: #101828;
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
        color: #101828;
        font-family: 'JetBrains Mono', monospace;
    }
    .dst-cell {
        color: #475467;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Status Badges */
    .chip {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .chip-benign {
        background: #ECFDF3;
        color: #027A48;
    }
    .chip-ddos {
        background: #FEE4E2;
        color: #D92D20;
    }
    .chip-portscan {
        background: #EFF8FF;
        color: #175CD3;
    }
    .chip-malware {
        background: #FEF0C7;
        color: #B54708;
    }

    .dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        display: inline-block;
    }

    /* ── Mobile Incident Cards (Shown on narrow viewports) ── */
    .mobile-cards-list {
        display: none;
    }
    .mobile-flow-card {
        background: #FFFFFF;
        border: 1px solid #EAECF0;
        border-radius: 10px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.65rem;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.03);
    }
    .flow-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.45rem;
    }
    .flow-card-time {
        font-size: 0.78rem;
        color: #667085;
        font-family: 'JetBrains Mono', monospace;
    }
    .flow-card-row {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.8125rem;
        font-family: 'JetBrains Mono', monospace;
        margin: 0.25rem 0;
        word-break: break-all;
    }
    .flow-label {
        font-size: 0.72rem;
        color: #98A2B3;
        text-transform: uppercase;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        width: 48px;
        flex-shrink: 0;
    }
    .flow-card-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 0.5rem;
        padding-top: 0.4rem;
        border-top: 1px solid #F2F4F7;
        font-size: 0.75rem;
        color: #667085;
    }

    /* ── Solid Red Export Button Matching Mockup ── */
    .btn-red-export {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 0.4rem;
        background: #D92D20 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        padding: 0.55rem 1.1rem !important;
        cursor: pointer !important;
        box-shadow: 0 1px 2px rgba(217, 45, 32, 0.15) !important;
        transition: background-color 0.15s ease !important;
        text-decoration: none !important;
    }
    .btn-red-export:hover {
        background: #B42318 !important;
        color: #FFFFFF !important;
    }

    /* ── Form Controls & Touch Targets ── */
    .stButton > button {
        background: #FFFFFF !important;
        color: #344054 !important;
        border: 1px solid #D0D5DD !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.8125rem !important;
        font-weight: 500 !important;
        min-height: 42px !important;
        padding: 0 1rem !important;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.05) !important;
        transition: all 0.15s ease !important;
    }
    .stButton > button:hover {
        background: #FEF3F2 !important;
        border-color: #D92D20 !important;
        color: #D92D20 !important;
    }
    .stSelectbox > div > div, .stTextInput > div > div > input {
        background: #FFFFFF !important;
        border: 1px solid #D0D5DD !important;
        border-radius: 8px !important;
        color: #101828 !important;
        font-size: 0.875rem !important;
        min-height: 42px !important;
    }
    .stSelectbox > div > div:hover, .stTextInput > div > div > input:focus {
        border-color: #D92D20 !important;
        box-shadow: 0 0 0 1px #D92D20 !important;
    }

    /* ── Empty State ── */
    .empty-box {
        text-align: center;
        padding: 3rem 1.5rem;
        background: #FFFFFF;
        border: 1px dashed #EAECF0;
        border-radius: 12px;
        margin: 1.25rem 0;
    }
    .empty-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #101828;
        margin-bottom: 0.25rem;
    }
    .empty-desc {
        font-size: 0.8125rem;
        color: #475467;
    }

    /* ── MOBILE-FIRST RESPONSIVE BREAKPOINTS ── */
    @media (max-width: 1024px) {
        .kpi-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: 14px !important;
            padding-right: 14px !important;
            padding-top: 0.85rem !important;
            max-width: 100% !important;
        }
        .page-title {
            font-size: 1.5rem;
        }
        .kpi-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: 0.75rem;
        }
        .kpi-card {
            padding: 0.95rem 1rem;
            min-height: 110px;
        }
        .kpi-value {
            font-size: 1.6rem;
        }
        .kpi-sparkline {
            display: none;
        }
        /* Switch from table to mobile cards on phone */
        .desktop-table-wrapper {
            display: none;
        }
        .mobile-cards-list {
            display: block;
        }
    }

    @media (max-width: 480px) {
        .kpi-grid {
            grid-template-columns: 1fr;
        }
        .mockup-brand-name {
            font-size: 1rem;
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
    """Renders the top branding inside the sidebar matching the mockup."""
    html = dedent("""
    <div class="mockup-brand">
        <div class="mockup-brand-logo">🛡</div>
        <div>
            <div class="mockup-brand-name">IoT Shield</div>
            <div class="mockup-brand-sub">Network Threat Intelligence</div>
        </div>
    </div>
    """).strip()
    st.html(html)


def render_sidebar_status(is_detector_live: bool, data_source: str, last_ts: str):
    """Renders the real system status card and user profile at the bottom of the sidebar."""
    det_dot = PALETTE["success_green"] if is_detector_live else PALETTE["warning_amber"]
    det_text = "Detector Online" if is_detector_live else "Detector Offline"

    fb_dot = PALETTE["success_green"] if data_source.startswith("Firebase") else PALETTE["warning_amber"]
    fb_text = "Firebase Connected" if data_source.startswith("Firebase") else "Local Cache"

    time_ago = format_relative_time(last_ts)

    html = dedent(f"""
    <div class="sidebar-status-box">
        <div style="margin-bottom:0.45rem;">
            <span class="status-row-val" style="font-size:0.8125rem;">
                <span class="dot" style="background:{fb_dot};"></span>
                {fb_text}
            </span>
            <div style="font-size:0.72rem;color:#667085;margin-left:14px;">Live sync active</div>
        </div>
        <div style="margin-bottom:0.45rem;">
            <span class="status-row-val" style="font-size:0.8125rem;">
                <span class="dot" style="background:{det_dot};"></span>
                {det_text}
            </span>
            <div style="font-size:0.72rem;color:#667085;margin-left:14px;">Last telemetry: {time_ago}</div>
        </div>
        <div class="status-row" style="margin-top:0.45rem;border-top:1px solid #FEE4E2;padding-top:0.4rem;font-size:0.75rem;">
            <span>Model:</span>
            <span style="font-weight:600;color:#101828;">RF + XGBoost</span>
        </div>
        <div class="status-row" style="font-size:0.75rem;">
            <span>Interface:</span>
            <span style="font-weight:600;color:#101828;">Wi-Fi</span>
        </div>
    </div>
    <div class="sidebar-profile">
        <div class="profile-avatar">VR</div>
        <div class="profile-info">
            <div class="profile-name">Vardhan Reddy</div>
            <div class="profile-role">Administrator</div>
        </div>
    </div>
    """).strip()
    st.html(html)


def get_sparkline_svg(color_stroke: str, curve_type: str = "up") -> str:
    """Returns a clean lightweight inline SVG sparkline matching the mockup."""
    if curve_type == "up":
        # Upward trending curve
        return f"""<svg class="kpi-sparkline" viewBox="0 0 68 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M2 20C14 18 20 14 30 15C40 16 48 8 66 3" stroke="{color_stroke}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>"""
    elif curve_type == "flat":
        # Neutral flat wave
        return f"""<svg class="kpi-sparkline" viewBox="0 0 68 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M2 13C18 12 32 14 48 13C56 12 62 13 66 13" stroke="{color_stroke}" stroke-width="2" stroke-linecap="round"/>
        </svg>"""
    else:
        # Dynamic red curve matching mockup Card 1
        return f"""<svg class="kpi-sparkline" viewBox="0 0 68 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M2 21C12 20 22 17 32 18C42 19 50 11 66 5" stroke="{color_stroke}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>"""


def render_kpi_card(label: str, value: str, trend_text: str, trend_sub: str, icon_symbol: str, icon_class: str, spark_color: str, spark_type: str = "up") -> str:
    """Renders a single clean white KPI metric card matching the approved mockup."""
    sparkline_svg = get_sparkline_svg(spark_color, spark_type)
    trend_class = "neutral" if trend_text.startswith("•") else ""
    return dedent(f"""
    <div class="kpi-card">
        <div class="kpi-top">
            <div class="kpi-icon-circle {icon_class}">{icon_symbol}</div>
            <span class="kpi-label">{label}</span>
        </div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-bottom-row">
            <div class="kpi-trend {trend_class}">
                {trend_text}
                <span class="kpi-trend-sub">{trend_sub}</span>
            </div>
            {sparkline_svg}
        </div>
    </div>
    """).strip()


def render_section_header(title: str, subtitle: str) -> str:
    """Renders a card section title with the red accent bar matching the mockup."""
    return dedent(f"""
    <div class="section-header-wrap">
        <div class="red-accent-bar"></div>
        <div>
            <div class="saas-card-title">{title}</div>
            <div class="saas-card-sub">{subtitle}</div>
        </div>
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
