import streamlit as st

from utils.database import get_executive_kpis, get_sla_kpis, run_query
from utils.ui import (
    inject_styles,
    metric_card,
    money,
    page_heading,
    page_links,
    render_sidebar,
    render_footer,
)

st.set_page_config(
    page_title="Billing Assurance Control Tower",
    page_icon="B",
    layout="wide",
    initial_sidebar_state="auto",
)

inject_styles()
render_sidebar()

try:
    executive = get_executive_kpis()
    sla = get_sla_kpis()
    active_controls = int(
        run_query(
            "SELECT COUNT(DISTINCT control_id) AS active_controls "
            "FROM controls.business_control_matrix WHERE status = 'Active'"
        ).iloc[0]["active_controls"]
    )
    c001 = run_query(
        """
        SELECT
            COALESCE(SUM(duplicate_records_involved), 0) AS duplicate_records_involved,
            COALESCE(SUM(duplicate_customer_cases), 0) AS duplicate_customer_cases
        FROM controls.v_control_performance
        WHERE control_id = 'C001'
        """
    ).iloc[0]
except Exception as error:
    st.error(f"Unable to load control tower data from DuckDB: {error}")
    st.stop()

if executive.empty or sla.empty:
    st.error("DuckDB did not return the required executive and SLA KPI rows.")
    st.stop()

kpi = executive.iloc[0]
sla_kpi = sla.iloc[0]
duplicate_records = int(c001["duplicate_records_involved"])
duplicate_cases = int(c001["duplicate_customer_cases"])

page_heading(
    "REVENUE ASSURANCE · OPERATIONS",
    "Billing Assurance & Revenue Protection",
    "A unified command center for billing controls, financial exposure, discount governance and operational service levels.",
)

st.markdown(
    f"""
    <section class="hero">
      <div class="hero-content">
        <div class="ba-eyebrow">CONTROL ENVIRONMENT · LIVE</div>
        <h1>See the signal. Prioritize the work.</h1>
        <p>Trace billing data from validation through investigation and management action, with DuckDB as the analytical source of truth.</p>
        <div class="landing-status">
          <span class="status-pill"><span class="signal-dot"></span> Warehouse online</span>
          <span class="status-pill">{active_controls} active controls</span>
          <span class="status-pill">Operational reporting ready</span>
        </div>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="kpi-grid landing-kpis">
      {metric_card("Exception Records", f'{int(kpi["control_hits"]):,}', "Control-generated records", "blue")}
      {metric_card("Affected Customers", f'{int(kpi["unique_customers"]):,}', "Across the control queue", "cyan")}
      {metric_card("Gross Control Exposure", money(kpi["financial_impact"], compact=True), "Under review · not confirmed loss", "violet")}
      {metric_card("Open Exceptions", f'{int(kpi["open_exceptions"]):,}', "Require operational action", "amber")}
      {metric_card("High Severity", f'{int(kpi["high_severity_exceptions"]):,}', "Across active exception records", "red")}
      {metric_card("SLA Met Rate", f'{float(sla_kpi["sla_met_rate_pct"]):.1f}%', "Requests completed within target", "green")}
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-header">Control-to-action workflow</div>
    <div class="workflow-rail">
      <span>Data</span><b>›</b><span>Validation</span><b>›</b><span>Controls</span><b>›</b>
      <span>Exceptions</span><b>›</b><span>Exposure</span><b>›</b><span>Decisions</span><b>›</b>
      <span>SLA</span><b>›</b><span>Management action</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-header">Workspaces</div>', unsafe_allow_html=True)
st.caption("Open a focused workspace for executive review, control analysis or operational investigation.")

modules = page_links()
module_descriptions = {
    "Executive Control Tower": "A concise view of portfolio exposure, control performance and operational posture.",
    "Billing Integrity": "Investigate duplicate records, missing billing totals and rate anomalies.",
    "Exception Management": "Triage, filter and review the enterprise exception queue.",
    "Discount Decisions": "Review deterministic approval decisions and their economic trade-offs.",
    "SLA Operations": "Monitor request turnaround, service targets and breach workload.",
    "Customer Exposure": "Understand observed customer-level control exposure and concentration.",
}
for start in range(0, len(modules), 3):
    columns = st.columns(3, gap="medium")
    for column, (number, title, path, icon) in zip(columns, modules[start : start + 3]):
        with column:
            st.markdown(
                f"""
                <div class="module-card">
                  <div class="module-number">WORKSPACE {number}</div>
                  <div class="module-title">{title}</div>
                  <div class="module-description">{module_descriptions[title]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.page_link(path, label=f"Open {title}", icon=icon)

st.caption(
    "Control exposure is an investigation measure, not confirmed revenue loss. "
    f"C001's {duplicate_records:,} records represent {duplicate_cases:,} duplicate customer cases; "
    "SLA breach hours are tracked separately from financial exposure."
)
render_footer(
    f"C001 retains {duplicate_records:,} billing records across "
    f"{duplicate_cases:,} duplicate customer cases for investigation."
)
