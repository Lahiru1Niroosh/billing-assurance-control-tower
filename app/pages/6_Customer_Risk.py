from utils.ui import (
    RISK_COLORS,
    inject_styles,
    money,
    render_footer,
    render_sidebar,
    style_chart,
)
import html
import pandas as pd
import plotly.express as px
import streamlit as st
from utils.database import run_query

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Customer Exposure Command Center",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="auto"
)

inject_styles()
render_sidebar()

# ============================================================
# NEXT-LEVEL CSS & ANIMATIONS
# ============================================================
# ============================================================
# HELPER FUNCTIONS
# ============================================================
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
    st.info("No customer exposure data is available to display.")
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
        <h1>Customer Exposure & Investigation</h1>
        <p>Observed control activity • Financial exposure • Exception concentration • Investigation priority</p>
        <span class="badge">● EXPOSURE MONITORING ACTIVE</span>
    </div>
</div>
''', unsafe_allow_html=True)

st.markdown('''
<div class="signal-strip">
    <span><span class="signal-dot"></span> Observed exposure monitoring</span>
    <span>Data source • DuckDB</span>
    <span>Exposure aggregation • live</span>
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
    "Overview",
    "Exposure Analysis",
    "Investigation Queue",
    "Management View"
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
            style_chart(px.pie(
                profile, names="risk_band", values="customers", 
                color="risk_band", color_discrete_map=RISK_COLORS,
                hole=.6, template="plotly_dark",
                title="Customers by Control Exposure Risk Band"
            )), 
            width="stretch"
        )
    
    with b:
        st.plotly_chart(
            style_chart(px.bar(
                profile, x="risk_band", y="financial_impact", 
                color="risk_band", color_discrete_map=RISK_COLORS,
                text_auto=".2s", template="plotly_dark",
                title="Financial Impact by Risk Band"
            )), 
            width="stretch"
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
    st.dataframe(profile_table, width="stretch", hide_index=True)

# ------------------------------------------------------------
# TAB 2: EXPOSURE ANALYSIS
# ------------------------------------------------------------
with exposure:
    st.markdown('<div class="section-header">Customer Financial Exposure</div>', unsafe_allow_html=True)
    top_n = st.selectbox("Top Customers", [5, 10, 15, 25], index=1)
    top = customers.nlargest(top_n, "financial_impact")
    
    st.plotly_chart(
        style_chart(px.bar(
            top.sort_values("financial_impact"), 
            x="financial_impact", y="customer_id", 
            orientation="h", color="risk_band", color_discrete_map=RISK_COLORS,
            hover_data=["control_hits", "controls_involved", "open_exceptions"], 
            template="plotly_dark", 
            title="Highest Observed Customer Exposure"
        ), 420), 
        width="stretch"
    )
    
    a, b = st.columns(2)
    with a:
        st.plotly_chart(
            style_chart(px.scatter(
                customers, x="control_hits", y="financial_impact", 
                color="risk_band", color_discrete_map=RISK_COLORS,
                hover_data=["customer_id", "controls_involved", "highest_severity"], 
                template="plotly_dark", 
                title="Control Concentration"
            )), 
            width="stretch"
        )
    
    with b:
        mix = exceptions.groupby("control_id", as_index=False).agg(
            control_hits=("exception_id", "size"),
            financial_impact=("financial_impact", "sum")
        )
        st.plotly_chart(
            style_chart(px.bar(
                mix, x="control_id", y="financial_impact", 
                text_auto=".2s", template="plotly_dark", 
                title="Exposure by Control"
            )), 
            width="stretch"
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
        st.dataframe(table, width="stretch", hide_index=True, height=420)
        
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
        st.dataframe(activity, width="stretch", hide_index=True)

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
            width="stretch", hide_index=True, height=380
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

render_footer("Exposure bands summarize observed control activity and are not predictive customer scores.")