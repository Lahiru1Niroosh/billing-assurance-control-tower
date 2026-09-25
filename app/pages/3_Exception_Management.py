import html
import pandas as pd
import plotly.express as px
import streamlit as st
from utils.database import run_query

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Exception Management Center",
    page_icon="🚨",
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
            radial-gradient(circle at 10% 10%, rgba(239, 68, 68, 0.14), transparent 35%),
            radial-gradient(circle at 90% 15%, rgba(14, 165, 233, 0.12), transparent 35%),
            radial-gradient(circle at 50% 90%, rgba(245, 158, 11, 0.08), transparent 40%),
            linear-gradient(135deg, #07111f 0%, #0b1628 50%, #172033 100%);
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
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
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
        background: linear-gradient(135deg, rgba(127, 29, 29, 0.5), rgba(30, 64, 175, 0.35), rgba(8, 145, 178, 0.2));
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
        background: rgba(239, 68, 68, 0.25);
        filter: blur(50px);
        animation: floatOrb 8s ease-in-out infinite;
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 250px; height: 250px;
        left: -100px; bottom: -130px;
        border-radius: 50%;
        background: rgba(14, 165, 233, 0.2);
        filter: blur(50px);
        animation: floatOrb 10s ease-in-out infinite reverse;
    }

    .hero-content { position: relative; z-index: 2; }

    .hero h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #ffffff, #fca5a5, #fecaca);
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
        color: #fecaca;
        background: rgba(239, 68, 68, 0.14);
        border: 1px solid rgba(248, 113, 113, 0.4);
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
        border-color: rgba(248, 113, 113, 0.4);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4), 0 0 20px rgba(239, 68, 68, 0.15);
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
    .card.blue::after { background: #3b82f6; }
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
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.25), rgba(14, 165, 233, 0.15));
        color: #ffffff;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2);
        border: 1px solid rgba(248, 113, 113, 0.25);
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
        border-color: rgba(248, 113, 113, 0.3);
    }

    .info-card h4 {
        margin: 0 0 14px 0;
        color: #fca5a5;
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
       EXPANDER & INFO BOXES
    ------------------------------------------------------- */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        color: #cbd5e1;
        font-weight: 600;
    }

    .stAlert {
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.08);
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
       SELECT BOX
    ------------------------------------------------------- */
    .stSelectbox [data-baseweb="select"] > div {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        color: #e2e8f0;
    }

    .stSelectbox [data-baseweb="select"] > div:hover {
        border-color: rgba(248, 113, 113, 0.4);
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


def money(v):
    return f"${float(v):,.2f}"


def style(fig, h=350):
    fig.update_layout(
        height=h,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e5e7eb",
        margin=dict(l=15, r=15, t=55, b=15),
        hovermode="x unified"
    )
    return fig


def priority(row):
    if row.severity == "HIGH" and row.status == "OPEN":
        return "Critical"
    if row.severity == "HIGH" and row.status == "MONITOR":
        return "High"
    if row.severity == "MEDIUM" and row.status in {"OPEN", "MONITOR"}:
        return "Medium"
    return "Low"


# ============================================================
# DATA LOADING
# ============================================================
try:
    exceptions = run_query("SELECT * FROM controls.v_exception_queue")
except Exception as error:
    st.error(f"Unable to load exceptions: {error}")
    st.stop()

if exceptions.empty:
    st.error("No exceptions are currently available in DuckDB.")
    st.stop()

exceptions["financial_impact"] = pd.to_numeric(exceptions.financial_impact, errors="coerce").fillna(0)
exceptions["priority"] = exceptions.apply(priority, axis=1)

# Extract Metrics
total = len(exceptions)
open_count = int((exceptions.status == "OPEN").sum())
reviewed = int((exceptions.status == "REVIEWED").sum())
monitor = int((exceptions.status == "MONITOR").sum())
high = int((exceptions.severity == "HIGH").sum())
impact = exceptions.financial_impact.sum()
customers = exceptions.customer_id.nunique()

# ============================================================
# HERO SECTION
# ============================================================
st.markdown('''
<div class="hero">
    <div class="hero-content">
        <h1>Exception Management Center</h1>
        <p>Prioritize • Investigate • Resolve • Monitor</p>
        <span class="badge">● EXCEPTION WORKFLOW ACTIVE</span>
    </div>
</div>
''', unsafe_allow_html=True)

st.markdown('''
<div class="signal-strip">
    <span><span class="signal-dot"></span> Control engine ready</span>
    <span>Data source • DuckDB</span>
    <span>Exception queue • active</span>
    <span>Review workflow • operational</span>
</div>
''', unsafe_allow_html=True)

# ============================================================
# KPI GRID
# ============================================================
st.markdown(f'''
<div class="kpi-grid">
    <div class="card red">
        <div class="icon">🚨</div>
        <div class="label">Total Exceptions</div>
        <div class="value">{total:,}</div>
    </div>
    <div class="card orange">
        <div class="icon">🔓</div>
        <div class="label">Open Exceptions</div>
        <div class="value">{open_count:,}</div>
    </div>
    <div class="card green">
        <div class="icon">✅</div>
        <div class="label">Reviewed</div>
        <div class="value">{reviewed:,}</div>
    </div>
    <div class="card blue">
        <div class="icon">👁️</div>
        <div class="label">Monitor</div>
        <div class="value">{monitor:,}</div>
    </div>
    <div class="card pink">
        <div class="icon">🔴</div>
        <div class="label">High Severity</div>
        <div class="value">{high:,}</div>
    </div>
    <div class="card cyan">
        <div class="icon">💰</div>
        <div class="label">Financial Impact</div>
        <div class="value">{money(impact)}</div>
    </div>
    <div class="card purple">
        <div class="icon">👥</div>
        <div class="label">Affected Customers</div>
        <div class="value">{customers:,}</div>
    </div>
    <div class="card yellow">
        <div class="icon">📌</div>
        <div class="label">Average Impact / Exception</div>
        <div class="value">{money(impact/total if total else 0)}</div>
    </div>
</div>
''', unsafe_allow_html=True)

# ============================================================
# TABS
# ============================================================
overview, analysis, operations, investigation = st.tabs([
    "📊 Exception Overview",
    "🔍 Exception Analysis",
    "📋 Operations Queue",
    "🧠 Investigation"
])

# ------------------------------------------------------------
# TAB 1: EXCEPTION OVERVIEW
# ------------------------------------------------------------
with overview:
    st.markdown('<div class="section-header">Exception Priority</div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    
    with a:
        severity_data = exceptions.severity.value_counts().rename_axis("severity").reset_index(name="exceptions")
        st.plotly_chart(
            style(px.bar(
                severity_data, x="severity", y="exceptions", 
                color="severity", template="plotly_dark", 
                title="Exceptions by Severity"
            )), 
            use_container_width=True
        )
    
    with b:
        status_data = exceptions.status.value_counts().rename_axis("status").reset_index(name="exceptions")
        st.plotly_chart(
            style(px.pie(
                status_data, names="status", values="exceptions", 
                hole=.55, template="plotly_dark", 
                title="Exceptions by Status"
            )), 
            use_container_width=True
        )
    
    with c:
        data = exceptions.groupby("control_id", as_index=False).financial_impact.sum()
        st.plotly_chart(
            style(px.bar(
                data, x="control_id", y="financial_impact", 
                text_auto=".2s", template="plotly_dark", 
                title="Financial Impact by Control"
            )), 
            use_container_width=True
        )

# ------------------------------------------------------------
# TAB 2: EXCEPTION ANALYSIS
# ------------------------------------------------------------
with analysis:
    st.markdown('<div class="section-header">Control and Financial Analysis</div>', unsafe_allow_html=True)
    
    data = exceptions.groupby(["control_id", "control_name"], as_index=False).agg(
        control_hits=("exception_id", "size"),
        financial_impact=("financial_impact", "sum")
    )
    st.dataframe(
        data.assign(financial_impact=data.financial_impact.map(money)),
        use_container_width=True,
        hide_index=True
    )
    
    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            style(px.bar(
                data, x="control_id", y="control_hits", 
                text_auto=True, template="plotly_dark", 
                title="Control Activity"
            )), 
            use_container_width=True
        )
    
    with right:
        st.plotly_chart(
            style(px.bar(
                data, x="control_id", y="financial_impact", 
                text_auto=".2s", template="plotly_dark", 
                title="Financial Exposure"
            )), 
            use_container_width=True
        )
    
    st.info("Investigation priority is a dashboard view only: Critical = HIGH + OPEN; High = HIGH + MONITOR; Medium = MEDIUM + OPEN/MONITOR; Low = LOW or REVIEWED.")

# ------------------------------------------------------------
# TAB 3: OPERATIONS QUEUE
# ------------------------------------------------------------
with operations:
    st.markdown('<div class="section-header">Operational Exception Queue</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        control = st.selectbox("Control", ["All"] + sorted(exceptions.control_id.unique()))
    with c2:
        severity = st.selectbox("Severity", ["All"] + sorted(exceptions.severity.unique()))
    with c3:
        status = st.selectbox("Status", ["All"] + sorted(exceptions.status.unique()))
    
    filtered = exceptions.copy()
    if control != "All":
        filtered = filtered[filtered.control_id == control]
    if severity != "All":
        filtered = filtered[filtered.severity == severity]
    if status != "All":
        filtered = filtered[filtered.status == status]
    
    filtered = filtered.assign(
        _rank=filtered.priority.map({"Critical": 0, "High": 1, "Medium": 2, "Low": 3})
    ).sort_values(["_rank", "financial_impact"], ascending=[True, False])
    
    if filtered.empty:
        st.info("No exceptions match the current filters.")
    else:
        cols = [c for c in [
            "exception_id", "priority", "control_id", "control_name", 
            "customer_id", "financial_impact", "severity", "status", "exception_date"
        ] if c in filtered]
        table = filtered[cols].copy()
        table["financial_impact"] = table.financial_impact.map(money)
        st.dataframe(table, use_container_width=True, hide_index=True, height=430)

# ------------------------------------------------------------
# TAB 4: INVESTIGATION
# ------------------------------------------------------------
with investigation:
    st.markdown('<div class="section-header">Exception Investigation</div>', unsafe_allow_html=True)
    
    selected_id = st.selectbox(
        "Select Exception",
        exceptions.exception_id.tolist(),
        format_func=lambda x: f"EXC-{int(x):03d}"
    )
    selected = exceptions[exceptions.exception_id == selected_id].iloc[0]
    
    a, b = st.columns(2)
    with a:
        st.markdown(f'''
        <div class="info-card">
            <h4>📄 Exception</h4>
            <p>
                Control: <strong>{html.escape(str(selected.control_id))}</strong><br>
                Customer: <strong>{html.escape(str(selected.customer_id))}</strong><br>
                Severity: <strong>{selected.severity}</strong><br>
                Status: <strong>{selected.status}</strong>
            </p>
        </div>
        ''', unsafe_allow_html=True)
    
    with b:
        st.markdown(f'''
        <div class="info-card">
            <h4>💰 Financial and Guidance</h4>
            <p>
                Impact: <strong>{money(selected.financial_impact)}</strong><br><br>
                {html.escape(str(selected.description))}
            </p>
        </div>
        ''', unsafe_allow_html=True)
    
    st.info("Review the exception evidence and supporting customer records before taking action. This is an investigation suggestion, not an automatic conclusion.")

# ============================================================
# FOOTER
# ============================================================
st.markdown('''
<div style="text-align:center; color:#64748b; padding:30px 24px; font-size:.82rem; border-top: 1px solid rgba(255,255,255,0.05); margin-top: 40px;">
    <strong>Billing Assurance & Revenue Protection Control Tower</strong><br>
    Financial impact represents control-identified impact requiring investigation and is not confirmed revenue loss.
</div>
''', unsafe_allow_html=True)