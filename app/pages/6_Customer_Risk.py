import html
import pandas as pd
import plotly.express as px
import streamlit as st
from utils.database import run_query

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Customer Risk & Exposure Command Center",
    page_icon="👥",
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
        0% { box-shadow: 0 0 0 0 rgba(168, 85, 247, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(168, 85, 247, 0); }
        100% { box-shadow: 0 0 0 0 rgba(168, 85, 247, 0); }
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
        background: linear-gradient(135deg, rgba(3, 105, 161, 0.48), rgba(126, 34, 206, 0.32), rgba(8, 145, 178, 0.2));
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
        background: rgba(168, 85, 247, 0.22);
        filter: blur(50px);
        animation: floatOrb 10s ease-in-out infinite reverse;
    }

    .hero-content { position: relative; z-index: 2; }

    .hero h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #ffffff, #c4b5fd, #7dd3fc);
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
        color: #ddd6fe;
        background: rgba(168, 85, 247, 0.14);
        border: 1px solid rgba(192, 132, 252, 0.4);
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
        border-color: rgba(196, 181, 253, 0.4);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4), 0 0 20px rgba(168, 85, 247, 0.15);
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
    .card.purple::after { background: #a855f7; }
    .card.cyan::after { background: #06b6d4; }
    .card.blue::after { background: #3b82f6; }
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
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.25), rgba(14, 165, 233, 0.15));
        color: #ffffff;
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.2);
        border: 1px solid rgba(196, 181, 253, 0.25);
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
        border-color: rgba(196, 181, 253, 0.3);
    }

    .info-card h4 {
        margin: 0 0 14px 0;
        color: #c4b5fd;
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
    .stTextInput input {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        color: #e2e8f0;
    }

    .stSelectbox [data-baseweb="select"] > div:hover,
    .stMultiSelect [data-baseweb="select"] > div:hover,
    .stTextInput input:hover {
        border-color: rgba(196, 181, 253, 0.4);
    }

    .stMultiSelect [data-baseweb="tag"] {
        background: rgba(168, 85, 247, 0.2);
        border: 1px solid rgba(192, 132, 252, 0.3);
        color: #ddd6fe;
        border-radius: 8px;
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
def card(icon, label, value, accent="purple"):
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
    if row.high_severity_hits > 0 and row.open_exceptions > 0:
        return "Critical Attention"
    if row.high_severity_hits > 0 and row.monitor_exceptions > 0:
        return "High Attention"
    if row.open_exceptions > 0 and row.risk_band == "MEDIUM":
        return "Medium Attention"
    return "Lower Attention"


def safe(v):
    return html.escape(str(v))


# ============================================================
# DATA LOADING
# ============================================================
try:
    risk = run_query("SELECT * FROM controls.v_customer_risk")
    exceptions = run_query("SELECT * FROM controls.v_exception_queue")
except Exception as error:
    st.error(f"Unable to load customer-risk data: {error}")
    st.stop()

if risk.empty or exceptions.empty:
    st.error("No customer-risk or exception data is available from DuckDB.")
    st.stop()

risk = risk.rename(columns={"customer_risk": "risk_band"})
exceptions["financial_impact"] = pd.to_numeric(exceptions.financial_impact, errors="coerce").fillna(0)

base = exceptions.groupby("customer_id", as_index=False).agg(
    control_hits=("exception_id", "size"),
    controls_involved=("control_id", "nunique"),
    financial_impact=("financial_impact", "sum"),
    high_severity_hits=("severity", lambda x: (x == "HIGH").sum()),
    open_exceptions=("status", lambda x: (x == "OPEN").sum()),
    reviewed_exceptions=("status", lambda x: (x == "REVIEWED").sum()),
    monitor_exceptions=("status", lambda x: (x == "MONITOR").sum())
)

rank = exceptions.assign(
    _rank=exceptions.severity.map({"HIGH": 3, "MEDIUM": 2, "LOW": 1})
).groupby("customer_id")["_rank"].max().map({3: "HIGH", 2: "MEDIUM", 1: "LOW"}).rename("highest_severity")

customers = base.merge(risk[["customer_id", "risk_band"]], on="customer_id", how="left").merge(rank, on="customer_id", how="left")
customers["risk_band"] = customers.risk_band.fillna("LOW")
customers["highest_severity"] = customers.highest_severity.fillna("LOW")
customers["priority"] = customers.apply(priority, axis=1)


# ============================================================
# HERO SECTION
# ============================================================
st.markdown('''
<div class="hero">
    <div class="hero-content">
        <h1>Customer Risk & Exposure Command Center</h1>
        <p>Customer-level control exposure • Financial impact • Exception concentration • Investigation priority</p>
        <span class="badge">● CUSTOMER RISK MONITORING ACTIVE</span>
    </div>
</div>
''', unsafe_allow_html=True)

st.markdown('''
<div class="signal-strip">
    <span><span class="signal-dot"></span> Risk monitoring active</span>
    <span>Data source • DuckDB</span>
    <span>Exposure model • live</span>
    <span>Investigation queue • prioritized</span>
</div>
''', unsafe_allow_html=True)


# ============================================================
# KPI GRID
# ============================================================
unique = len(customers)
hits = len(exceptions)
impact = exceptions.financial_impact.sum()
high = int((customers.risk_band == "HIGH").sum())
medium = int((customers.risk_band == "MEDIUM").sum())
low = int((customers.risk_band == "LOW").sum())

st.markdown(f'''
<div class="kpi-grid">
    <div class="card purple">
        <div class="icon">👥</div>
        <div class="label">Unique Customers</div>
        <div class="value">{unique:,}</div>
    </div>
    <div class="card cyan">
        <div class="icon">🛡️</div>
        <div class="label">Total Control Hits</div>
        <div class="value">{hits:,}</div>
    </div>
    <div class="card red">
        <div class="icon">🔴</div>
        <div class="label">High-Risk Customers</div>
        <div class="value">{high:,}</div>
    </div>
    <div class="card orange">
        <div class="icon">🟡</div>
        <div class="label">Medium-Risk Customers</div>
        <div class="value">{medium:,}</div>
    </div>
    <div class="card green">
        <div class="icon">🟢</div>
        <div class="label">Low-Risk Customers</div>
        <div class="value">{low:,}</div>
    </div>
    <div class="card blue">
        <div class="icon">💰</div>
        <div class="label">Financial Impact</div>
        <div class="value">{money(impact)}</div>
    </div>
    <div class="card pink">
        <div class="icon">📌</div>
        <div class="label">Average Impact / Customer</div>
        <div class="value">{money(impact/unique)}</div>
    </div>
    <div class="card yellow">
        <div class="icon">📊</div>
        <div class="label">Average Control Hits / Customer</div>
        <div class="value">{hits/unique:.2f}</div>
    </div>
</div>
''', unsafe_allow_html=True)


# ============================================================
# TABS
# ============================================================
overview, exposure, investigation, management = st.tabs([
    "📊 Risk Overview",
    "📈 Exposure Analysis",
    "🧠 Customer Investigation",
    "💼 Management"
])

profile = customers.groupby("risk_band", as_index=False).agg(
    customers=("customer_id", "nunique"),
    control_hits=("control_hits", "sum"),
    financial_impact=("financial_impact", "sum")
)
profile["order"] = profile.risk_band.map({"HIGH": 0, "MEDIUM": 1, "LOW": 2})
profile = profile.sort_values("order")

# ------------------------------------------------------------
# TAB 1: RISK OVERVIEW
# ------------------------------------------------------------
with overview:
    st.markdown('<div class="section-header">Customer Risk Distribution</div>', unsafe_allow_html=True)
    a, b = st.columns(2)
    
    with a:
        st.plotly_chart(
            style(px.pie(
                profile, names="risk_band", values="customers", 
                hole=.6, template="plotly_dark", 
                title="Customers by Control Exposure Risk Band"
            )), 
            use_container_width=True
        )
    
    with b:
        st.plotly_chart(
            style(px.bar(
                profile, x="risk_band", y="financial_impact", 
                text_auto=".2s", template="plotly_dark", 
                title="Financial Impact by Risk Band"
            )), 
            use_container_width=True
        )
    
    profile["impact_per_customer"] = profile.financial_impact / profile.customers
    profile["hits_per_customer"] = profile.control_hits / profile.customers
    
    profile_table = profile.rename(columns={
        "risk_band": "Risk Band",
        "customers": "Customers",
        "control_hits": "Control Hits",
        "financial_impact": "Financial Impact",
        "impact_per_customer": "Impact / Customer",
        "hits_per_customer": "Hits / Customer"
    })
    profile_table["Financial Impact"] = profile_table["Financial Impact"].map(money)
    st.dataframe(profile_table, use_container_width=True, hide_index=True)

# ------------------------------------------------------------
# TAB 2: EXPOSURE ANALYSIS
# ------------------------------------------------------------
with exposure:
    st.markdown('<div class="section-header">Customer Financial Exposure</div>', unsafe_allow_html=True)
    top_n = st.selectbox("Top Customers", [5, 10, 15, 25], index=1)
    top = customers.nlargest(top_n, "financial_impact")
    
    st.plotly_chart(
        style(px.bar(
            top.sort_values("financial_impact"), 
            x="financial_impact", y="customer_id", 
            orientation="h", color="risk_band", 
            hover_data=["control_hits", "controls_involved", "open_exceptions"], 
            template="plotly_dark", 
            title="Highest Observed Customer Exposure"
        ), 420), 
        use_container_width=True
    )
    
    a, b = st.columns(2)
    with a:
        st.plotly_chart(
            style(px.scatter(
                customers, x="control_hits", y="financial_impact", 
                color="risk_band", 
                hover_data=["customer_id", "controls_involved", "highest_severity"], 
                template="plotly_dark", 
                title="Control Concentration"
            )), 
            use_container_width=True
        )
    
    with b:
        mix = exceptions.groupby("control_id", as_index=False).agg(
            control_hits=("exception_id", "size"),
            financial_impact=("financial_impact", "sum")
        )
        st.plotly_chart(
            style(px.bar(
                mix, x="control_id", y="financial_impact", 
                text_auto=".2s", template="plotly_dark", 
                title="Exposure by Control"
            )), 
            use_container_width=True
        )

# ------------------------------------------------------------
# TAB 3: CUSTOMER INVESTIGATION
# ------------------------------------------------------------
with investigation:
    st.markdown('<div class="section-header">Customer Risk Filters and Queue</div>', unsafe_allow_html=True)
    
    a, b, c = st.columns(3)
    with a:
        bands = st.multiselect("Risk Band", sorted(customers.risk_band.unique()))
    with b:
        controls = st.multiselect("Control ID", sorted(exceptions.control_id.unique()))
    with c:
        search = st.text_input("Customer ID")
    
    filtered = customers.copy()
    filtered_events = exceptions.copy()
    
    if bands:
        filtered = filtered[filtered.risk_band.isin(bands)]
    if controls:
        filtered_events = filtered_events[filtered_events.control_id.isin(controls)]
    if search.strip():
        filtered = filtered[filtered.customer_id.str.contains(search.strip(), case=False, na=False)]
    
    filtered = filtered[filtered.customer_id.isin(filtered_events.customer_id)]
    filtered = filtered.sort_values(
        ["priority", "financial_impact"],
        key=lambda s: s.map({"Critical Attention": 0, "High Attention": 1, "Medium Attention": 2, "Lower Attention": 3}) if s.name == "priority" else -s,
        ascending=True
    )
    
    if filtered.empty:
        st.info("No customers match the selected filters.")
    else:
        table = filtered[[
            "customer_id", "risk_band", "control_hits", "controls_involved", 
            "financial_impact", "high_severity_hits", "open_exceptions", 
            "reviewed_exceptions", "monitor_exceptions", "highest_severity", "priority"
        ]].copy()
        table["financial_impact"] = table.financial_impact.map(money)
        st.dataframe(table, use_container_width=True, hide_index=True, height=420)
        
        selected_id = st.selectbox("Select Customer", filtered.customer_id.tolist())
        selected = filtered[filtered.customer_id == selected_id].iloc[0]
        
        st.markdown(f'''
        <div class="info-card">
            <h4>🔍 Customer Investigation</h4>
            <p>
                Customer: <strong>{safe(selected.customer_id)}</strong><br>
                Risk Band: <strong>{selected.risk_band}</strong><br>
                Financial Impact: <strong>{money(selected.financial_impact)}</strong><br>
                Control Hits: <strong>{int(selected.control_hits)}</strong><br>
                Open Exceptions: <strong>{int(selected.open_exceptions)}</strong><br>
                Priority: <strong>{selected.priority}</strong>
            </p>
        </div>
        ''', unsafe_allow_html=True)
        
        events = exceptions[exceptions.customer_id == selected_id]
        activity = events.groupby(["control_id", "control_name"], as_index=False).agg(
            control_hits=("exception_id", "size"),
            financial_impact=("financial_impact", "sum"),
            status=("status", lambda x: ", ".join(sorted(set(x))))
        )
        activity["financial_impact"] = activity.financial_impact.map(money)
        st.dataframe(activity, use_container_width=True, hide_index=True)

# ------------------------------------------------------------
# TAB 4: MANAGEMENT
# ------------------------------------------------------------
with management:
    st.markdown('<div class="section-header">High-Risk Customer Watchlist</div>', unsafe_allow_html=True)
    highrisk = customers[customers.risk_band == "HIGH"].sort_values("financial_impact", ascending=False)
    
    if not highrisk.empty:
        st.dataframe(
            highrisk[[
                "customer_id", "control_hits", "financial_impact", 
                "open_exceptions", "highest_severity", "priority"
            ]].assign(financial_impact=lambda x: x.financial_impact.map(money)),
            use_container_width=True, hide_index=True, height=380
        )
    else:
        st.info("No high-risk customers are present.")
    
    st.markdown('''
    <div class="info-card">
        <h4>💼 Management View</h4>
        <p>Investigate high-exposure customers, review recurring control activity, trace exposure to specific controls, and review open high-severity exceptions. Control hits are not the same as unique customers.</p>
    </div>
    ''', unsafe_allow_html=True)
    
    with st.expander("How Customer Risk Is Defined"):
        st.write("Risk bands use the existing customer-risk aggregation based on observed control activity. They are not a credit score, fraud score, churn prediction or customer-value rating.")
    
    with st.expander("Data & Metric Notes"):
        st.write("Data is synthetic/project data. Financial impact is modeled or recorded control exposure, not confirmed revenue loss. Investigation priority is a presentation aid, not a new control rule.")

# ============================================================
# FOOTER
# ============================================================
st.markdown('''
<div style="text-align:center; color:#64748b; padding:30px 24px; font-size:.82rem; border-top: 1px solid rgba(255,255,255,0.05); margin-top: 40px;">
    <strong>Billing Assurance & Revenue Protection Control Tower</strong><br>
    Financial impact represents control-identified exposure requiring investigation, not confirmed realized revenue loss.
</div>
''', unsafe_allow_html=True)