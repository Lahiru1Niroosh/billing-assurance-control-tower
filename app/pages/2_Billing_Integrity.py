from utils.ui import inject_styles, money, render_footer, render_sidebar, style_chart
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
    st.info("No billing control performance is available to display.")
    st.stop()

hits = int(controls.control_hits.sum())
control_customer_hits = int(controls.unique_customers.sum())
impact = float(controls.financial_impact.sum())


def value(control_id, column):
    return controls.loc[controls.control_id == control_id, column].sum()


rate_hits = int(value("C003", "control_hits"))
duplicate_records = int(value("C001", "duplicate_records_involved"))
duplicate_cases = int(value("C001", "duplicate_customer_cases"))
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
        <div class="label">Billing Exception Records</div>
        <div class="value">{hits:,}</div>
    </div>
    <div class="card purple">
        <div class="icon">👥</div>
        <div class="label">Affected Customers (by Control)</div>
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
        <div class="label">Duplicate Records Involved</div>
        <div class="value">{duplicate_records:,}</div>
        <small>{duplicate_cases:,} duplicate customer cases</small>
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

st.caption(
    "Affected Customers (by Control) sums customer counts across controls. "
    f"C001 involves {duplicate_records:,} billing records across "
    f"{duplicate_cases:,} duplicate customer cases; both records in each case are retained."
)

# ============================================================
# TABS
# ============================================================
overview, analysis, queue_tab, investigation = st.tabs([
    "Overview",
    "Control Analysis",
    "Exception Queue",
    "Investigation"
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
            text="control_hits", title="Billing Exception Records by Control",
            template="plotly_dark"
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(style_chart(fig), width="stretch")
    
    with right:
        fig = px.bar(
            controls, x="control_id", y="financial_impact", 
            text="financial_impact", title="Financial Impact by Billing Control", 
            template="plotly_dark"
        )
        fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        fig.update_layout(yaxis_tickprefix="$")
        st.plotly_chart(style_chart(fig), width="stretch")
    
    st.markdown('<div class="section-header">Control Mix</div>', unsafe_allow_html=True)
    fig = px.pie(
        controls, names="control_id", values="control_hits",
        hole=.58, title="Billing Exception Record Distribution",
        template="plotly_dark"
    )
    fig.update_traces(textinfo="label+percent")
    st.plotly_chart(style_chart(fig, 380), width="stretch")

# ------------------------------------------------------------
# TAB 2: CONTROL ANALYSIS
# ------------------------------------------------------------
with analysis:
    st.markdown('<div class="section-header">Billing Control Assessment</div>', unsafe_allow_html=True)
    definitions = [
        ("🔁 Duplicate Billing", f"C001 retained <strong>{duplicate_records:,} duplicate records involved</strong> across <strong>{duplicate_cases:,} duplicate customer cases</strong>. Both records per case are retained for investigation."),
        ("❌ Missing / Zero Billing", f"C002 identified <strong>{missing_hits:,} exception records</strong> using the validated tenure and active-service eligibility rules. Validate billing completeness and service activity."),
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
    st.dataframe(display, width="stretch", hide_index=True)
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
        st.dataframe(table, width="stretch", hide_index=True, height=430)

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

render_footer("C001 preserves both records for investigation. Control exposure is not confirmed revenue loss.")