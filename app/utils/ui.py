from __future__ import annotations

import html
from collections.abc import Sequence

import plotly.graph_objects as go
import streamlit as st


PALETTE = {
    "background": "#080D18",
    "surface": "#101827",
    "surface_raised": "#151F30",
    "border": "rgba(148, 163, 184, 0.16)",
    "text": "#F1F5F9",
    "muted": "#A4B1C2",
    "subtle": "#748399",
    "blue": "#5BA6F8",
    "cyan": "#55C6D9",
    "violet": "#9B8AFB",
    "green": "#42C99A",
    "amber": "#E9B45E",
    "red": "#F07878",
}

CHART_COLORS = [
    PALETTE["blue"],
    PALETTE["violet"],
    PALETTE["cyan"],
    PALETTE["green"],
    PALETTE["amber"],
    PALETTE["red"],
]
SEVERITY_COLORS = {
    "HIGH": PALETTE["red"],
    "MEDIUM": PALETTE["amber"],
    "LOW": PALETTE["green"],
}
STATUS_COLORS = {
    "OPEN": PALETTE["red"],
    "MONITOR": PALETTE["amber"],
    "REVIEWED": PALETTE["green"],
}
SLA_STATUS_COLORS = {
    "Met": PALETTE["green"],
    "At Risk": PALETTE["amber"],
    "Breached": PALETTE["red"],
}
DECISION_COLORS = {
    "AUTO_APPROVE": PALETTE["green"],
    "MANAGER_REVIEW": PALETTE["amber"],
    "DECLINE": PALETTE["red"],
}
RISK_COLORS = {
    "HIGH": PALETTE["red"],
    "MEDIUM": PALETTE["amber"],
    "LOW": PALETTE["green"],
}

