import html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from utils.database import run_query

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Discount Decision Command Center",
    page_icon="💼",
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
            radial-gradient(circle at 10% 10%, rgba(34, 197, 94, 0.14), transparent 35%),
            radial-gradient(circle at 90% 15%, rgba(59, 130, 246, 0.14), transparent 35%),
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
        0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }
        100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
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
        background: linear-gradient(135deg, rgba(6, 95, 70, 0.5), rgba(30, 64, 175, 0.35), rgba(8, 145, 178, 0.2));
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
        background: rgba(34, 197, 94, 0.25);
        filter: blur(50px);
        animation: floatOrb 8s ease-in-out infinite;
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 250px; height: 250px;
        left: -100px; bottom: -130px;
        border-radius: 50%;
        background: rgba(59, 130, 246, 0.2);
        filter: blur(50px);
        animation: floatOrb 10s ease-in-out infinite reverse;
    }

    .hero-content { position: relative; z-index: 2; }

    .hero h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #ffffff, #86efac, #93c5fd);
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
        color: #bbf7d0;
        background: rgba(34, 197, 94, 0.13);
        border: 1px solid rgba(74, 222, 128, 0.4);
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
        border-color: rgba(134, 239, 172, 0.4);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4), 0 0 20px rgba(34, 197, 94, 0.15);
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
    .card.green::after { background: #22c55e; }
    .card.blue::after { background: #3b82f6; }
    .card.cyan::after { background: #06b6d4; }
    .card.orange::after { background: #f97316; }
    .card.red::after { background: #ef4444; }
    .card.yellow::after { background: #eab308; }
    .card.purple::after { background: #a855f7; }
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
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.25), rgba(59, 130, 246, 0.15));
        color: #ffffff;
        box-shadow: 0 4px 15px rgba(34, 197, 94, 0.2);
        border: 1px solid rgba(134, 239, 172, 0.25);
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
        border-color: rgba(134, 239, 172, 0.3);
    }

    .info-card h4 {
        margin: 0 0 14px 0;
        color: #86efac;
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
       SELECT BOX & TEXT INPUT
    ------------------------------------------------------- */
    .stSelectbox [data-baseweb="select"] > div,
    .stTextInput input {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        color: #e2e8f0;
    }

    .stSelectbox [data-baseweb="select"] > div:hover,
    .stTextInput input:hover {
        border-color: rgba(134, 239, 172, 0.4);
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
</style>
""", unsafe_allow_html=True)


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def card(icon, label, value, accent="green"):
    return f'''
    <div class="card {accent}">
        <div class="icon">{icon}</div>
        <div class="label">{label}</div>
        <div class="value">{value}</div>
    </div>
    '''


def money(v):
    return f"${float(v):,.2f}"


def style(fig, h=360):
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
except Exception as error:
    st.error(f"Unable to load discount decisions: {error}")
    st.stop()

if requests.empty:
    st.error("Discount decision data is unavailable from DuckDB.")
    st.stop()


def values(column):
    return sorted(requests[column].dropna().astype(str).unique())


# ============================================================
# HERO SECTION
# ============================================================
st.markdown('''
<div class="hero">
    <div class="hero-content">
        <h1>Discount Decision Command Center</h1>
        <p>Customer retention • Discount governance • Economic impact • Approval control</p>
        <span class="badge">● DISCOUNT GOVERNANCE ACTIVE</span>
    </div>
</div>
''', unsafe_allow_html=True)

st.markdown('''
<div class="signal-strip">
    <span><span class="signal-dot"></span> Decision engine ready</span>
    <span>Data source • DuckDB</span>
    <span>Governance workflow • active</span>
    <span>Approval model • operating</span>
</div>
''', unsafe_allow_html=True)


# ============================================================
# FILTERS
# ============================================================
def apply_filters():
    with st.container(border=True):
        a, b, c = st.columns(3)
        with a:
            decision = st.selectbox("Decision", ["All"] + values("decision"), key="decision_filter")
        with b:
            tier = st.selectbox("Value Tier", ["All"] + values("value_tier"), key="tier_filter")
        with c:
            approval = st.selectbox("Approval Level", ["All"] + values("approval_level"), key="approval_filter")
        d, e = st.columns(2)
        with d:
            month = st.selectbox("Request Month", ["All"] + values("request_month"), key="month_filter")
        with e:
            customer = st.text_input("Customer ID", key="decision_customer")
    
    result = requests.copy()
    if decision != "All":
        result = result[result.decision == decision]
    if tier != "All":
        result = result[result.value_tier == tier]
    if approval != "All":
        result = result[result.approval_level == approval]
    if month != "All":
        result = result[result.request_month == month]
    if customer.strip():
        result = result[result.customer_id.astype(str).str.contains(customer.strip(), case=False, na=False)]
    return result


filtered = apply_filters()

# Extract Metrics
total = len(filtered)
auto = int((filtered.decision == "AUTO_APPROVE").sum())
review = int((filtered.decision == "MANAGER_REVIEW").sum())
decline = int((filtered.decision == "DECLINE").sum())
cost = filtered.discount_cost.sum()
retention = filtered.estimated_retention_value.sum()
net = filtered.net_economic_impact.sum()
bcr = filtered.benefit_cost_ratio.mean() if total else 0

# ============================================================
# KPI GRID
# ============================================================
st.markdown(f'''
<div class="kpi-grid">
    <div class="card blue">
        <div class="icon">📥</div>
        <div class="label">Total Requests</div>
        <div class="value">{total:,}</div>
    </div>
    <div class="card green">
        <div class="icon">✅</div>
        <div class="label">Auto Approved</div>
        <div class="value">{auto:,}</div>
    </div>
    <div class="card yellow">
        <div class="icon">👤</div>
        <div class="label">Manager Review</div>
        <div class="value">{review:,}</div>
    </div>
    <div class="card red">
        <div class="icon">🔴</div>
        <div class="label">Declined</div>
        <div class="value">{decline:,}</div>
    </div>
    <div class="card orange">
        <div class="icon">💸</div>
        <div class="label">Discount Cost</div>
        <div class="value">{money(cost)}</div>
    </div>
    <div class="card cyan">
        <div class="icon">📈</div>
        <div class="label">Expected Retention Value</div>
        <div class="value">{money(retention)}</div>
    </div>
    <div class="card purple">
        <div class="icon">⚖️</div>
        <div class="label">Net Economic Impact</div>
        <div class="value">{money(net)}</div>
    </div>
    <div class="card pink">
        <div class="icon">📊</div>
        <div class="label">Average Benefit / Cost</div>
        <div class="value">{bcr:.2f}x</div>
    </div>
</div>
''', unsafe_allow_html=True)

if filtered.empty:
    st.warning("No discount requests match the current filters.")
    st.stop()

# ============================================================
# TABS
# ============================================================
overview, economics_tab, queue, investigation = st.tabs([
    "📊 Decision Overview",
    "📈 Economics",
    "📋 Decision Queue",
    "🧠 Investigation"
])

# ------------------------------------------------------------
# TAB 1: DECISION OVERVIEW
# ------------------------------------------------------------
with overview:
    st.markdown('<div class="section-header">Decision Landscape</div>', unsafe_allow_html=True)
    a, b = st.columns(2)
    
    with a:
        decision_data = filtered.decision.value_counts().rename_axis("decision").reset_index(name="requests")
        st.plotly_chart(
            style(px.pie(
                decision_data, names="decision", values="requests", 
                hole=.58, template="plotly_dark", 
                title="Observed Decision Distribution"
            )), 
            use_container_width=True
        )
    
    with b:
        data = pd.DataFrame({
            "metric": ["Discount Cost", "Expected Retention Value", "Net Economic Impact"],
            "value": [cost, retention, net]
        })
        st.plotly_chart(
            style(px.bar(
                data, x="metric", y="value", 
                text_auto=".2s", template="plotly_dark", 
                title="Discount Economics"
            )), 
            use_container_width=True
        )
    
    st.markdown('''
    <div class="info-card">
        <h4>💡 Economic Decision Framework</h4>
        <p>Customer Value → Retention Uplift → Expected Retention Value → compare against Discount Cost → economic decision.</p>
        <small>Estimated retention value is model-derived and is not guaranteed realized revenue or retention.</small>
    </div>
    ''', unsafe_allow_html=True)

# ------------------------------------------------------------
# TAB 2: ECONOMICS
# ------------------------------------------------------------
with economics_tab:
    st.markdown('<div class="section-header">Decision Rule Analysis</div>', unsafe_allow_html=True)
    rules = filtered.decision_rule.value_counts().rename_axis("decision_rule").reset_index(name="requests")
    st.plotly_chart(
        style(px.bar(
            rules, x="decision_rule", y="requests", 
            text="requests", template="plotly_dark", 
            title="Observed Decision Rules"
        )), 
        use_container_width=True
    )
    
    st.markdown('<div class="section-header">Customer Value Tiers</div>', unsafe_allow_html=True)
    tiers = filtered.groupby(["value_tier", "decision"], as_index=False).size().rename(columns={"size": "requests"})
    st.plotly_chart(
        style(px.bar(
            tiers, x="value_tier", y="requests", color="decision", 
            barmode="stack", text_auto=True, template="plotly_dark", 
            title="Decision Distribution by Value Tier"
        )), 
        use_container_width=True
    )
    
    st.markdown('<div class="section-header">Economic Decision Profile</div>', unsafe_allow_html=True)
    fig = px.scatter(
        filtered, x="discount_cost", y="estimated_retention_value", 
        color="decision", 
        hover_data=["request_id", "customer_id", "requested_discount_pct", "value_tier", "benefit_cost_ratio"], 
        template="plotly_dark", 
        title="Discount Cost versus Estimated Retention Value"
    )
    maxv = max(float(filtered.discount_cost.max()), float(filtered.estimated_retention_value.max()))
    fig.add_trace(go.Scatter(
        x=[0, maxv], y=[0, maxv], mode="lines", 
        name="Break-even reference", line=dict(dash="dash")
    ))
    st.plotly_chart(style(fig, 420), use_container_width=True)

# ------------------------------------------------------------
# TAB 3: DECISION QUEUE
# ------------------------------------------------------------
with queue:
    st.markdown('<div class="section-header">Discount Decision Queue</div>', unsafe_allow_html=True)
    order = {"DECLINE": 0, "MANAGER_REVIEW": 1, "AUTO_APPROVE": 2}
    data = filtered.assign(
        _order=filtered.decision.map(order)
    ).sort_values(["_order", "net_economic_impact"])
    
    cols = [c for c in [
        "request_id", "customer_id", "request_date", "requested_discount_pct", 
        "customer_value", "discount_cost", "estimated_retention_value", 
        "net_economic_impact", "benefit_cost_ratio", "value_tier", 
        "decision", "approval_level", "decision_reason", "sla_status"
    ] if c in data]
    
    table = data[cols].copy()
    for c in ["customer_value", "discount_cost", "estimated_retention_value", "net_economic_impact"]:
        if c in table:
            table[c] = table[c].map(money)
    
    st.dataframe(table, use_container_width=True, hide_index=True, height=450)

# ------------------------------------------------------------
# TAB 4: INVESTIGATION
# ------------------------------------------------------------
with investigation:
    st.markdown('<div class="section-header">Decision Investigation</div>', unsafe_allow_html=True)
    selected_id = st.selectbox("Select Request", filtered.request_id.tolist())
    selected = filtered[filtered.request_id == selected_id].iloc[0]
    
    a, b = st.columns(2)
    with a:
        st.json({c: safe(selected[c]) for c in [
            "request_id", "customer_id", "request_date", 
            "requested_discount_pct", "current_monthly_charge", 
            "customer_value", "value_tier"
        ] if c in selected})
    
    with b:
        st.json({c: safe(selected[c]) for c in [
            "discount_cost", "estimated_retention_value", "net_economic_impact", 
            "benefit_cost_ratio", "decision", "decision_rule", 
            "approval_level", "decision_reason", "sla_target_hours", 
            "turnaround_hours", "sla_status", "breach_hours"
        ] if c in selected})
    
    st.markdown('''
    <div class="info-card">
        <h4>📋 Decision Model Assumptions</h4>
        <p>Customer value, retention uplift, retention value and benefit-cost ratio are model-derived inputs. Discount cost is calculated from the request. Results are synthetic/project data and estimated retention value is not guaranteed realized revenue.</p>
    </div>
    ''', unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown('''
<div style="text-align:center; color:#64748b; padding:30px 24px; font-size:.82rem; border-top: 1px solid rgba(255,255,255,0.05); margin-top: 40px;">
    <strong>Billing Assurance & Revenue Protection Control Tower</strong><br>
    Discount Governance • DuckDB • Python • Streamlit • Plotly
</div>
''', unsafe_allow_html=True)