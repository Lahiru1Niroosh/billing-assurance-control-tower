from utils.ui import (
    SEVERITY_COLORS,
    inject_styles,
    money,
    render_footer,
    render_sidebar,
    style_chart,
)
import pandas as pd
import plotly.express as px
import streamlit as st
from utils.database import get_control_performance, get_executive_kpis, get_sla_kpis

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Executive Control Tower",
    page_icon="🚀",
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
    kpi_df = get_executive_kpis()
    control_df = get_control_performance()
    sla_df = get_sla_kpis()
except Exception as error: 
    st.error(f"Unable to load executive data: {error}")
    st.stop()

if kpi_df.empty: 
    st.error("Executive KPI data is unavailable.")
    st.stop()

# Extract Data
k = kpi_df.iloc[0]
control_hits = int(k.control_hits)
customers = int(k.unique_customers)
impact = float(k.financial_impact)
duplicate_records = int(k.duplicate_records_involved)
duplicate_cases = int(k.duplicate_customer_cases)
open_count = int(k.open_exceptions)
high = int(k.high_severity_exceptions)
medium = int(k.medium_severity_exceptions)
low = int(k.low_severity_exceptions)
met_rate = float(sla_df.iloc[0].sla_met_rate_pct) if not sla_df.empty else 0
non_breach_rate = float(sla_df.iloc[0].non_breach_rate_pct) if not sla_df.empty else 0

# ============================================================
# HERO SECTION
# ============================================================
st.markdown('''
<div class="hero">
    <div class="hero-content">
        <h1>Billing Assurance Control Tower</h1>
        <p>Revenue protection • Billing integrity • Discount governance • SLA operations</p>
        <span class="badge">● CONTROL ENVIRONMENT ACTIVE</span>
    </div>
</div>
''', unsafe_allow_html=True)

st.markdown('''
<div class="signal-strip">
    <span><span class="signal-dot"></span> Control engine ready</span>
    <span>Data source • DuckDB</span>
    <span>Control hits • live</span>
    <span>Operational status • monitoring</span>
</div>
''', unsafe_allow_html=True)

# ============================================================
# KPI GRID
# ============================================================
st.markdown(f'''
<div class="kpi-grid">
    <div class="card blue">
        <div class="icon">🛡️</div>
        <div class="label">Control Hits</div>
        <div class="value">{control_hits:,}</div>
    </div>
    <div class="card purple">
        <div class="icon">👥</div>
        <div class="label">Unique Customers</div>
        <div class="value">{customers:,}</div>
    </div>
    <div class="card cyan">
        <div class="icon">💰</div>
        <div class="label">Financial Impact</div>
        <div class="value">{money(impact)}</div>
    </div>
    <div class="card orange">
        <div class="icon">🚨</div>
        <div class="label">Open Exceptions</div>
        <div class="value">{open_count:,}</div>
    </div>
    <div class="card red">
        <div class="icon">🔴</div>
        <div class="label">High Severity</div>
        <div class="value">{high:,}</div>
    </div>
    <div class="card yellow">
        <div class="icon">🟡</div>
        <div class="label">Medium Severity</div>
        <div class="value">{medium:,}</div>
    </div>
    <div class="card green">
        <div class="icon">🟢</div>
        <div class="label">Low Severity</div>
        <div class="value">{low:,}</div>
    </div>
    <div class="card pink">
        <div class="icon">⏱️</div>
        <div class="label">SLA Met Rate</div>
        <div class="value">{met_rate:.1f}%</div>
    </div>
</div>
''', unsafe_allow_html=True)

# ============================================================
# TABS
# ============================================================
overview, performance, financial, management = st.tabs([
    "Overview",
    "Control Performance",
    "Financial Exposure",
    "Management Brief"
])

