from utils.ui import (
    DECISION_COLORS,
    inject_styles,
    money,
    render_footer,
    render_sidebar,
    style_chart,
)
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
    st.info("No discount requests are available to display.")
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
    "Overview",
    "Decision Economics",
    "Decision Queue",
    "Investigation"
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
            style_chart(px.pie(
                decision_data, names="decision", values="requests", 
                color="decision", color_discrete_map=DECISION_COLORS,
                hole=.58, template="plotly_dark",
                title="Observed Decision Distribution"
            )), 
            width="stretch"
        )
    
    with b:
        data = pd.DataFrame({
            "metric": ["Discount Cost", "Expected Retention Value", "Net Economic Impact"],
            "value": [cost, retention, net]
        })
        st.plotly_chart(
            style_chart(px.bar(
                data, x="metric", y="value", 
                text_auto=".2s", template="plotly_dark", 
                title="Discount Economics"
            )), 
            width="stretch"
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
        style_chart(px.bar(
            rules, x="decision_rule", y="requests", 
            text="requests", template="plotly_dark", 
            title="Observed Decision Rules"
        )), 
        width="stretch"
    )
    
    st.markdown('<div class="section-header">Customer Value Tiers</div>', unsafe_allow_html=True)
    tiers = filtered.groupby(["value_tier", "decision"], as_index=False).size().rename(columns={"size": "requests"})
    st.plotly_chart(
        style_chart(px.bar(
            tiers, x="value_tier", y="requests", color="decision", 
            color_discrete_map=DECISION_COLORS,
            barmode="stack", text_auto=True, template="plotly_dark",
            title="Decision Distribution by Value Tier"
        )), 
        width="stretch"
    )
    
    st.markdown('<div class="section-header">Economic Decision Profile</div>', unsafe_allow_html=True)
    fig = px.scatter(
        filtered, x="discount_cost", y="estimated_retention_value", 
        color="decision", color_discrete_map=DECISION_COLORS,
        hover_data=["request_id", "customer_id", "requested_discount_pct", "value_tier", "benefit_cost_ratio"], 
        template="plotly_dark", 
        title="Discount Cost versus Estimated Retention Value"
    )
    maxv = max(float(filtered.discount_cost.max()), float(filtered.estimated_retention_value.max()))
    fig.add_trace(go.Scatter(
        x=[0, maxv], y=[0, maxv], mode="lines", 
        name="Break-even reference", line=dict(dash="dash")
    ))
    st.plotly_chart(style_chart(fig, 420), width="stretch")

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
    
    st.dataframe(table, width="stretch", hide_index=True, height=450)

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

render_footer("Retention value is modeled and is not guaranteed realized revenue or customer retention.")