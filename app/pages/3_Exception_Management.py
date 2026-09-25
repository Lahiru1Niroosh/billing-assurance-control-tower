from utils.ui import (
    SEVERITY_COLORS,
    STATUS_COLORS,
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
    page_title="Exception Management Center",
    page_icon="🚨",
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
    st.info("No exceptions are currently available for prioritization.")
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
    "Overview",
    "Priority Analysis",
    "Operations Queue",
    "Investigation"
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
            style_chart(px.bar(
                severity_data, x="severity", y="exceptions", 
                color="severity", color_discrete_map=SEVERITY_COLORS,
                template="plotly_dark",
                title="Exceptions by Severity"
            )), 
            width="stretch"
        )
    
    with b:
        status_data = exceptions.status.value_counts().rename_axis("status").reset_index(name="exceptions")
        st.plotly_chart(
            style_chart(px.pie(
                status_data, names="status", values="exceptions", 
                color="status", color_discrete_map=STATUS_COLORS,
                hole=.55, template="plotly_dark",
                title="Exceptions by Status"
            )), 
            width="stretch"
        )
    
    with c:
        data = exceptions.groupby("control_id", as_index=False).financial_impact.sum()
        st.plotly_chart(
            style_chart(px.bar(
                data, x="control_id", y="financial_impact", 
                text_auto=".2s", template="plotly_dark", 
                title="Financial Impact by Control"
            )), 
            width="stretch"
        )

# ------------------------------------------------------------
# TAB 2: EXCEPTION ANALYSIS
# ------------------------------------------------------------
with analysis:
    st.markdown('<div class="section-header">Control and Financial Analysis</div>', unsafe_allow_html=True)
    
    data = exceptions.groupby(["control_id", "control_name"], as_index=False).agg(
        exception_records=("exception_id", "size"),
        financial_impact=("financial_impact", "sum")
    )
    st.dataframe(
        data.assign(financial_impact=data.financial_impact.map(money)),
        width="stretch",
        hide_index=True
    )
    duplicate_records = int(
        data.loc[data.control_id == "C001", "exception_records"].sum()
    )
    c001_customers = int(
        exceptions.loc[exceptions.control_id == "C001", "customer_id"].nunique()
    )
    st.caption(
        f"C001 includes {duplicate_records:,} duplicate records involved across "
        f"{c001_customers:,} duplicate customer cases, not independent cases."
    )
    
    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            style_chart(px.bar(
                data, x="control_id", y="exception_records",
                text_auto=True, template="plotly_dark",
                title="Exception Records by Control"
            )), 
            width="stretch"
        )
    
    with right:
        st.plotly_chart(
            style_chart(px.bar(
                data, x="control_id", y="financial_impact", 
                text_auto=".2s", template="plotly_dark", 
                title="Financial Exposure"
            )), 
            width="stretch"
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
        st.dataframe(table, width="stretch", hide_index=True, height=430)

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

render_footer("Control-identified exposure requires investigation and is not confirmed revenue loss.")