# ------------------------------------------------------------
# TAB 1: EXECUTIVE VIEW
# ------------------------------------------------------------
with overview:
    st.markdown('<div class="section-header">Control Intelligence</div>', unsafe_allow_html=True)
    a, b = st.columns(2)
    
    with a: 
        st.plotly_chart(
            style_chart(px.bar(
                control_df, x="control_id", y="control_hits", 
                text="control_hits", template="plotly_dark", 
                title="Control Activity"
            )), 
            width="stretch"
        )
    
    with b: 
        st.plotly_chart(
            style_chart(px.pie(
                pd.DataFrame({"severity":["HIGH","MEDIUM","LOW"], "exceptions":[high,medium,low]}),
                names="severity", values="exceptions", color="severity",
                color_discrete_map=SEVERITY_COLORS, hole=.58,
                template="plotly_dark", title="Exception Severity"
            )), 
            width="stretch"
        )
    
    st.markdown('''
    <div class="info-card">
        <h4>📝 Executive Interpretation</h4>
        <p>Control activity shows where exceptions are generated. Severity distribution shows the current exception profile, while SLA met rate provides the primary operational monitoring visibility.</p>
    </div>
    ''', unsafe_allow_html=True)

# ------------------------------------------------------------
# TAB 2: CONTROL PERFORMANCE
# ------------------------------------------------------------
with performance:
    st.markdown('<div class="section-header">Control Performance Detail</div>', unsafe_allow_html=True)
    
    detail = control_df.copy()
    detail["financial_impact"] = detail.financial_impact.map(money)
    st.dataframe(detail, width="stretch", hide_index=True)
    st.caption(
        f"C001: {duplicate_records:,} duplicate records involved across "
        f"{duplicate_cases:,} duplicate customer cases; both billing records "
        "in each case are retained for investigation."
    )
    
    st.plotly_chart(
        style_chart(px.bar(
            control_df, x="control_id", y="control_hits", 
            color="control_name", template="plotly_dark", 
            title="Control Hits by Control"
        )), 
        width="stretch"
    )

# ------------------------------------------------------------
# TAB 3: FINANCIAL EXPOSURE
# ------------------------------------------------------------
with financial:
    st.markdown('<div class="section-header">Financial Impact by Control</div>', unsafe_allow_html=True)
    
    fig = px.bar(
        control_df, x="control_id", y="financial_impact", 
        text="financial_impact", template="plotly_dark", 
        title="Identified Financial Impact"
    )
    fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    fig.update_layout(yaxis_tickprefix="$")
    st.plotly_chart(style_chart(fig, 420), width="stretch")
    
    st.markdown(f'''
    <div class="info-card">
        <h4>💡 Financial Exposure</h4>
        <p>Total identified impact: <strong>{money(impact)}</strong><br>
        Financial impact represents control-identified impact requiring investigation and is not confirmed revenue loss.</p>
    </div>
    ''', unsafe_allow_html=True)

# ------------------------------------------------------------
# TAB 4: MANAGEMENT VIEW
# ------------------------------------------------------------
with management:
    a, b, c = st.columns(3)
    
    with a: 
        st.markdown(f'''
        <div class="info-card">
            <h4>🚨 Exception Position</h4>
            <p><strong>{open_count:,}</strong> exceptions are currently open.<br>
            High severity: <strong>{high:,}</strong></p>
        </div>
        ''', unsafe_allow_html=True)
    
    with b: 
        st.markdown(f'''
        <div class="info-card">
            <h4>💰 Financial Position</h4>
            <p>Controls identify <strong>{money(impact)}</strong> requiring investigation or operational decision-making.</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with c: 
        st.markdown(f'''
        <div class="info-card">
            <h4>⏱️ Operational Position</h4>
            <p>Current SLA met rate is <strong>{met_rate:.1f}%</strong>; non-breach rate is <strong>{non_breach_rate:.1f}%</strong>.</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with st.expander("⚠️ Important caveat"): 
        st.write("Financial impact represents control-identified impact, not confirmed revenue loss.")

render_footer("Control-identified exposure requires investigation and is not confirmed revenue loss.")