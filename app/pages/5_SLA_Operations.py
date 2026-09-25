import html
import pandas as pd
import plotly.express as px
import streamlit as st
from utils.database import run_query

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="SLA Operations Command Center",
    page_icon="⏱️",
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
            radial-gradient(circle at 90% 15%, rgba(168, 85, 247, 0.14), transparent 35%),
            radial-gradient(circle at 50% 90%, rgba(6, 182, 212, 0.1), transparent 40%),
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
        background: linear-gradient(135deg, rgba(3, 105, 161, 0.5), rgba(126, 34, 206, 0.3), rgba(8, 145, 178, 0.2));
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
        background: rgba(168, 85, 247, 0.2);
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
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.25), rgba(168, 85, 247, 0.15));
        color: #ffffff;
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.2);
        border: 1px solid rgba(125, 211, 252, 0.25);
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

    .info-card small {
        color: #64748b;
        display: block;
        margin-top: 10px;
        font-size: 0.8rem;
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
       FILTER CONTAINER
    ------------------------------------------------------- */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 20px;
        margin-bottom: 25px;
        backdrop-filter: blur(10px);
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
       SELECT BOX, MULTISELECT & TEXT INPUT
    ------------------------------------------------------- */
    .stSelectbox [data-baseweb="select"] > div,
    .stMultiSelect [data-baseweb="select"] > div,
    .stTextInput input,
    .stNumberInput input {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        color: #e2e8f0;
    }

    .stSelectbox [data-baseweb="select"] > div:hover,
    .stMultiSelect [data-baseweb="select"] > div:hover,
    .stTextInput input:hover,
    .stNumberInput input:hover {
        border-color: rgba(125, 211, 252, 0.4);
    }

    .stMultiSelect [data-baseweb="tag"] {
        background: rgba(14, 165, 233, 0.2);
        border: 1px solid rgba(56, 189, 248, 0.3);
        color: #bae6fd;
        border-radius: 8px;
    }

    /* -------------------------------------------------------
       JSON VIEWER
    ------------------------------------------------------- */
    .stJson {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.08);
        background: rgba(255, 255, 255, 0.02);
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
</style>
""", unsafe_allow_html=True)


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def card(icon, label, value, accent="cyan"):
    return f'''
    <div class="card {accent}">
        <div class="icon">{icon}</div>
        <div class="label">{label}</div>
        <div class="value">{value}</div>
    </div>
    '''


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


def safe(v):
    return html.escape(str(v))


# ============================================================
# DATA LOADING
# ============================================================
try:
    requests = run_query("SELECT * FROM staging.discount_decisions_sla")
    source_kpis = run_query("SELECT * FROM controls.v_sla_kpis")
except Exception as error:
    st.error(f"Unable to load SLA data: {error}")
    st.stop()

if requests.empty:
    st.error("No SLA records are available from DuckDB.")
    st.stop()

requests["request_date"] = pd.to_datetime(requests.request_date)
requests["breach_hours"] = pd.to_numeric(requests.breach_hours, errors="coerce").fillna(0)
requests["turnaround_hours"] = pd.to_numeric(requests.turnaround_hours, errors="coerce")


# ============================================================
# FILTERS
# ============================================================
def apply_filters():
    with st.container(border=True):
        a, b, c = st.columns(3)
        with a:
            status = st.multiselect("SLA Status", sorted(requests.sla_status.unique()), key="sla_status")
        with b:
            approval = st.multiselect("Approval Level", sorted(requests.approval_level.unique()), key="sla_approval")
        with c:
            month = st.multiselect("Request Month", sorted(requests.request_month.unique()), key="sla_month")
        d, e = st.columns(2)
        with d:
            customer = st.text_input("Customer ID", key="sla_customer")
        with e:
            minimum = st.number_input("Minimum Breach Hours", min_value=0.0, value=0.0, step=.25, key="sla_minimum")
    
    result = requests.copy()
    if status:
        result = result[result.sla_status.isin(status)]
    if approval:
        result = result[result.approval_level.isin(approval)]
    if month:
        result = result[result.request_month.isin(month)]
    if customer.strip():
        result = result[result.customer_id.astype(str).str.contains(customer.strip(), case=False, na=False)]
    return result[result.breach_hours >= minimum]


# ============================================================
# HERO SECTION
# ============================================================
st.markdown('''
<div class="hero">
    <div class="hero-content">
        <h1>SLA Operations Command Center</h1>
        <p>Decision turnaround • SLA compliance • Breach monitoring • Operational workload</p>
        <span class="badge">● SLA MONITORING ACTIVE</span>
    </div>
</div>
''', unsafe_allow_html=True)

st.markdown('''
<div class="signal-strip">
    <span><span class="signal-dot"></span> SLA monitoring active</span>
    <span>Data source • DuckDB</span>
    <span>Review queue • live</span>
    <span>Operational cadence • tracked</span>
</div>
''', unsafe_allow_html=True)


# ============================================================
# KPI GRID
# ============================================================
filtered = apply_filters()

# Extract Metrics
total = len(filtered)
met = int((filtered.sla_status == "Met").sum())
risk = int((filtered.sla_status == "At Risk").sum())
breached = int((filtered.sla_status == "Breached").sum())
compliance = met / total * 100 if total else 0
avg = filtered.turnaround_hours.mean() if total else 0
review = filtered[filtered.approval_level != "System"].turnaround_hours.mean() if not filtered[filtered.approval_level != "System"].empty else 0
hours = filtered.breach_hours.sum()

st.markdown(f'''
<div class="kpi-grid">
    <div class="card blue">
        <div class="icon">📥</div>
        <div class="label">Total Requests</div>
        <div class="value">{total:,}</div>
    </div>
    <div class="card green">
        <div class="icon">◉</div>
        <div class="label">SLA Compliance</div>
        <div class="value">{compliance:.2f}%</div>
    </div>
    <div class="card cyan">
        <div class="icon">✓</div>
        <div class="label">SLA Met</div>
        <div class="value">{met:,}</div>
    </div>
    <div class="card orange">
        <div class="icon">⚠</div>
        <div class="label">At Risk</div>
        <div class="value">{risk:,}</div>
    </div>
    <div class="card red">
        <div class="icon">⛔</div>
        <div class="label">Breached</div>
        <div class="value">{breached:,}</div>
    </div>
    <div class="card purple">
        <div class="icon">◷</div>
        <div class="label">Average Turnaround</div>
        <div class="value">{avg:.2f} h</div>
    </div>
    <div class="card pink">
        <div class="icon">◷</div>
        <div class="label">Average Review Turnaround</div>
        <div class="value">{review:.2f} h</div>
    </div>
    <div class="card yellow">
        <div class="icon">⌛</div>
        <div class="label">Total Breach Hours</div>
        <div class="value">{hours:.2f} h</div>
    </div>
</div>
''', unsafe_allow_html=True)


# ============================================================
# TABS
# ============================================================
overview, performance, operations, investigation = st.tabs([
    "📊 SLA Overview",
    "📈 Performance",
    "📋 Operations",
    "🧠 Investigation"
])

# ------------------------------------------------------------
# TAB 1: SLA OVERVIEW
# ------------------------------------------------------------
with overview:
    st.markdown('<div class="section-header">SLA Performance Overview</div>', unsafe_allow_html=True)
    a, b = st.columns(2)
    
    with a:
        st.plotly_chart(
            style(px.pie(
                pd.DataFrame({
                    "status": ["Met", "At Risk", "Breached"],
                    "requests": [met, risk, breached]
                }),
                names="status", values="requests", hole=.6, 
                template="plotly_dark", title="SLA Status Distribution"
            )), 
            use_container_width=True
        )
    
    with b:
        st.markdown(f'''
        <div class="info-card">
            <h4>📊 Operational Summary</h4>
            <p>
                Total Requests: <strong>{total:,}</strong><br>
                SLA Met: <strong>{met:,}</strong><br>
                At Risk: <strong>{risk:,}</strong><br>
                Breached: <strong>{breached:,}</strong><br>
                Compliance: <strong>{compliance:.2f}%</strong><br>
                Breach Hours: <strong>{hours:.2f}</strong>
            </p>
            <small>Performance uses recorded turnaround against each request target.</small>
        </div>
        ''', unsafe_allow_html=True)

# ------------------------------------------------------------
# TAB 2: PERFORMANCE
# ------------------------------------------------------------
with performance:
    st.markdown('<div class="section-header">SLA Performance by Approval Level</div>', unsafe_allow_html=True)
    if total:
        grouped = filtered.groupby("approval_level", as_index=False).agg(
            requests=("request_id", "size"),
            met=("sla_status", lambda x: (x == "Met").sum()),
            at_risk=("sla_status", lambda x: (x == "At Risk").sum()),
            breached=("sla_status", lambda x: (x == "Breached").sum()),
            avg_turnaround=("turnaround_hours", "mean"),
            target=("sla_target_hours", "mean"),
            breach_hours=("breach_hours", "sum")
        )
        grouped["compliance_pct"] = grouped.met / grouped.requests * 100
        
        a, b = st.columns(2)
        with a:
            st.plotly_chart(
                style(px.bar(
                    grouped, x="compliance_pct", y="approval_level", 
                    orientation="h", text="compliance_pct", 
                    template="plotly_dark", title="Compliance by Approval Level"
                )), 
                use_container_width=True
            )
        with b:
            st.dataframe(grouped, use_container_width=True, hide_index=True)
        
        a, b = st.columns(2)
        with a:
            st.plotly_chart(
                style(px.histogram(
                    filtered, x="turnaround_hours", color="sla_status", 
                    template="plotly_dark", title="Decision Turnaround Distribution"
                )), 
                use_container_width=True
            )
        with b:
            st.plotly_chart(
                style(px.bar(
                    grouped, x="approval_level", y=["target", "avg_turnaround"], 
                    barmode="group", template="plotly_dark", 
                    title="SLA Target vs Actual"
                )), 
                use_container_width=True
            )
        
        monthly = filtered.groupby("request_month", as_index=False).agg(
            requests=("request_id", "size"),
            met=("sla_status", lambda x: (x == "Met").sum()),
            breached=("sla_status", lambda x: (x == "Breached").sum())
        )
        monthly["compliance_pct"] = monthly.met / monthly.requests * 100
        
        a, b = st.columns(2)
        with a:
            st.plotly_chart(
                style(px.line(
                    monthly, x="request_month", y="compliance_pct", 
                    markers=True, template="plotly_dark", 
                    title="Monthly SLA Compliance"
                )), 
                use_container_width=True
            )
        with b:
            st.plotly_chart(
                style(px.bar(
                    monthly, x="request_month", y="breached", 
                    text_auto=True, template="plotly_dark", 
                    title="Breaches by Month"
                )), 
                use_container_width=True
            )

# ------------------------------------------------------------
# TAB 3: OPERATIONS
# ------------------------------------------------------------
with operations:
    st.markdown('<div class="section-header">Operational Workload vs SLA</div>', unsafe_allow_html=True)
    st.plotly_chart(
        style(px.scatter(
            filtered, x="daily_review_load", y="turnaround_hours", 
            color="sla_status", 
            hover_data=["request_id", "approval_level", "sla_target_hours", "breach_hours"], 
            template="plotly_dark", 
            title="Observed Workload and Turnaround Relationship"
        )), 
        use_container_width=True
    )
    
    st.markdown('<div class="section-header">SLA Exception Queue</div>', unsafe_allow_html=True)
    queue = filtered[filtered.sla_status.isin(["Breached", "At Risk"])].sort_values(
        ["breach_hours", "turnaround_hours"], ascending=False
    )
    cols = [c for c in [
        "request_id", "customer_id", "request_date", "request_month", 
        "decision", "approval_level", "value_tier", "requested_discount_pct", 
        "turnaround_hours", "sla_target_hours", "breach_hours", "sla_status", 
        "daily_review_load", "decision_reason"
    ] if c in queue]
    st.dataframe(queue[cols], use_container_width=True, hide_index=True, height=430)

# ------------------------------------------------------------
# TAB 4: INVESTIGATION
# ------------------------------------------------------------
with investigation:
    st.markdown('<div class="section-header">SLA Investigation</div>', unsafe_allow_html=True)
    queue = filtered[filtered.sla_status.isin(["Breached", "At Risk"])].sort_values(
        ["breach_hours", "turnaround_hours"], ascending=False
    )
    
    if queue.empty:
        st.info("Select filters that return an SLA exception to open the investigation view.")
    else:
        sid = st.selectbox("Select Request", queue.request_id.tolist())
        selected = queue[queue.request_id == sid].iloc[0]
        st.json({c: safe(selected[c]) for c in [
            "request_id", "customer_id", "decision", "approval_level", 
            "value_tier", "requested_discount_pct", "decision_timestamp", 
            "turnaround_hours", "sla_target_hours", "sla_status", 
            "breach_hours", "daily_review_load", "decision_reason"
        ] if c in selected})
        
        gap = float(selected.turnaround_hours - selected.sla_target_hours)
        st.info(
            f"Recorded turnaround exceeded the assigned SLA target by {gap:.2f} hours." 
            if selected.sla_status == "Breached" 
            else "Request remains within the recorded SLA process but is approaching the defined threshold."
        )
    
    st.markdown('''
    <div class="info-card">
        <h4>🧠 Management View</h4>
        <p>Review breached approval queues, investigate recurring approval-level delays, monitor high daily-review-load periods and review requests approaching SLA thresholds.</p>
    </div>
    ''', unsafe_allow_html=True)
    
    with st.expander("How SLA is calculated"):
        st.write("SLA Status uses recorded turnaround_hours compared with each request's sla_target_hours. Breached means turnaround exceeds target; At Risk uses the existing dataset definition; Met means completed within SLA. This dashboard monitors timing and does not prove root cause. Project data is synthetic/analytical.")

# ============================================================
# FOOTER
# ============================================================
st.markdown('''
<div style="text-align:center; color:#64748b; padding:30px 24px; font-size:.82rem; border-top: 1px solid rgba(255,255,255,0.05); margin-top: 40px;">
    <strong>Billing Assurance & Revenue Protection Control Tower</strong><br>
    SLA metrics are recorded/modelled project data and do not independently establish root cause.
</div>
''', unsafe_allow_html=True)