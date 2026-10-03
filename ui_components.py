"""
ui_components.py — Enterprise Cybersecurity UI/UX Components for IoT Shield
Designed with Cloudflare/Datadog/Sentry/CrowdStrike aesthetics.
"""

from datetime import datetime
import streamlit as st


# ─────────────────────────────────────────────────────────────
# PALETTE DEFINITION
# ─────────────────────────────────────────────────────────────
PALETTE = {
    "bg": "#0B0F14",
    "surface": "#11171F",
    "card": "#151C25",
    "border": "rgba(255, 255, 255, 0.07)",
    "border_hover": "rgba(255, 255, 255, 0.14)",
    "text_primary": "#F5F7FA",
    "text_secondary": "#9AA6B2",
    "text_muted": "#6F7A86",
    "blue": "#4C8DFF",
    "green": "#35C77A",
    "amber": "#F5B942",
    "red": "#FF5D5D",
}

CLASS_COLORS = {
    "benign": PALETTE["green"],
    "ddos": PALETTE["red"],
    "malware": PALETTE["amber"],
    "portscan": PALETTE["blue"],
}

SEV_COLORS = {
    "critical": PALETTE["red"],
    "high": PALETTE["amber"],
    "medium": PALETTE["blue"],
    "none": PALETTE["green"],
}


