from utils.ui import (
    SLA_STATUS_COLORS,
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
    page_title="SLA Operations Command Center",
    page_icon="⏱️",
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
    st.error(f"Unable to load SLA data: {error}")
    st.stop()

if requests.empty:
    st.info("No SLA records are available to display.")
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
        <p>Decision turnaround • SLA met rate • non-breach monitoring • operational workload</p>
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
met_rate = met / total * 100 if total else 0
non_breach_rate = (met + risk) / total * 100 if total else 0
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
        <div class="label">SLA Met Rate</div>
        <div class="value">{met_rate:.2f}%</div>
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
    "Overview",
    "Performance Analysis",
    "Operations Queue",
    "Investigation"
])

# ------------------------------------------------------------
# TAB 1: SLA OVERVIEW
# ------------------------------------------------------------
with overview:
    st.markdown('<div class="section-header">SLA Performance Overview</div>', unsafe_allow_html=True)
    a, b = st.columns(2)
    
    with a:
        st.plotly_chart(
            style_chart(px.pie(
                pd.DataFrame({
                    "status": ["Met", "At Risk", "Breached"],
                    "requests": [met, risk, breached]
                }),
                names="status", values="requests", hole=.6, 
                color="status", color_discrete_map=SLA_STATUS_COLORS,
                template="plotly_dark", title="SLA Status Distribution"
            )), 
            width="stretch"
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
                SLA Met Rate: <strong>{met_rate:.2f}%</strong><br>
                Non-Breach Rate: <strong>{non_breach_rate:.2f}%</strong><br>
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
        grouped["met_rate_pct"] = grouped.met / grouped.requests * 100
        grouped["non_breach_rate_pct"] = (
            (grouped.met + grouped.at_risk) / grouped.requests * 100
        )
        
        a, b = st.columns(2)
        with a:
            st.plotly_chart(
                style_chart(px.bar(
                    grouped, x="met_rate_pct", y="approval_level",
                    orientation="h", text="met_rate_pct",
                    template="plotly_dark", title="SLA Met Rate by Approval Level"
                )), 
                width="stretch"
            )
        with b:
            st.dataframe(grouped, width="stretch", hide_index=True)
        
        a, b = st.columns(2)
        with a:
            st.plotly_chart(
                style_chart(px.histogram(
                    filtered, x="turnaround_hours", color="sla_status", 
                    color_discrete_map=SLA_STATUS_COLORS,
                    template="plotly_dark", title="Decision Turnaround Distribution"
                )), 
                width="stretch"
            )
        with b:
            st.plotly_chart(
                style_chart(px.bar(
                    grouped, x="approval_level", y=["target", "avg_turnaround"], 
                    barmode="group", template="plotly_dark", 
                    title="SLA Target vs Actual"
                )), 
                width="stretch"
            )
        
        monthly = filtered.groupby("request_month", as_index=False).agg(
            requests=("request_id", "size"),
            met=("sla_status", lambda x: (x == "Met").sum()),
            at_risk=("sla_status", lambda x: (x == "At Risk").sum()),
            breached=("sla_status", lambda x: (x == "Breached").sum())
        )
        monthly["met_rate_pct"] = monthly.met / monthly.requests * 100
        monthly["non_breach_rate_pct"] = (
            (monthly.met + monthly.at_risk) / monthly.requests * 100
        )
        
        a, b = st.columns(2)
        with a:
            st.plotly_chart(
                style_chart(px.line(
                    monthly, x="request_month", y="met_rate_pct",
                    markers=True, template="plotly_dark", 
                    title="Monthly SLA Met Rate"
                )), 
                width="stretch"
            )
        with b:
            st.plotly_chart(
                style_chart(px.bar(
                    monthly, x="request_month", y="breached", 
                    text_auto=True, template="plotly_dark", 
                    title="Breaches by Month"
                )), 
                width="stretch"
            )

# ------------------------------------------------------------
# TAB 3: OPERATIONS
# ------------------------------------------------------------
with operations:
    st.markdown('<div class="section-header">Operational Workload vs SLA</div>', unsafe_allow_html=True)
    st.plotly_chart(
        style_chart(px.scatter(
            filtered, x="daily_review_load", y="turnaround_hours", 
            color="sla_status", 
            color_discrete_map=SLA_STATUS_COLORS,
            hover_data=["request_id", "approval_level", "sla_target_hours", "breach_hours"], 
            template="plotly_dark", 
            title="Observed Workload and Turnaround Relationship"
        )), 
        width="stretch"
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
    st.dataframe(queue[cols], width="stretch", hide_index=True, height=430)

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

render_footer("Breach hours measure SLA target overrun and are separate from financial exposure.")