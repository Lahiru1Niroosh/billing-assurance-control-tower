import pandas as pd
import plotly.express as px
import streamlit as st

from utils.database import run_query

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Billing Integrity Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# NEXT-LEVEL CSS & ANIMATIONS
# ============================================================
st.markdown("""
<style>
    /* -------------------------------------------------------
       GLOBAL & BACKGROUND
    ------------------------------------------------------- */
    .stApp {
        background: 
            radial-gradient(circle at 10% 10%, rgba(14, 165, 233, 0.15), transparent 35%),
            radial-gradient(circle at 90% 15%, rgba(139, 92, 246, 0.12), transparent 35%),
            radial-gradient(circle at 50% 90%, rgba(6, 182, 212, 0.1), transparent 40%),
            linear-gradient(135deg, #050b16 0%, #0b1628 50%, #111827 100%);
        color: #f8fafc;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.25); }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    /* -------------------------------------------------------
       ANIMATIONS
    ------------------------------------------------------- */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes pulseGlow {
        0% { box-shadow: 0 0 0 0 rgba(14, 165, 233, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(14, 165, 233, 0); }
        100% { box-shadow: 0 0 0 0 rgba(14, 165, 233, 0); }
    }

    @keyframes floatOrb {
        0% { transform: translate(0, 0); }
        50% { transform: translate(-20px, 15px); }
        100% { transform: translate(10px, -10px); }
    }

    /* -------------------------------------------------------
       HERO SECTION
    ------------------------------------------------------- */
    .hero {
        position: relative;
        overflow: hidden;
        padding: 40px 45px;
        border-radius: 24px;
        background: linear-gradient(135deg, rgba(3, 105, 161, 0.5), rgba(124, 58, 237, 0.3), rgba(8, 145, 178, 0.2));
        border: 1px solid rgba(255, 255, 255, 0.12);
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        margin-bottom: 30px;
        animation: fadeInUp 0.8s ease-out;
    }

    .hero::before {
        content: "";
        position: absolute;
        width: 300px; height: 300px;
        right: -80px; top: -120px;
        border-radius: 50%;
        background: rgba(14, 165, 233, 0.25);
        filter: blur(50px);
        animation: floatOrb 8s ease-in-out infinite;
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 250px; height: 250px;
        left: -100px; bottom: -130px;
        border-radius: 50%;
        background: rgba(139, 92, 246, 0.2);
        filter: blur(50px);
        animation: floatOrb 10s ease-in-out infinite reverse;
    }

    .hero-content { position: relative; z-index: 2; }

    .hero h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #ffffff, #7dd3fc, #c4b5fd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero p {
        color: #cbd5e1;
        font-size: 1.1rem;
        margin: 10px 0 18px 0;
        font-weight: 400;
    }

    .badge {
        display: inline-flex;
        align-items: center;
        padding: 8px 16px;
        border-radius: 999px;
        color: #bae6fd;
        background: rgba(14, 165, 233, 0.14);
        border: 1px solid rgba(56, 189, 248, 0.4);
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        animation: pulseGlow 3s infinite;
    }

    /* -------------------------------------------------------
       KPI CARDS
    ------------------------------------------------------- */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 18px;
        margin-bottom: 25px;
    }

    .card {
        position: relative;
        padding: 22px;
        border-radius: 20px;
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.07), rgba(255, 255, 255, 0.02));
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(16px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        overflow: hidden;
        animation: fadeInUp 0.6s ease-out backwards;
    }

    /* Staggered animation delays */
    .card:nth-child(1) { animation-delay: 0.1s; }
    .card:nth-child(2) { animation-delay: 0.15s; }
    .card:nth-child(3) { animation-delay: 0.2s; }
    .card:nth-child(4) { animation-delay: 0.25s; }
    .card:nth-child(5) { animation-delay: 0.1s; }
    .card:nth-child(6) { animation-delay: 0.15s; }
    .card:nth-child(7) { animation-delay: 0.2s; }
    .card:nth-child(8) { animation-delay: 0.25s; }

    .card:hover {
        transform: translateY(-6px) scale(1.01);
        border-color: rgba(125, 211, 252, 0.4);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4), 0 0 20px rgba(14, 165, 233, 0.15);
    }

    .card::after {
        content: "";
        position: absolute;
        width: 120px; height: 120px;
        right: -40px; bottom: -50px;
        border-radius: 50%;
        opacity: 0.15;
        filter: blur(15px);
        transition: opacity 0.3s ease;
    }

    .card:hover::after { opacity: 0.3; }

    .card .icon {
        font-size: 1.5rem;
        margin-bottom: 10px;
        display: block;
    }

    .card .label {
        color: #94a3b8;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 6px;
    }

    .card .value {
        font-size: 1.7rem;
        font-weight: 800;
        color: #f8fafc;
        letter-spacing: -0.5px;
    }

    /* Accent Colors */
    .card.blue::after { background: #0ea5e9; }
    .card.purple::after { background: #a855f7; }
    .card.cyan::after { background: #06b6d4; }
    .card.orange::after { background: #f97316; }
    .card.red::after { background: #ef4444; }
    .card.yellow::after { background: #eab308; }
    .card.green::after { background: #22c55e; }
    .card.pink::after { background: #ec4899; }

    /* -------------------------------------------------------
       SECTION HEADERS
    ------------------------------------------------------- */
    .section-header {
        margin: 35px 0 20px 0;
        font-size: 1.4rem;
        font-weight: 750;
        color: #f8fafc;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .section-header::after {
        content: "";
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(255,255,255,0.15), transparent);
    }

    /* -------------------------------------------------------
       TABS (Standardized & Clean)
    ------------------------------------------------------- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(255, 255, 255, 0.03);
        padding: 6px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 20px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 10px 22px;
        color: #94a3b8;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        border: none;
        background: transparent;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #e2e8f0;
        background: rgba(255, 255, 255, 0.05);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.25), rgba(139, 92, 246, 0.15));
        color: #ffffff;
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.2);
        border: 1px solid rgba(125, 211, 252, 0.2);
    }

    /* -------------------------------------------------------
       INFO / MANAGEMENT CARDS
    ------------------------------------------------------- */
    .info-card {
        padding: 26px;
        border-radius: 20px;
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0.02));
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
        height: 100%;
        transition: transform 0.25s ease, border-color 0.25s ease;
        animation: fadeInUp 0.6s ease-out backwards;
    }

    .info-card:hover {
        transform: translateY(-4px);
        border-color: rgba(125, 211, 252, 0.3);
    }

    .info-card h4 {
        margin: 0 0 14px 0;
        color: #7dd3fc;
        font-size: 1.1rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .info-card p {
        color: #cbd5e1;
        line-height: 1.7;
        font-size: 0.95rem;
        margin: 0;
    }

    .info-card strong {
        color: #f8fafc;
        font-weight: 700;
    }

    /* -------------------------------------------------------
       PLOTLY CHART CONTAINERS
    ------------------------------------------------------- */
    .stPlotlyChart {
        border-radius: 18px;
        overflow: hidden;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 10px;
        transition: border-color 0.3s ease;
    }

    .stPlotlyChart:hover {
        border-color: rgba(255, 255, 255, 0.15);
    }

    /* -------------------------------------------------------
       EXPANDER
    ------------------------------------------------------- */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        color: #cbd5e1;
        font-weight: 600;
    }

    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 0 0 12px 12px;
        color: #94a3b8;
    }

    /* -------------------------------------------------------
       DATAFRAME
    ------------------------------------------------------- */
    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* -------------------------------------------------------
       MULTISELECT
    ------------------------------------------------------- */
    .stMultiSelect [data-baseweb="tag"] {
        background: rgba(14, 165, 233, 0.2);
        border: 1px solid rgba(56, 189, 248, 0.3);
        color: #bae6fd;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def card(icon, label, value, accent="blue"):
    return f'''
    <div class="card {accent}">
        <div class="icon">{icon}</div>
        <div class="label">{label}</div>
        <div class="value">{value}</div>
    </div>
    '''


def money(value):
    return f"${float(value):,.2f}"


def plot_style(fig, height=360):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e5e7eb",
        margin=dict(l=15, r=15, t=55, b=15),
        hovermode="x unified"
    )
    return fig


# ============================================================
# DATA LOADING
# ============================================================
try:
    performance = run_query("SELECT * FROM controls.v_control_performance")
    exceptions = run_query("SELECT * FROM controls.v_exception_queue WHERE control_id IN ('C001','C002','C003')")
except Exception as error:
    st.error(f"Unable to load billing data: {error}")
    st.stop()

scope = ["C001", "C002", "C003"]
controls = performance[performance.control_id.isin(scope)].copy()
if controls.empty:
    st.error("Billing control data is unavailable from DuckDB.")
    st.stop()

hits = int(controls.control_hits.sum())
control_customer_hits = int(controls.unique_customers.sum())
impact = float(controls.financial_impact.sum())


def value(control_id, column):
    return controls.loc[controls.control_id == control_id, column].sum()


rate_hits = int(value("C003", "control_hits"))
duplicate_hits = int(value("C001", "control_hits"))
missing_hits = int(value("C002", "control_hits"))
rate_impact = float(value("C003", "financial_impact"))

# ============================================================
# HERO SECTION
# ============================================================
st.markdown('''
<div class="hero">
    <div class="hero-content">
        <h1>Billing Integrity Command Center</h1>
        <p>Detecting duplicate billing • missing charges • rate mismatches • financial exposure</p>
        <span class="badge">● BILLING CONTROLS ACTIVE</span>
    </div>
</div>
''', unsafe_allow_html=True)

st.markdown('''
<div class="signal-strip">
    <span><span class="signal-dot"></span> Control engine ready</span>
    <span>Data source • DuckDB</span>
    <span>Integrity checks • active</span>
    <span>Operating mode • validation</span>
</div>
''', unsafe_allow_html=True)

# ============================================================
# KPI GRID
# ============================================================
st.markdown(f'''
<div class="kpi-grid">
    <div class="card blue">
        <div class="icon">🛡️</div>
        <div class="label">Billing Control Hits</div>
        <div class="value">{hits:,}</div>
    </div>
    <div class="card purple">
        <div class="icon">👥</div>
        <div class="label">Customer Control Hits</div>
        <div class="value">{control_customer_hits:,}</div>
    </div>
    <div class="card cyan">
        <div class="icon">💰</div>
        <div class="label">Financial Impact</div>
        <div class="value">{money(impact)}</div>
    </div>
    <div class="card orange">
        <div class="icon">⚠️</div>
        <div class="label">Rate Mismatch Hits</div>
        <div class="value">{rate_hits:,}</div>
    </div>
    <div class="card red">
        <div class="icon">🔁</div>
        <div class="label">Duplicate Billing</div>
        <div class="value">{duplicate_hits:,}</div>
    </div>
    <div class="card yellow">
        <div class="icon">❌</div>
        <div class="label">Missing / Zero Billing</div>
        <div class="value">{missing_hits:,}</div>
    </div>
    <div class="card green">
        <div class="icon">💵</div>
        <div class="label">Rate Impact</div>
        <div class="value">{money(rate_impact)}</div>
    </div>
    <div class="card pink">
        <div class="icon">📊</div>
        <div class="label">Average Impact / Hit</div>
        <div class="value">{money(impact/hits if hits else 0)}</div>
    </div>
</div>
''', unsafe_allow_html=True)

st.caption("Customer Control Hits is a sum of control-level counts and can include one customer across multiple controls.")

# ============================================================
# TABS
# ============================================================
overview, analysis, queue_tab, investigation = st.tabs([
    "📊 Integrity Overview",
    "🔍 Control Analysis",
    "📋 Exception Queue",
    "🧠 Investigation"
])

# ------------------------------------------------------------
# TAB 1: INTEGRITY OVERVIEW
# ------------------------------------------------------------
with overview:
    st.markdown('<div class="section-header">Billing Control Landscape</div>', unsafe_allow_html=True)
    left, right = st.columns(2)
    
    with left:
        fig = px.bar(
            controls, x="control_id", y="control_hits", 
            text="control_hits", title="Billing Exceptions by Control", 
            template="plotly_dark"
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(plot_style(fig), use_container_width=True)
    
    with right:
        fig = px.bar(
            controls, x="control_id", y="financial_impact", 
            text="financial_impact", title="Financial Impact by Billing Control", 
            template="plotly_dark"
        )
        fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        fig.update_layout(yaxis_tickprefix="$")
        st.plotly_chart(plot_style(fig), use_container_width=True)
    
    st.markdown('<div class="section-header">Control Mix</div>', unsafe_allow_html=True)
    fig = px.pie(
        controls, names="control_id", values="control_hits", 
        hole=.58, title="Billing Control Hit Distribution", 
        template="plotly_dark"
    )
    fig.update_traces(textinfo="label+percent")
    st.plotly_chart(plot_style(fig, 380), use_container_width=True)

# ------------------------------------------------------------
# TAB 2: CONTROL ANALYSIS
# ------------------------------------------------------------
with analysis:
    st.markdown('<div class="section-header">Billing Control Assessment</div>', unsafe_allow_html=True)
    definitions = [
        ("🔁 Duplicate Billing", f"C001 identified <strong>{duplicate_hits:,}</strong> hits. Investigate customer and billing records before any financial adjustment."),
        ("❌ Missing / Zero Billing", f"C002 identified <strong>{missing_hits:,}</strong> cases. Validate billing completeness, customer status and service activity."),
        ("💰 Rate Mismatch", f"C003 identified <strong>{rate_hits:,}</strong> cases and <strong>{money(rate_impact)}</strong> of impact. Compare billed and expected rates, including legitimate pricing or contract changes.")
    ]
    for col, (title, text) in zip(st.columns(3), definitions):
        with col:
            st.markdown(f'''
            <div class="info-card">
                <h4>{title}</h4>
                <p>{text}</p>
            </div>
            ''', unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">Control-Level Metrics</div>', unsafe_allow_html=True)
    display = controls.copy()
    display["financial_impact"] = display["financial_impact"].map(money)
    st.dataframe(display, use_container_width=True, hide_index=True)
    st.caption("Financial impact represents control-identified impact requiring investigation and is not confirmed revenue loss.")

# ------------------------------------------------------------
# TAB 3: EXCEPTION QUEUE
# ------------------------------------------------------------
with queue_tab:
    st.markdown('<div class="section-header">Billing Exception Detail</div>', unsafe_allow_html=True)
    if exceptions.empty:
        st.info("No billing integrity exceptions are currently available.")
    else:
        selected_controls = st.multiselect("Control", scope, default=scope)
        selected_status = st.multiselect("Status", sorted(exceptions.status.unique()), default=[])
        selected_severity = st.multiselect("Severity", sorted(exceptions.severity.unique()), default=[])
        
        filtered = exceptions[exceptions.control_id.isin(selected_controls)]
        if selected_status:
            filtered = filtered[filtered.status.isin(selected_status)]
        if selected_severity:
            filtered = filtered[filtered.severity.isin(selected_severity)]
        
        cols = [c for c in ["exception_id", "control_id", "control_name", "customer_id", "financial_impact", "severity", "status"] if c in filtered]
        table = filtered[cols].sort_values("financial_impact", ascending=False).copy()
        table["financial_impact"] = table["financial_impact"].map(money)
        st.dataframe(table, use_container_width=True, hide_index=True, height=430)

# ------------------------------------------------------------
# TAB 4: INVESTIGATION
# ------------------------------------------------------------
with investigation:
    st.markdown('<div class="section-header">Billing Control Investigation</div>', unsafe_allow_html=True)
    if exceptions.empty:
        st.info("No billing integrity exceptions are currently available.")
    else:
        selected_id = st.selectbox(
            "Select Exception",
            exceptions.exception_id.tolist(),
            format_func=lambda x: f"EXC-{int(x):03d}"
        )
        selected = exceptions[exceptions.exception_id == selected_id].iloc[0]
        
        details = st.columns(2)
        with details[0]:
            st.markdown(f'''
            <div class="info-card">
                <h4>📄 Exception</h4>
                <p>
                    Control: <strong>{selected.control_id}</strong><br>
                    Control Name: <strong>{selected.control_name}</strong><br>
                    Customer: <strong>{selected.customer_id}</strong><br>
                    Severity: <strong>{selected.severity}</strong><br>
                    Status: <strong>{selected.status}</strong>
                </p>
            </div>
            ''', unsafe_allow_html=True)
        
        with details[1]:
            st.markdown(f'''
            <div class="info-card">
                <h4>💵 Financial Detail</h4>
                <p>
                    Financial impact: <strong>{money(selected.financial_impact)}</strong><br>
                    Exception type: {selected.exception_type}<br><br>
                    {selected.description}
                </p>
            </div>
            ''', unsafe_allow_html=True)
    
    st.markdown('''
    <div class="info-card">
        <h4>🛡️ Active Billing Controls</h4>
        <p>
            <strong>C001</strong> • Duplicate Billing<br>
            <strong>C002</strong> • Missing Billing Total<br>
            <strong>C003</strong> • Rate Mismatch
        </p>
        <small style="color: #64748b; display: block; margin-top: 10px;">
            These controls identify records for investigation; they do not automatically establish confirmed loss.
        </small>
    </div>
    ''', unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown('''
<div style="text-align:center; color:#64748b; padding:30px 24px; font-size:.82rem; border-top: 1px solid rgba(255,255,255,0.05); margin-top: 40px;">
    <strong>Billing Assurance & Revenue Protection Control Tower</strong><br>
    Billing Integrity • C001 • C002 • C003<br><br>
    Financial impact represents control-identified impact requiring investigation and is not confirmed revenue loss.
</div>
''', unsafe_allow_html=True)