_PAGES = (
    ("01", "Executive Control Tower", "pages/1_Executive_Control_Tower.py", ":material/space_dashboard:"),
    ("02", "Billing Integrity", "pages/2_Billing_Integrity.py", ":material/verified:"),
    ("03", "Exception Management", "pages/3_Exception_Management.py", ":material/inbox:"),
    ("04", "Discount Decisions", "pages/4_Discount_Decisions.py", ":material/account_balance_wallet:"),
    ("05", "SLA Operations", "pages/5_SLA_Operations.py", ":material/timer:"),
    ("06", "Customer Exposure", "pages/6_Customer_Risk.py", ":material/groups:"),
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            color-scheme: dark;
            --ba-bg: #080D18;
            --ba-surface: #101827;
            --ba-raised: #151F30;
            --ba-border: rgba(148, 163, 184, .16);
            --ba-text: #F1F5F9;
            --ba-muted: #A4B1C2;
            --ba-subtle: #748399;
            --ba-blue: #5BA6F8;
            --ba-cyan: #55C6D9;
            --ba-violet: #9B8AFB;
            --ba-green: #42C99A;
            --ba-amber: #E9B45E;
            --ba-red: #F07878;
        }
        html, body, [class*="css"] { font-family: Inter, "Segoe UI", sans-serif; }
        .stApp {
            position: relative;
            isolation: isolate;
            min-height: 100vh;
            color: var(--ba-text);
            background: linear-gradient(145deg, #070B14 0%, #050810 52%, #080B16 100%);
        }
        .stApp::before, .stApp::after {
            content: "";
            position: fixed;
            inset: -12%;
            z-index: 0;
            pointer-events: none;
        }
        .stApp::before {
            background:
                radial-gradient(ellipse at 15% 18%, rgba(20, 105, 191, .20), transparent 34%),
                radial-gradient(ellipse at 78% 24%, rgba(48, 92, 184, .17), transparent 35%),
                radial-gradient(ellipse at 68% 82%, rgba(23, 158, 185, .11), transparent 31%),
                radial-gradient(ellipse at 35% 76%, rgba(91, 68, 164, .15), transparent 36%);
            filter: blur(30px);
            opacity: .82;
            transform: translate3d(-1.5%, -1%, 0) scale(1.04);
            animation: ba-atmosphere-drift 29s ease-in-out infinite alternate;
            will-change: transform;
        }
        .stApp::after {
            inset: 0;
            background-image:
                linear-gradient(rgba(115, 163, 212, .034) 1px, transparent 1px),
                linear-gradient(90deg, rgba(115, 163, 212, .034) 1px, transparent 1px),
                radial-gradient(ellipse at 50% 38%, transparent 18%, rgba(2, 5, 12, .32) 100%);
            background-size: 44px 44px, 44px 44px, 100% 100%;
            background-position: 0 0, 0 0, center;
            opacity: .68;
            animation: ba-grid-glide 38s linear infinite;
        }
        @keyframes ba-atmosphere-drift {
            0% { transform: translate3d(-1.5%, -1%, 0) scale(1.04); }
            50% { transform: translate3d(1.2%, .8%, 0) scale(1.07); }
            100% { transform: translate3d(.3%, -1.2%, 0) scale(1.05); }
        }
        @keyframes ba-grid-glide {
            from { background-position: 0 0, 0 0, center; }
            to { background-position: 44px 22px, 44px 22px, center; }
        }
        [data-testid="stAppViewContainer"] {
            position: relative;
            z-index: 1;
            background: transparent;
        }
        [data-testid="stHeader"] { background: rgba(5, 8, 16, .28); }
        .block-container {
            position: relative;
            z-index: 1;
            max-width: 1580px;
            padding: 1.45rem clamp(1.15rem, 2.5vw, 2.7rem) 2.5rem;
            animation: ba-enter .42s ease-out both;
        }
        @keyframes ba-enter { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
        [data-testid="stSidebar"] {
            position: relative;
            z-index: 2;
            background: linear-gradient(180deg, rgba(8, 13, 23, .95), rgba(6, 10, 18, .97));
            backdrop-filter: blur(18px);
            border-right: 1px solid rgba(148, 163, 184, .12);
        }
        [data-testid="stSidebar"] > div:first-child { padding-top: .75rem; }
        [data-testid="stSidebarNav"] { display: none; }
        .ba-brand { padding: .5rem .3rem 1.1rem; border-bottom: 1px solid var(--ba-border); margin-bottom: .8rem; }
        .ba-brand-mark { color: var(--ba-cyan); font-size: .69rem; font-weight: 750; letter-spacing: .16em; text-transform: uppercase; }
        .ba-brand-title { margin-top: .34rem; color: var(--ba-text); font-size: 1rem; font-weight: 680; letter-spacing: -.025em; line-height: 1.3; }
        .ba-brand-subtitle { margin-top: .12rem; color: var(--ba-muted); font-size: .78rem; line-height: 1.45; }
        .ba-sidebar-status { display: flex; justify-content: space-between; gap: .5rem; padding: .68rem .7rem; margin: .85rem 0; background: rgba(20, 31, 47, .7); border: 1px solid var(--ba-border); border-radius: 10px; color: var(--ba-muted); font-size: .72rem; }
        .ba-sidebar-status strong { color: var(--ba-text); font-weight: 650; }
        [data-testid="stSidebar"] [data-testid="stPageLink"] a {
            position: relative;
            min-height: 2.35rem; border-radius: 9px; border: 1px solid transparent;
            color: #B8C4D3; transition: background-color .18s ease, border-color .18s ease, color .18s ease;
        }
        [data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
            background: rgba(91, 166, 248, .09); border-color: rgba(91, 166, 248, .18); color: var(--ba-text);
        }
        [data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {
            background: linear-gradient(105deg, rgba(49,117,192,.20), rgba(91,166,248,.055) 58%, rgba(89,72,155,.10));
            background-size: 180% 100%;
            border-color: rgba(91,166,248,.25);
            box-shadow: inset 2px 0 0 rgba(88,185,242,.72), 0 0 18px rgba(40,116,193,.08);
            color: #E5F1FF;
            animation: ba-nav-aura 18s ease-in-out infinite alternate;
        }
        @keyframes ba-nav-aura { to { background-position: 100% 50%; } }
        .ba-page-head { margin: .1rem 0 1.1rem; padding: .15rem 0 .95rem; border-bottom: 1px solid rgba(148, 163, 184, .12); }
        .ba-eyebrow { color: var(--ba-cyan); font-size: .68rem; font-weight: 750; letter-spacing: .16em; text-transform: uppercase; margin-bottom: .32rem; }
        .ba-page-title { color: var(--ba-text); font-size: clamp(1.55rem, 2.1vw, 2.05rem); font-weight: 720; letter-spacing: -.045em; line-height: 1.16; margin: 0; }
        .ba-page-subtitle { color: var(--ba-muted); font-size: .91rem; line-height: 1.55; margin-top: .42rem; max-width: 76ch; }
        .hero, .hero-shell {
            position: relative; overflow: hidden; isolation: isolate;
            padding: clamp(1.15rem, 2vw, 1.75rem) clamp(1.25rem, 2.5vw, 2.1rem);
            margin: .15rem 0 1rem; border-radius: 14px;
            background: linear-gradient(108deg, rgba(13, 28, 48, .84), rgba(13, 22, 38, .82) 55%, rgba(21, 23, 43, .83));
            border: 1px solid rgba(115, 175, 225, .22);
            box-shadow: inset 0 1px 0 rgba(255,255,255,.055), 0 16px 42px rgba(0,0,0,.23), 0 0 28px rgba(38,112,185,.055);
            backdrop-filter: blur(16px);
        }
        .hero::before, .hero-shell::before {
            content: "";
            position: absolute;
            z-index: 0;
            inset: 0 auto 0 -48%;
            width: 42%;
            pointer-events: none;
            background: linear-gradient(105deg, transparent, rgba(107,197,242,.075), rgba(132,153,255,.045), transparent);
            transform: skewX(-18deg);
            animation: ba-hero-sweep 22s ease-in-out infinite;
        }
        .hero::after, .hero-shell::after {
            content: ""; position: absolute; z-index: 0; right: -7rem; top: -9rem; width: 21rem; height: 21rem;
            border-radius: 50%; background: radial-gradient(circle, rgba(79, 152, 232, .17), transparent 68%);
            animation: ba-ambient 24s ease-in-out infinite alternate;
        }
        @keyframes ba-ambient { to { transform: translate(-1.2rem, 1rem); opacity: .65; } }
        @keyframes ba-hero-sweep {
            0%, 18% { transform: translate3d(0,0,0) skewX(-18deg); opacity: 0; }
            30% { opacity: .8; }
            68%, 100% { transform: translate3d(390%,0,0) skewX(-18deg); opacity: 0; }
        }
        .hero-content { position: relative; z-index: 1; }
        .hero h1 { margin: 0; color: var(--ba-text); font-size: clamp(1.45rem, 2vw, 1.9rem); font-weight: 730; letter-spacing: -.045em; line-height: 1.2; }
        .hero p { color: #BAC6D6; font-size: .9rem; line-height: 1.5; margin: .48rem 0 .8rem; }
        .badge, .status-pill {
            display: inline-flex; align-items: center; gap: .48rem; padding: .34rem .62rem;
            border-radius: 999px; border: 1px solid rgba(91,166,248,.22);
            background: rgba(91,166,248,.08); color: #B9D9FC;
            font-size: .67rem; font-weight: 700; letter-spacing: .09em; text-transform: uppercase;
        }
        .signal-strip { display: flex; flex-wrap: wrap; gap: .45rem .9rem; padding: .58rem .78rem; margin: 0 0 1rem; border: 1px solid rgba(148,163,184,.15); border-radius: 10px; background: rgba(10,17,29,.68); box-shadow: inset 0 1px 0 rgba(255,255,255,.025); backdrop-filter: blur(12px); }
        .signal-pill { display: inline-flex; align-items: center; gap: .38rem; color: var(--ba-muted); font-size: .71rem; line-height: 1.35; }
        .signal-dot { display: inline-block; flex: 0 0 auto; width: 7px; height: 7px; border-radius: 50%; background: var(--ba-green); box-shadow: 0 0 0 3px rgba(66,201,154,.1); animation: ba-status-breathe 3.8s ease-in-out infinite; }
        @keyframes ba-status-breathe { 50% { opacity: .72; box-shadow: 0 0 0 4px rgba(66,201,154,.07), 0 0 10px rgba(66,201,154,.18); } }
        .landing-status { display: flex; flex-wrap: wrap; gap: .45rem; margin-top: .25rem; }
        .workflow-rail { display: flex; align-items: center; justify-content: space-between; gap: .45rem; overflow-x: auto; padding: .78rem .85rem; border: 1px solid rgba(148,163,184,.16); border-radius: 10px; background: rgba(9,16,28,.72); box-shadow: inset 0 1px 0 rgba(255,255,255,.03); backdrop-filter: blur(12px); white-space: nowrap; }
        .workflow-rail span { color: #CBD6E4; font-size: .76rem; font-weight: 600; }
        .workflow-rail b { color: var(--ba-blue); font-size: 1rem; font-weight: 500; }
        .module-card { min-height: 112px; margin: 0 0 .45rem; padding: .88rem .95rem; border: 1px solid rgba(148,163,184,.16); border-radius: 11px; background: linear-gradient(145deg, rgba(16,27,43,.84), rgba(10,17,29,.80)); box-shadow: inset 0 1px 0 rgba(255,255,255,.035), 0 10px 26px rgba(0,0,0,.16); backdrop-filter: blur(14px); transition: transform .28s ease, border-color .28s ease, box-shadow .28s ease; }
        .module-card:hover { transform: translateY(-3px); border-color: rgba(91,166,248,.42); box-shadow: inset 0 1px 0 rgba(255,255,255,.06), 0 14px 30px rgba(0,0,0,.23), 0 0 22px rgba(58,137,209,.10); }
        .module-number { color: var(--ba-cyan); font-size: .64rem; font-weight: 750; letter-spacing: .12em; }
        .module-title { margin-top: .34rem; color: var(--ba-text); font-size: .97rem; font-weight: 690; }
        .module-description { margin-top: .27rem; color: var(--ba-muted); font-size: .76rem; line-height: 1.45; }
        .info-card { min-height: 100%; padding: .9rem 1rem; border: 1px solid rgba(148,163,184,.16); border-radius: 10px; background: linear-gradient(145deg, rgba(15,25,40,.82), rgba(10,17,29,.78)); box-shadow: inset 0 1px 0 rgba(255,255,255,.035), 0 10px 26px rgba(0,0,0,.14); backdrop-filter: blur(13px); }
        .info-card h4 { margin: 0 0 .45rem; color: var(--ba-text); font-size: .9rem; font-weight: 680; }
        .info-card p { margin: 0; color: #C4CFDC; font-size: .82rem; line-height: 1.56; }
        .info-card small { color: var(--ba-subtle); font-size: .72rem; }
        .ba-footer { display: flex; flex-wrap: wrap; justify-content: space-between; gap: .35rem 1rem; padding: .85rem .1rem .2rem; margin-top: 1.8rem; border-top: 1px solid rgba(148,163,184,.13); color: var(--ba-subtle); font-size: .72rem; line-height: 1.5; }
        .ba-footer strong { color: var(--ba-muted); font-weight: 650; }
        .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 165px), 1fr)); gap: .72rem; margin: .15rem 0 1.05rem; align-items: stretch; }
        .card, .metric-card, .glass-card {
            min-height: 106px; height: 100%; box-sizing: border-box; padding: .86rem .92rem;
            position: relative; overflow: hidden; border-radius: 11px;
            background: linear-gradient(145deg, rgba(16,27,43,.84), rgba(10,17,29,.82));
            border: 1px solid rgba(148,163,184,.16);
            box-shadow: inset 0 1px 0 rgba(255,255,255,.045), 0 12px 28px rgba(0,0,0,.18);
            backdrop-filter: blur(14px);
            animation: ba-card-arrive .55s ease-out both;
            transition: transform .28s ease, border-color .28s ease, box-shadow .28s ease;
        }
        .card:nth-child(2), .metric-card:nth-child(2) { animation-delay: 45ms; }
        .card:nth-child(3), .metric-card:nth-child(3) { animation-delay: 90ms; }
        .card:nth-child(4), .metric-card:nth-child(4) { animation-delay: 135ms; }
        .card:nth-child(5), .metric-card:nth-child(5) { animation-delay: 180ms; }
        .card:nth-child(6), .metric-card:nth-child(6) { animation-delay: 225ms; }
        .card:nth-child(7), .metric-card:nth-child(7) { animation-delay: 270ms; }
        .card:nth-child(8), .metric-card:nth-child(8) { animation-delay: 315ms; }
        @keyframes ba-card-arrive { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
        .card:hover, .metric-card:hover, .glass-card:hover { transform: translateY(-3px); border-color: rgba(91,166,248,.42); box-shadow: inset 0 1px 0 rgba(255,255,255,.065), 0 16px 34px rgba(0,0,0,.25), 0 0 24px rgba(55,132,202,.11); }
        .card::before, .metric-card::before { content: ""; position: absolute; inset: 0 auto 0 0; width: 2px; background: var(--ba-accent, var(--ba-blue)); opacity: .82; }
        .card .icon { display: none; }
        .card .label, .metric-card .label { color: var(--ba-muted); font-size: .66rem; font-weight: 700; letter-spacing: .09em; line-height: 1.35; text-transform: uppercase; margin: 0 0 .45rem; }
        .card .value, .metric-card .value { color: var(--ba-text); font-size: clamp(1.35rem, 1.9vw, 1.8rem); font-weight: 720; letter-spacing: -.04em; line-height: 1.12; overflow-wrap: anywhere; }
        .card small, .metric-card small { display: block; margin-top: .38rem; color: var(--ba-subtle); font-size: .7rem; line-height: 1.35; }
        .card.blue, .metric-card.blue { --ba-accent: var(--ba-blue); }
        .card.cyan, .metric-card.cyan { --ba-accent: var(--ba-cyan); }
        .card.purple, .card.violet, .metric-card.purple { --ba-accent: var(--ba-violet); }
        .card.green, .metric-card.green { --ba-accent: var(--ba-green); }
        .card.orange, .card.yellow, .metric-card.orange { --ba-accent: var(--ba-amber); }
        .card.red, .metric-card.red { --ba-accent: var(--ba-red); }
        .card.pink { --ba-accent: var(--ba-violet); }
        .section-header, .section-title {
            display: flex; align-items: center; gap: .65rem; margin: 1.35rem 0 .72rem;
            color: var(--ba-text); font-size: 1rem; font-weight: 680; letter-spacing: -.02em; line-height: 1.3;
        }
        .section-header::after { content: ""; flex: 1; height: 1px; background: linear-gradient(90deg, rgba(148,163,184,.2), transparent); }
        .stTabs [data-baseweb="tab-list"] { gap: .3rem; padding: .28rem; border: 1px solid var(--ba-border); border-radius: 10px; background: rgba(13,20,32,.76); }
        .stTabs [data-baseweb="tab"] { min-height: 2.25rem; padding: .4rem .78rem; border-radius: 7px; color: var(--ba-muted); font-size: .8rem; font-weight: 600; transition: color .16s ease, background .16s ease; }
        .stTabs [data-baseweb="tab"]:hover { color: var(--ba-text); background: rgba(148,163,184,.07); }
        .stTabs [aria-selected="true"] { color: var(--ba-text) !important; background: rgba(91,166,248,.13) !important; }
        .stTabs [data-baseweb="tab-highlight"] { background: var(--ba-blue); height: 2px; }
        [data-testid="stVerticalBlockBorderWrapper"], [data-testid="stForm"], [data-testid="stExpander"] {
            border-color: var(--ba-border) !important; border-radius: 11px !important; background: rgba(16,24,39,.47);
        }
        [data-testid="stWidgetLabel"] p, label, .stCaption, [data-testid="stCaptionContainer"] { color: var(--ba-muted); }
        input, textarea, [data-baseweb="select"] > div { background: #111B2A !important; border-color: rgba(148,163,184,.22) !important; border-radius: 8px !important; color: var(--ba-text) !important; }
        input:hover, textarea:hover, [data-baseweb="select"] > div:hover { border-color: rgba(91,166,248,.48) !important; }
        input:focus, textarea:focus, [data-baseweb="select"] > div:focus-within, button:focus-visible, a:focus-visible {
            outline: 2px solid rgba(91,166,248,.72) !important; outline-offset: 2px !important;
        }
        [data-testid="stMultiSelect"] [data-baseweb="tag"] { background: rgba(91,166,248,.14); border: 1px solid rgba(91,166,248,.23); color: #C4E0FF; border-radius: 6px; }
        .stButton > button, [data-testid="stDownloadButton"] button { border: 1px solid rgba(91,166,248,.28); border-radius: 8px; background: rgba(91,166,248,.10); color: #DCEBFC; transition: background .18s ease, border-color .18s ease, transform .18s ease; }
        .stButton > button:hover, [data-testid="stDownloadButton"] button:hover { border-color: rgba(91,166,248,.55); background: rgba(91,166,248,.17); transform: translateY(-1px); }
        [data-testid="stDataFrame"], [data-testid="stTable"] { overflow: hidden; border: 1px solid var(--ba-border); border-radius: 10px; }
        [data-testid="stDataFrame"] [role="columnheader"], [data-testid="stDataFrame"] [role="gridcell"] { font-size: .78rem; }
        [data-testid="stAlert"] { border-radius: 9px; }
        .stMarkdown p, .stMarkdown li { color: #C4CFDC; line-height: 1.58; }
        .stMarkdown strong { color: var(--ba-text); }
        hr { border-color: rgba(148,163,184,.13) !important; }
        @media (max-width: 1100px) {
            .block-container { padding-left: 1rem; padding-right: 1rem; }
            .kpi-grid { grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }
        }
        @media (max-width: 720px) {
            .block-container { padding: .9rem .72rem 1.4rem; }
            .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .55rem; }
            .card, .metric-card { min-height: 94px; padding: .7rem .74rem; }
            .hero, .hero-shell { padding: 1rem; }
            .stTabs [data-baseweb="tab-list"] { overflow-x: auto; }
            .stTabs [data-baseweb="tab"] { padding: .35rem .55rem; white-space: nowrap; }
        }
        @media (prefers-reduced-motion: reduce) {
            .stApp::before, .stApp::after,
            .block-container, .hero::before, .hero::after,
            .hero-shell::before, .hero-shell::after,
            .card, .metric-card, .glass-card, .signal-dot,
            [data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {
                animation: none !important;
            }
            *, *::before, *::after {
                scroll-behavior: auto !important;
                transition-duration: .01ms !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="ba-brand">
              <div class="ba-brand-mark">Billing Assurance</div>
              <div class="ba-brand-title">Revenue Protection</div>
              <div class="ba-brand-subtitle">Control Tower · Analytics workspace</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        try:
            from utils.database import get_executive_kpis, run_query

            kpis = get_executive_kpis()
            if kpis.empty:
                raise RuntimeError("Executive KPI view returned no rows")
            hits = int(kpis.iloc[0]["control_hits"])
            customers = int(kpis.iloc[0]["unique_customers"])
            controls = int(
                run_query(
                    "SELECT COUNT(*) AS active_controls "
                    "FROM controls.business_control_matrix WHERE status = 'Active'"
                ).iloc[0]["active_controls"]
            )
            status = f"<strong>{hits:,}</strong> records · <strong>{customers:,}</strong> customers"
        except Exception as error:
            controls = "Unavailable"
            status = f"<strong>Warehouse unavailable</strong> · {html.escape(str(error))}"
        st.markdown(
            f'<div class="ba-sidebar-status"><span>DuckDB status</span><span>{status}</span></div>',
            unsafe_allow_html=True,
        )
        st.page_link("app.py", label="Control Tower Home", icon=":material/home:")
        for number, label, path, icon in _PAGES:
            st.page_link(
                path,
                label=f"{number}  {label}",
                icon=icon,
                help=f"Open {label}",
            )
        st.markdown(
            f'<div class="ba-sidebar-status"><span>Control framework</span><strong>{controls} active controls</strong></div>',
            unsafe_allow_html=True,
        )


def page_heading(eyebrow: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <header class="ba-page-head">
          <div class="ba-eyebrow">{html.escape(eyebrow)}</div>
          <h1 class="ba-page-title">{html.escape(title)}</h1>
          <div class="ba-page-subtitle">{html.escape(subtitle)}</div>
        </header>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, context: str = "", accent: str = "blue") -> str:
    return (
        f'<div class="card {html.escape(accent)}">'
        f'<div class="label">{html.escape(label)}</div>'
        f'<div class="value">{html.escape(value)}</div>'
        f"<small>{html.escape(context)}</small>"
        "</div>"
    )


def money(value: float, compact: bool = False) -> str:
    amount = float(value)
    if compact and abs(amount) >= 1000:
        return f"${amount / 1000:,.1f}K"
    return f"${amount:,.2f}"


def style_chart(fig: go.Figure, height: int = 350) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        height=height,
        colorway=CHART_COLORS,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family='Inter, "Segoe UI", sans-serif', size=12, color=PALETTE["muted"]),
        title=dict(font=dict(size=15, color=PALETTE["text"]), x=0, xanchor="left"),
        margin=dict(l=18, r=18, t=56, b=22),
        hovermode="closest",
        hoverlabel=dict(
            bgcolor="#172235",
            bordercolor="rgba(148,163,184,.25)",
            font=dict(color=PALETTE["text"], size=12),
        ),
        legend=dict(font=dict(size=11, color=PALETTE["muted"]), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=True, gridcolor="rgba(148,163,184,.12)", zerolinecolor="rgba(148,163,184,.16)"),
        yaxis=dict(showgrid=False, gridcolor="rgba(148,163,184,.12)", zerolinecolor="rgba(148,163,184,.16)"),
    )
    return fig


def section_heading(title: str, description: str | None = None) -> None:
    st.markdown(
        f'<div class="section-header">{html.escape(title)}</div>',
        unsafe_allow_html=True,
    )
    if description:
        st.caption(description)


def page_links() -> Sequence[tuple[str, str, str, str]]:
    return _PAGES


def render_footer(note: str) -> None:
    st.markdown(
        f"""
        <footer class="ba-footer">
          <strong>Billing Assurance &amp; Revenue Protection Control Tower</strong>
          <span>DuckDB · Python · Streamlit · Plotly</span>
          <span>{html.escape(note)}</span>
        </footer>
        """,
        unsafe_allow_html=True,
    )
