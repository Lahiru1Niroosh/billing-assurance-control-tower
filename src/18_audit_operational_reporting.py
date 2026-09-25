import duckdb
from pathlib import Path
from datetime import datetime

# ============================================================
# PHASE 4.6 — AUDIT TRAIL & OPERATIONAL REPORTING
# Billing Assurance & Revenue Protection Control Tower
# ============================================================

DB_PATH = Path("data/warehouse/billing_assurance.duckdb")

con = duckdb.connect(str(DB_PATH))

print("=" * 70)
print("PHASE 4.6 — AUDIT TRAIL & OPERATIONAL REPORTING")
print("=" * 70)

# ------------------------------------------------------------
# 1. AUDIT TABLE
# ------------------------------------------------------------

con.execute("""
CREATE TABLE IF NOT EXISTS core.control_execution_audit (
    audit_id BIGINT,
    run_timestamp TIMESTAMP,
    control_id VARCHAR,
    control_name VARCHAR,
    control_type VARCHAR,
    execution_status VARCHAR,
    exception_count BIGINT,
    unique_customers BIGINT,
    financial_impact DOUBLE,
    notes VARCHAR
)
""")

# ------------------------------------------------------------
# 2. GENERATE AUDIT RUN ID
# ------------------------------------------------------------

run_timestamp = datetime.now()
run_id = int(run_timestamp.strftime("%Y%m%d%H%M%S"))

# ------------------------------------------------------------
# 3. CAPTURE CONTROL EXECUTION RESULTS
# ------------------------------------------------------------

control_results = con.execute("""
SELECT
    eq.control_id,
    bcm.control_name,
    COUNT(*) AS exception_count,
    COUNT(DISTINCT eq.customer_id) AS unique_customers,
    ROUND(SUM(COALESCE(eq.financial_impact, 0)), 2) AS financial_impact
FROM controls.exception_queue AS eq
LEFT JOIN controls.business_control_matrix AS bcm
    ON eq.control_id = bcm.control_id
GROUP BY
    eq.control_id,
    bcm.control_name
ORDER BY eq.control_id
""").fetchall()