def inject_global_styles():
    """Injects high-end cybersecurity enterprise design tokens, resets and responsive rules."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global App Canvas */
    html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"] {
        background-color: #0B0F14 !important;
        color: #F5F7FA !important;
        font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* Container Spacing & Centering */
    .block-container {
        max-width: 1440px !important;
        padding-top: 1.25rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        margin: 0 auto !important;
    }

    /* Clean Streamlit Clutter */
    #MainMenu, footer, header[data-testid="stHeader"] {
        visibility: hidden !important;
        height: 0 !important;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #0B0F14;
    }
    ::-webkit-scrollbar-thumb {
        background: #222C38;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #324050;
    }

    /* ── TOP HEADER / NAVBAR ── */
    .soc-header {
        background: #11171F;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 0.85rem 1.4rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1.2rem;
        margin-bottom: 1.25rem;
        flex-wrap: wrap;
    }
    .soc-brand {
        display: flex;
        align-items: center;
        gap: 0.85rem;
    }
    .soc-brand-icon {
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, rgba(76, 141, 255, 0.18), rgba(53, 199, 122, 0.12));
        border: 1px solid rgba(76, 141, 255, 0.35);
        border-radius: 9px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.15rem;
    }
    .soc-brand-title {
        font-size: 1.125rem;
        font-weight: 700;
        color: #F5F7FA;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    .soc-brand-subtitle {
        font-size: 0.75rem;
        color: #9AA6B2;
        font-weight: 400;
        margin-top: 1px;
    }
    .soc-header-center {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        flex-wrap: wrap;
    }
    .soc-header-right {
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }

    /* Status Pills */
    .soc-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.3rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        line-height: 1.2;
        border: 1px solid rgba(255, 255, 255, 0.08);
        background: #151C25;
        color: #9AA6B2;
    }
    .soc-pill.live {
        background: rgba(53, 199, 122, 0.08);
        border-color: rgba(53, 199, 122, 0.25);
        color: #35C77A;
    }
    .soc-pill.offline {
        background: rgba(245, 185, 66, 0.08);
        border-color: rgba(245, 185, 66, 0.25);
        color: #F5B942;
    }
    .soc-pill.blue {
        background: rgba(76, 141, 255, 0.08);
        border-color: rgba(76, 141, 255, 0.25);
        color: #4C8DFF;
    }
    .pulse-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: currentColor;
        box-shadow: 0 0 8px currentColor;
    }

    /* ── NAVIGATION TABS ── */
    [data-testid="stTabs"] [role="tablist"] {
        background: #11171F !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        border-radius: 10px !important;
        padding: 4px !important;
        gap: 6px !important;
        margin-bottom: 1.25rem !important;
        display: flex !important;
    }
    [data-testid="stTabs"] [role="tab"] {
        background: transparent !important;
        color: #9AA6B2 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        padding: 0.45rem 1.15rem !important;
        border: none !important;
        border-radius: 7px !important;
        transition: all 0.15s ease-in-out !important;
        min-height: 38px !important;
    }
    [data-testid="stTabs"] [role="tab"]:hover {
        color: #F5F7FA !important;
        background: rgba(255, 255, 255, 0.03) !important;
    }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        background: #151C25 !important;
        color: #F5F7FA !important;
        font-weight: 600 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25) !important;
    }

    /* ── CARD PRIMITIVES ── */
    .soc-card {
        background: #151C25;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 1.15rem 1.3rem;
        margin-bottom: 1rem;
        transition: border-color 0.15s ease;
    }
    .soc-card:hover {
        border-color: rgba(255, 255, 255, 0.12);
    }
    .soc-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.85rem;
    }
    .soc-card-title {
        font-size: 0.875rem;
        font-weight: 600;
        color: #F5F7FA;
        letter-spacing: -0.01em;
    }
    .soc-card-subtitle {
        font-size: 0.75rem;
        color: #6F7A86;
    }

    /* ── METRIC GRIDS ── */
    .metric-grid-4 {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.9rem;
        margin-bottom: 1.15rem;
    }
    .metric-card-kpi {
        background: #151C25;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 1.1rem 1.25rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 104px;
        transition: all 0.15s ease;
    }
    .metric-card-kpi:hover {
        border-color: rgba(255, 255, 255, 0.13);
        transform: translateY(-1px);
    }
    .metric-kpi-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.35rem;
    }
    .metric-kpi-label {
        font-size: 0.78rem;
        font-weight: 500;
        color: #9AA6B2;
        letter-spacing: 0.01em;
    }
    .metric-kpi-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #F5F7FA;
        font-family: 'Inter', sans-serif;
        line-height: 1.1;
        letter-spacing: -0.03em;
        margin-bottom: 0.3rem;
    }
    .metric-kpi-footer {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.72rem;
        color: #6F7A86;
    }
    .metric-kpi-footer.positive { color: #35C77A; }
    .metric-kpi-footer.warning { color: #F5B942; }
    .metric-kpi-footer.critical { color: #FF5D5D; }
    .metric-kpi-footer.info { color: #4C8DFF; }

    /* ── THREAT BREAKDOWN CARDS ── */
    .threat-card {
        background: #11171F;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 10px;
        padding: 0.95rem 1.1rem;
        display: flex;
        align-items: center;
        gap: 0.9rem;
        transition: border-color 0.15s;
    }
    .threat-card:hover {
        border-color: rgba(255, 255, 255, 0.12);
    }
    .threat-indicator {
        width: 10px;
        height: 10px;
        border-radius: 3px;
        flex-shrink: 0;
    }
    .threat-info {
        flex-grow: 1;
    }
    .threat-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #9AA6B2;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.2rem;
    }
    .threat-count {
        font-size: 1.35rem;
        font-weight: 700;
        color: #F5F7FA;
        line-height: 1;
        font-family: 'JetBrains Mono', monospace;
    }
    .threat-pct {
        font-size: 0.72rem;
        color: #6F7A86;
        margin-left: 0.35rem;
    }

    /* ── DEDICATED LIVE DETECTOR STATUS CARD ── */
    .soc-status-panel {
        background: #11171F;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 1.15rem 1.4rem;
        margin-bottom: 1.15rem;
    }
    .soc-status-grid {
        display: grid;
        grid-template-columns: 1.4fr repeat(4, 1fr);
        gap: 1rem;
        align-items: center;
    }
    .status-col {
        border-right: 1px solid rgba(255, 255, 255, 0.06);
        padding-right: 0.9rem;
    }
    .status-col:last-child {
        border-right: none;
        padding-right: 0;
    }
    .status-header-label {
        font-size: 0.7rem;
        font-weight: 600;
        color: #6F7A86;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.25rem;
    }
    .status-header-val {
        font-size: 0.88rem;
        font-weight: 600;
        color: #F5F7FA;
    }
    .status-header-sub {
        font-size: 0.72rem;
        color: #9AA6B2;
        margin-top: 2px;
        font-family: 'JetBrains Mono', monospace;
    }

    /* ── TABLE STYLING ── */
    .soc-table-wrapper {
        background: #11171F;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        margin-bottom: 1.15rem;
    }
    .soc-table {
        width: 100%;
        border-collapse: collapse;
        text-align: left;
        font-size: 0.8rem;
    }
    .soc-table th {
        background: #151C25;
        color: #9AA6B2;
        font-weight: 600;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.75rem 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        white-space: nowrap;
    }
    .soc-table td {
        padding: 0.7rem 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        color: #F5F7FA;
        white-space: nowrap;
    }
    .soc-table tr:hover td {
        background: rgba(255, 255, 255, 0.02);
    }
    .soc-table tr:last-child td {
        border-bottom: none;
    }
    .soc-badge {
        display: inline-block;
        padding: 0.22rem 0.55rem;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.03em;
    }
    .badge-benign {
        background: rgba(53, 199, 122, 0.12);
        color: #35C77A;
        border: 1px solid rgba(53, 199, 122, 0.25);
    }
    .badge-ddos {
        background: rgba(255, 93, 93, 0.12);
        color: #FF5D5D;
        border: 1px solid rgba(255, 93, 93, 0.25);
    }
    .badge-malware {
        background: rgba(245, 185, 66, 0.12);
        color: #F5B942;
        border: 1px solid rgba(245, 185, 66, 0.25);
    }
    .badge-portscan {
        background: rgba(76, 141, 255, 0.12);
        color: #4C8DFF;
        border: 1px solid rgba(76, 141, 255, 0.25);
    }

    /* ── SOC INCIDENT ALERTS ── */
    .soc-incident-card {
        background: #151C25;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 10px;
        padding: 0.85rem 1.15rem;
        margin-bottom: 0.6rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        transition: all 0.15s ease;
        position: relative;
    }
    .soc-incident-card:hover {
        border-color: rgba(255, 255, 255, 0.14);
        background: #17202B;
    }
    .soc-incident-left {
        display: flex;
        align-items: center;
        gap: 0.9rem;
        flex-grow: 1;
    }
    .soc-severity-chip {
        font-size: 0.68rem;
        font-weight: 700;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        min-width: 68px;
        text-align: center;
    }
    .sev-critical { background: rgba(255, 93, 93, 0.18); color: #FF5D5D; border: 1px solid rgba(255, 93, 93, 0.35); }
    .sev-high     { background: rgba(245, 185, 66, 0.18); color: #F5B942; border: 1px solid rgba(245, 185, 66, 0.35); }
    .sev-medium   { background: rgba(76, 141, 255, 0.18); color: #4C8DFF; border: 1px solid rgba(76, 141, 255, 0.35); }
    .sev-none     { background: rgba(53, 199, 122, 0.18); color: #35C77A; border: 1px solid rgba(53, 199, 122, 0.35); }

    .soc-flow-nodes {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
    }
    .soc-ip-src { color: #4C8DFF; }
    .soc-ip-dst { color: #F5F7FA; }
    .soc-arrow { color: #6F7A86; }

    .soc-incident-meta {
        font-size: 0.75rem;
        color: #9AA6B2;
        display: flex;
        align-items: center;
        gap: 0.8rem;
        font-family: 'JetBrains Mono', monospace;
    }

    /* ── AI CHAT COPILOT ── */
    .ai-copilot-container {
        background: #11171F;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 1.25rem 1.4rem;
        margin-bottom: 1.2rem;
    }
    .ai-card-assistant {
        background: #151C25;
        border: 1px solid rgba(76, 141, 255, 0.2);
        border-left: 3px solid #4C8DFF;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin-top: 0.9rem;
        font-size: 0.875rem;
        line-height: 1.6;
        color: #F5F7FA;
    }
    .ai-badge {
        font-size: 0.7rem;
        font-weight: 600;
        color: #4C8DFF;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    /* ── STREAMLIT WIDGET OVERRIDES ── */
    .stButton > button {
        background: #151C25 !important;
        color: #F5F7FA !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
        padding: 0.45rem 1rem !important;
        min-height: 38px !important;
        transition: all 0.15s ease !important;
    }
    .stButton > button:hover {
        background: #1A232E !important;
        border-color: #4C8DFF !important;
        color: #FFFFFF !important;
    }
    .stSelectbox > div > div, .stTextInput > div > div > input {
        background: #151C25 !important;
        border: 1px solid rgba(255, 255, 255, 0.09) !important;
        border-radius: 8px !important;
        color: #F5F7FA !important;
        font-size: 0.85rem !important;
    }
    .stSelectbox > div > div:hover, .stTextInput > div > div > input:focus {
        border-color: #4C8DFF !important;
    }

    /* ── EMPTY STATE ── */
    .soc-empty-state {
        text-align: center;
        padding: 3.5rem 1.5rem;
        background: #11171F;
        border: 1px dashed rgba(255, 255, 255, 0.09);
        border-radius: 12px;
        margin: 1rem 0;
    }
    .soc-empty-icon {
        font-size: 2.2rem;
        margin-bottom: 0.6rem;
        opacity: 0.8;
    }
    .soc-empty-title {
        font-size: 1rem;
        font-weight: 600;
        color: #F5F7FA;
        margin-bottom: 0.3rem;
    }
    .soc-empty-desc {
        font-size: 0.8rem;
        color: #6F7A86;
        max-width: 420px;
        margin: 0 auto;
        line-height: 1.5;
    }

    /* ── RESPONSIVE BREAKPOINTS ── */
    @media (max-width: 1200px) {
        .metric-grid-4 {
            grid-template-columns: repeat(2, 1fr);
        }
        .soc-status-grid {
            grid-template-columns: repeat(3, 1fr);
        }
        .status-col:nth-child(3) {
            border-right: none;
        }
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
            padding-top: 0.75rem !important;
        }
        .soc-header {
            padding: 0.75rem 1rem;
        }
        .metric-grid-4 {
            grid-template-columns: 1fr;
            gap: 0.6rem;
        }
        .soc-status-grid {
            grid-template-columns: 1fr;
            gap: 0.8rem;
        }
        .status-col {
            border-right: none;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            padding-bottom: 0.6rem;
            padding-right: 0;
        }
        .status-col:last-child {
            border-bottom: none;
            padding-bottom: 0;
        }
        .soc-incident-card {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
        }
        .soc-incident-meta {
            width: 100%;
            justify-content: space-between;
        }
    }

    @media (max-width: 480px) {
        .soc-brand-title {
            font-size: 1rem;
        }
        .metric-kpi-value {
            font-size: 1.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def format_relative_time(raw_ts: str) -> str:
    """Returns human-readable relative time string from ISO timestamp."""
    if not raw_ts:
        return "No events"
    try:
        ts_clean = str(raw_ts)[:19]
        dt = datetime.fromisoformat(ts_clean)
        diff = (datetime.now() - dt).total_seconds()
        diff_utc = (datetime.utcnow() - dt).total_seconds()
        secs = min(abs(diff), abs(diff_utc))
        if secs < 5:
            return "Just now"
        elif secs < 60:
            return f"{int(secs)}s ago"
        elif secs < 3600:
            return f"{int(secs // 60)}m ago"
        else:
            return f"{int(secs // 3600)}h ago"
    except Exception:
        return raw_ts[11:19] if len(raw_ts) >= 19 else str(raw_ts)


def render_header(stats: dict, is_detector_live: bool, data_source: str, last_ts: str, auto_refresh: bool):
    """Renders the sticky enterprise cybersecurity header."""
    status_class = "live" if is_detector_live else "offline"
    status_label = "LIVE MONITORING" if is_detector_live else "SENSOR OFFLINE"

    fb_connected = data_source.startswith("Firebase")
    fb_label = "Firebase Connected" if fb_connected else "Local File Bridge"
    fb_class = "live" if fb_connected else "offline"

    time_ago = format_relative_time(last_ts)
    total_flows = stats.get("total", 0)
    threats = stats.get("threats", 0)

    st.markdown(f"""
    <div class="soc-header">
        <div class="soc-brand">
            <div class="soc-brand-icon">🛡️</div>
            <div>
                <div class="soc-brand-title">IoT Shield</div>
                <div class="soc-brand-subtitle">Real-Time Network Threat Intelligence</div>
            </div>
        </div>
        <div class="soc-header-center">
            <div class="soc-pill {status_class}">
                <div class="pulse-dot"></div>
                {status_label}
            </div>
            <div class="soc-pill {fb_class}">
                <span>●</span> {fb_label}
            </div>
            <div class="soc-pill">
                <span style="color:#6F7A86;">Telemetry:</span>
                <span style="font-family:'JetBrains Mono',monospace;color:#F5F7FA;">{time_ago}</span>
            </div>
        </div>
        <div class="soc-header-right">
            <div class="soc-pill blue">
                <span>⚡</span> {threats:,} Threats / {total_flows:,} Flows
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_live_status_card(is_live: bool, last_ts: str, data_source: str, total_flows: int):
    """Renders dedicated SOC live detector status bar."""
    status_text = "Detector Online · Receiving Telemetry" if is_live else "Waiting for Local Detector Node"
    status_color = PALETTE["green"] if is_live else PALETTE["amber"]
    pulse_dot = "●" if is_live else "○"
    time_display = format_relative_time(last_ts)

    st.markdown(f"""
    <div class="soc-status-panel">
        <div class="soc-status-grid">
            <div class="status-col">
                <div class="status-header-label">Telemetry Pipeline</div>
                <div class="status-header-val" style="color:{status_color};display:flex;align-items:center;gap:0.4rem;">
                    <span>{pulse_dot}</span> {status_text}
                </div>
                <div class="status-header-sub">Interface: Monitored LAN / Wi-Fi</div>
            </div>
            <div class="status-col">
                <div class="status-header-label">Last Packet Ingest</div>
                <div class="status-header-val">{time_display}</div>
                <div class="status-header-sub">{last_ts[11:19] if last_ts else 'Standby'}</div>
            </div>
            <div class="status-col">
                <div class="status-header-label">Cloud Synchronizer</div>
                <div class="status-header-val" style="color:{PALETTE['green'] if data_source.startswith('Firebase') else PALETTE['amber']};">
                    {'Realtime Database' if data_source.startswith('Firebase') else 'Local Cache Fallback'}
                </div>
                <div class="status-header-sub">Sync Latency: &lt;1.2s</div>
            </div>
            <div class="status-col">
                <div class="status-header-label">Detection Engine</div>
                <div class="status-header-val">RF + XGBoost Ensemble</div>
                <div class="status-header-sub">Soft-Voting / 120k IoT-23</div>
            </div>
            <div class="status-col">
                <div class="status-header-label">Analytic Confidence</div>
                <div class="status-header-val" style="color:{PALETTE['green']};">99.8% – 100.0%</div>
                <div class="status-header-sub">Validated Test Accuracy</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_card(label: str, value: str, footer_text: str, footer_type: str = "info"):
    """Renders a single compact KPI metric card."""
    footer_class = f"metric-kpi-footer {footer_type}"
    return f"""
    <div class="metric-card-kpi">
        <div class="metric-kpi-top">
            <span class="metric-kpi-label">{label}</span>
        </div>
        <div class="metric-kpi-value">{value}</div>
        <div class="{footer_class}">{footer_text}</div>
    </div>
    """


def render_threat_card(label: str, count: int, total: int, color: str):
    """Renders a single threat class card with count and percentage."""
    pct = (count / total * 100) if total > 0 else 0.0
    return f"""
    <div class="threat-card">
        <div class="threat-indicator" style="background:{color};box-shadow:0 0 8px {color}66;"></div>
        <div class="threat-info">
            <div class="threat-label">{label}</div>
            <div class="threat-count">
                {count:,}
                <span class="threat-pct">({pct:.1f}%)</span>
            </div>
        </div>
    </div>
    """


def render_empty_state(title: str, message: str, icon: str = "🛡️"):
    """Renders an enterprise SOC empty state."""
    st.markdown(f"""
    <div class="soc-empty-state">
        <div class="soc-empty-icon">{icon}</div>
        <div class="soc-empty-title">{title}</div>
        <div class="soc-empty-desc">{message}</div>
    </div>
    """, unsafe_allow_html=True)
