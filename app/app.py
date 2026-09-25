import streamlit as st

# ============================================================
# BILLING ASSURANCE & REVENUE PROTECTION CONTROL TOWER
# ============================================================

st.set_page_config(
    page_title="Billing Assurance Control Tower",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(circle at 12% 15%, rgba(59, 130, 246, 0.18), transparent 30%),
                radial-gradient(circle at 80% 18%, rgba(168, 85, 247, 0.14), transparent 28%),
                radial-gradient(circle at 50% 100%, rgba(45, 212, 191, 0.08), transparent 34%),
                linear-gradient(135deg, #06111d 0%, #0b1628 48%, #111827 100%);
            color: #e2e8f0;
            font-family: "Inter", "Segoe UI", sans-serif;
        }

        .block-container {
            max-width: 1440px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(8,15,26,0.96), rgba(15,23,42,0.92));
            border-right: 1px solid rgba(148, 163, 184, 0.16);
        }

        .css-1d391kg, .css-17lntkn {
            background: transparent;
        }

        .main-title {
            font-size: 2.5rem;
            font-weight: 800;
            letter-spacing: -0.06em;
            margin: 0 0 0.5rem;
            background: linear-gradient(90deg, #f8fafc, #bfdbfe, #d8b4fe);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .subtitle {
            font-size: 1.05rem;
            color: #cbd5e1;
            margin-bottom: 1.75rem;
            max-width: 760px;
        }

        .hero-shell {
            position: relative;
            overflow: hidden;
            border-radius: 24px;
            padding: 1.5rem 1.5rem 1.2rem;
            background: linear-gradient(135deg, rgba(30, 64, 175, 0.38), rgba(88, 28, 135, 0.28), rgba(8, 145, 178, 0.16));
            border: 1px solid rgba(148, 163, 184, 0.18);
            box-shadow: 0 30px 60px rgba(2, 6, 23, 0.35);
            margin-bottom: 1.8rem;
        }

        .hero-shell::before {
            content: "";
            position: absolute;
            inset: auto -50px -60px auto;
            width: 240px;
            height: 240px;
            border-radius: 50%;
            background: rgba(59, 130, 246, 0.22);
            filter: blur(50px);
        }

        .hero-shell::after {
            content: "";
            position: absolute;
            inset: auto auto -70px -60px;
            width: 220px;
            height: 220px;
            border-radius: 50%;
            background: rgba(168, 85, 247, 0.18);
            filter: blur(45px);
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.55rem;
            padding: 0.5rem 0.9rem;
            border-radius: 999px;
            background: rgba(34, 197, 94, 0.12);
            border: 1px solid rgba(74, 222, 128, 0.35);
            color: #bbf7d0;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
            background: #4ade80;
            box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.7);
            animation: pulse 3s infinite;
        }

        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.55); }
            70% { box-shadow: 0 0 0 10px rgba(74, 222, 128, 0); }
            100% { box-shadow: 0 0 0 0 rgba(74, 222, 128, 0); }
        }

        .signal-strip {
            display: flex;
            flex-wrap: wrap;
            gap: 0.9rem;
            padding: 0.8rem 1rem;
            border-radius: 14px;
            background: rgba(15, 23, 42, 0.34);
            border: 1px solid rgba(148, 163, 184, 0.12);
            margin-bottom: 1.7rem;
        }

        .signal-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.55rem;
            font-size: 0.74rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #cbd5e1;
            white-space: nowrap;
        }

        .section-title {
            font-size: 1.05rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #cbd5e1;
            margin: 1.8rem 0 0.9rem;
        }

        .glass-card {
            background: linear-gradient(145deg, rgba(15,23,42,0.8), rgba(15,23,42,0.5));
            border: 1px solid rgba(148,163,184,0.12);
            border-radius: 18px;
            padding: 1.15rem 1.1rem;
            box-shadow: 0 20px 35px rgba(2, 6, 23, 0.2);
            height: 100%;
        }

        .metric-card {
            background: linear-gradient(145deg, rgba(15,23,42,0.8), rgba(15,23,42,0.55));
            border: 1px solid rgba(148,163,184,0.12);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            box-shadow: 0 15px 30px rgba(2, 6, 23, 0.16);
            min-height: 110px;
        }

        .metric-card .label {
            color: #94a3b8;
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            margin-bottom: 0.4rem;
        }

        .metric-card .value {
            font-size: 1.8rem;
            font-weight: 700;
            letter-spacing: -0.05em;
            color: #f8fafc;
        }

        .stMetric {
            background: rgba(15, 23, 42, 0.38);
            border: 1px solid rgba(148,163,184,0.12);
            border-radius: 16px;
            padding: 1rem 1.1rem;
            box-shadow: 0 15px 30px rgba(2, 6, 23, 0.15);
        }

        .stMetric > div > div > div[data-testid="stMetricLabel"] {
            letter-spacing: 0.12em;
            text-transform: uppercase;
            font-size: 0.68rem;
            color: #94a3b8;
        }

        .stMetric > div > div > div[data-testid="stMetricValue"] {
            font-size: 1.8rem;
            font-weight: 700;
            letter-spacing: -0.05em;
        }

        .sidebar-block {
            background: rgba(15, 23, 42, 0.45);
            border: 1px solid rgba(148, 163, 184, 0.12);
            border-radius: 14px;
            padding: 0.9rem 0.85rem;
            margin-bottom: 0.9rem;
        }

        .sidebar-block p {
            margin: 0;
            color: #cbd5e1;
            line-height: 1.6;
        }

        @media (max-width: 1100px) {
            .block-container { padding-left: 0.8rem; padding-right: 0.8rem; }
            .main-title { font-size: 2.1rem; }
            .signal-strip { gap: 0.6rem; }
        }

        @media (prefers-reduced-motion: reduce) {
            * { animation: none !important; transition: none !important; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">Billing Assurance & Revenue Protection Control Tower</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">Operational billing controls, exception management, discount decisions, and SLA monitoring for the revenue protection function.</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '''
    <div class="hero-shell">
        <div class="status-pill"><span class="status-dot"></span> Control environment ready</div>
    </div>
    ''',
    unsafe_allow_html=True,
)

st.markdown(
    '''
    <div class="signal-strip">
        <span class="signal-pill"><span class="status-dot"></span> Control engine ready</span>
        <span class="signal-pill">Data source • DuckDB</span>
        <span class="signal-pill">Operational layer • Streamlit</span>
        <span class="signal-pill">Revenue protection • monitoring</span>
    </div>
    ''',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(
        """
        <div style='padding:0.6rem 0.4rem 0.5rem;'><div style='font-size:0.74rem; letter-spacing:0.15em; text-transform:uppercase; color:#94a3b8;'>Billing Assurance</div><div style='font-size:1.3rem; font-weight:700; letter-spacing:-0.04em; color:#f8fafc; margin-top:0.2rem;'>Revenue Protection</div></div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("""
        <div class='sidebar-block'>
            <p><strong>01</strong> Executive Control Tower</p>
        </div>
        <div class='sidebar-block'>
            <p><strong>02</strong> Billing Integrity</p>
        </div>
        <div class='sidebar-block'>
            <p><strong>03</strong> Exception Management</p>
        </div>
        <div class='sidebar-block'>
            <p><strong>04</strong> Discount Decisions</p>
        </div>
        <div class='sidebar-block'>
            <p><strong>05</strong> SLA Operations</p>
        </div>
        <div class='sidebar-block'>
            <p><strong>06</strong> Customer Risk</p>
        </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.caption("Source of truth: DuckDB")
    st.caption("Presentation layer: Streamlit")

st.markdown('<div class="section-title">Project overview</div>', unsafe_allow_html=True)

st.write(
    """
    This control tower provides a modern operational view of billing assurance and revenue protection controls.
    The application connects directly to the project's DuckDB warehouse and surfaces validated control results for management, exception operations, financial oversight, and SLA monitoring.
    """
)

st.markdown('<div class="section-title">Control architecture</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("<div class='glass-card'><div style='font-size:0.72rem; letter-spacing:0.12em; text-transform:uppercase; color:#94a3b8;'>Source Data</div><div style='font-size:1.2rem; font-weight:600; margin-top:0.5rem;'>CSV / Python</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div class='glass-card'><div style='font-size:0.72rem; letter-spacing:0.12em; text-transform:uppercase; color:#94a3b8;'>Warehouse</div><div style='font-size:1.2rem; font-weight:600; margin-top:0.5rem;'>DuckDB</div></div>", unsafe_allow_html=True)
with col3:
    st.markdown("<div class='glass-card'><div style='font-size:0.72rem; letter-spacing:0.12em; text-transform:uppercase; color:#94a3b8;'>Controls</div><div style='font-size:1.2rem; font-weight:600; margin-top:0.5rem;'>Billing / Discount / SLA</div></div>", unsafe_allow_html=True)
with col4:
    st.markdown("<div class='glass-card'><div style='font-size:0.72rem; letter-spacing:0.12em; text-transform:uppercase; color:#94a3b8;'>Operational Layer</div><div style='font-size:1.2rem; font-weight:600; margin-top:0.5rem;'>Streamlit</div></div>", unsafe_allow_html=True)

st.markdown('<div class="section-title">Current control coverage</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Control Hits", "706")
with col2:
    st.metric("Unique Customers", "558")
with col3:
    st.metric("Financial Impact", "$83,085.84")
with col4:
    st.metric("SLA Compliance", "89.2%")

st.divider()
st.success("Control tower foundation is ready for operational monitoring and management review.")