for control_id, control_name, exception_count, unique_customers, financial_impact in control_results:

    control_type = con.execute("""
        SELECT control_type
        FROM controls.business_control_matrix
        WHERE control_id = ?
    """, [control_id]).fetchone()

    if control_type:
        control_type = control_type[0]
    else:
        control_type = "Unknown"

    notes = (
        f"{exception_count} duplicate billing records involved across "
        f"{unique_customers} duplicate customer cases"
        if control_id == "C001"
        else "Control execution completed successfully"
    )

    con.execute("""
        INSERT INTO core.control_execution_audit
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        run_id,
        run_timestamp,
        control_id,
        control_name,
        control_type,
        "SUCCESS",
        exception_count,
        unique_customers,
        financial_impact,
        notes
    ])

# ------------------------------------------------------------
# 4. OPERATIONAL RUN SUMMARY VIEW
# ------------------------------------------------------------

con.execute("""
CREATE OR REPLACE VIEW controls.v_operational_run_summary AS

SELECT
    audit_id,
    run_timestamp,
    COUNT(*) AS controls_executed,

    COUNT(*) FILTER (
        WHERE execution_status = 'SUCCESS'
    ) AS successful_controls,

    COUNT(*) FILTER (
        WHERE execution_status <> 'SUCCESS'
    ) AS failed_controls,

    SUM(exception_count) AS control_hits,

    SUM(unique_customers) AS control_customer_hits,

    SUM(exception_count) FILTER (
        WHERE control_id = 'C001'
    ) AS duplicate_records_involved,

    SUM(unique_customers) FILTER (
        WHERE control_id = 'C001'
    ) AS duplicate_customer_cases,

    ROUND(
        SUM(financial_impact),
        2
    ) AS financial_impact

FROM core.control_execution_audit

GROUP BY
    audit_id,
    run_timestamp

ORDER BY
    run_timestamp DESC;
""")

# ------------------------------------------------------------
# 5. CONTROL AUDIT HISTORY VIEW
# ------------------------------------------------------------

con.execute("""
CREATE OR REPLACE VIEW controls.v_control_audit_history AS

SELECT
    audit_id,
    run_timestamp,
    control_id,
    control_name,
    control_type,
    execution_status,
    exception_count,
    unique_customers,
    CASE
        WHEN control_id = 'C001' THEN exception_count
    END AS duplicate_records_involved,
    CASE
        WHEN control_id = 'C001' THEN unique_customers
    END AS duplicate_customer_cases,
    ROUND(financial_impact, 2) AS financial_impact,
    notes

FROM core.control_execution_audit

ORDER BY
    run_timestamp DESC,
    control_id;
""")

# ------------------------------------------------------------
# 6. CURRENT OPERATIONAL REPORT
# ------------------------------------------------------------

con.execute("""
CREATE OR REPLACE VIEW controls.v_operational_report AS

WITH current_kpis AS (
    SELECT *
    FROM controls.v_executive_kpis
),

sla AS (
    SELECT *
    FROM controls.v_sla_kpis
),

control_summary AS (
    SELECT
        COUNT(DISTINCT control_id) AS active_controls,
        COUNT(*) AS total_control_hits,
        COUNT(*) FILTER (
            WHERE status = 'OPEN'
        ) AS open_exceptions,
        COUNT(*) FILTER (
            WHERE severity = 'HIGH'
        ) AS high_severity_exceptions,
        COUNT(*) FILTER (
            WHERE control_id = 'C001'
        ) AS duplicate_records_involved,
        COUNT(DISTINCT customer_id) FILTER (
            WHERE control_id = 'C001'
        ) AS duplicate_customer_cases,
        ROUND(
            SUM(COALESCE(financial_impact, 0)),
            2
        ) AS total_financial_impact
    FROM controls.exception_queue
)

SELECT
    current_kpis.unique_customers,
    current_kpis.unique_exceptions,
    current_kpis.financial_impact,
    current_kpis.open_exceptions,
    current_kpis.high_severity_exceptions,

    control_summary.active_controls,
    control_summary.total_control_hits,
    control_summary.duplicate_records_involved,
    control_summary.duplicate_customer_cases,
    current_kpis.duplicate_records_involved AS c001_duplicate_records_involved,
    current_kpis.duplicate_customer_cases AS c001_duplicate_customer_cases,
    current_kpis.c001_affected_customers,

    sla.total_requests,
    sla.sla_met,
    sla.sla_at_risk,
    sla.sla_breached,
    sla.sla_met_rate_pct,
    sla.non_breach_rate_pct,
    sla.avg_turnaround_hours,
    sla.avg_review_turnaround_hours,

    CURRENT_TIMESTAMP AS report_generated_at

FROM current_kpis
CROSS JOIN sla
CROSS JOIN control_summary;
""")

# ------------------------------------------------------------
# 7. AUDIT TRAIL VALIDATION
# ------------------------------------------------------------

print("\nAUDIT TRAIL")

audit_count = con.execute("""
SELECT COUNT(*)
FROM core.control_execution_audit
WHERE audit_id = ?
""", [run_id]).fetchone()[0]

print(f"  Run ID       : {run_id}")
print(f"  Run timestamp: {run_timestamp}")
print(f"  Audit rows   : {audit_count}")

if audit_count != len(control_results):
    raise RuntimeError(
        f"Audit validation failed: expected {len(control_results)} rows, "
        f"found {audit_count}"
    )

print("  ✓ Audit trail validation passed")

# ------------------------------------------------------------
# 8. OPERATIONAL RUN SUMMARY
# ------------------------------------------------------------

print("\nOPERATIONAL RUN SUMMARY")

run_summary = con.execute("""
SELECT *
FROM controls.v_operational_run_summary
WHERE audit_id = ?
""", [run_id]).fetchdf()

print(run_summary.to_string(index=False))

# ------------------------------------------------------------
# 9. CONTROL AUDIT HISTORY
# ------------------------------------------------------------

print("\nCONTROL AUDIT HISTORY")

audit_history = con.execute("""
SELECT
    control_id,
    control_name,
    control_type,
    execution_status,
    exception_count,
    unique_customers,
    financial_impact
FROM controls.v_control_audit_history
WHERE audit_id = ?
ORDER BY control_id
""", [run_id]).fetchdf()

print(audit_history.to_string(index=False))

# ------------------------------------------------------------
# 10. OPERATIONAL REPORT
# ------------------------------------------------------------

print("\nCURRENT OPERATIONAL REPORT")

operational = con.execute("""
SELECT *
FROM controls.v_operational_report
""").fetchdf()

print(operational.to_string(index=False))

# ------------------------------------------------------------
# 11. FINAL VALIDATION
# ------------------------------------------------------------

required_views = [
    "v_operational_run_summary",
    "v_control_audit_history",
    "v_operational_report",
]

print("\nVIEW VALIDATION")

for view in required_views:

    exists = con.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = 'controls'
          AND table_name = ?
    """, [view]).fetchone()[0]

    if exists:
        print(f"  ✓ controls.{view}")
    else:
        raise RuntimeError(f"Missing view: controls.{view}")

con.close()

print("\n" + "=" * 70)
print("PHASE 4.6 COMPLETED SUCCESSFULLY")
print("=" * 70)
print(f"Database updated: {DB_PATH}")