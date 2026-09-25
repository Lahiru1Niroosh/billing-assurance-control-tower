import duckdb
from pathlib import Path

# ============================================================
# PHASE 4.5 — KPI & EXCEPTION VIEWS
# Billing Assurance & Revenue Protection Control Tower
# ============================================================

DB_PATH = Path("data/warehouse/billing_assurance.duckdb")

con = duckdb.connect(str(DB_PATH))

print("=" * 70)
print("PHASE 4.5 — KPI & EXCEPTION VIEWS")
print("=" * 70)

# ------------------------------------------------------------
# 1. EXECUTIVE KPI VIEW
# ------------------------------------------------------------

con.execute("""
CREATE OR REPLACE VIEW controls.v_executive_kpis AS

WITH exception_summary AS (
    SELECT
        COUNT(*) AS control_hits,
        COUNT(DISTINCT
            CASE
                WHEN customer_id IS NOT NULL
                THEN customer_id
            END
        ) AS unique_customers,
        COUNT(DISTINCT
            CONCAT(
                control_id,
                '|',
                COALESCE(CAST(customer_id AS VARCHAR), ''),
                '|',
                COALESCE(CAST(request_id AS VARCHAR), ''),
                '|',
                COALESCE(CAST(record_id AS VARCHAR), '')
            )
        ) AS unique_exceptions,
        COALESCE(SUM(financial_impact), 0) AS financial_impact,
        COUNT(*) FILTER (
            WHERE status = 'OPEN'
        ) AS open_exceptions,
        COUNT(*) FILTER (
            WHERE severity = 'HIGH'
        ) AS high_severity_exceptions,
        COUNT(*) FILTER (
            WHERE severity = 'MEDIUM'
        ) AS medium_severity_exceptions,
        COUNT(*) FILTER (
            WHERE severity = 'LOW'
        ) AS low_severity_exceptions
    FROM controls.exception_queue
),

c001_summary AS (
    SELECT
        COUNT(*) AS duplicate_records_involved,
        COUNT(DISTINCT customer_id) AS duplicate_customer_cases,
        COUNT(DISTINCT customer_id) AS affected_customers
    FROM controls.exception_queue
    WHERE control_id = 'C001'
)

SELECT
    control_hits,
    unique_exceptions,
    unique_customers,
    ROUND(financial_impact, 2) AS financial_impact,
    open_exceptions,
    high_severity_exceptions,
    medium_severity_exceptions,
    low_severity_exceptions,
    c001_summary.duplicate_records_involved,
    c001_summary.duplicate_customer_cases,
    c001_summary.affected_customers AS c001_affected_customers
FROM exception_summary
CROSS JOIN c001_summary;
""")

# ------------------------------------------------------------
# 2. EXCEPTION QUEUE VIEW
# ------------------------------------------------------------

con.execute("""
CREATE OR REPLACE VIEW controls.v_exception_queue AS

SELECT
    eq.exception_id,
    eq.control_id,
    bcm.control_name,
    eq.exception_type,
    eq.customer_id,
    eq.request_id,
    eq.record_id,
    eq.severity,
    eq.status,
    ROUND(COALESCE(eq.financial_impact, 0), 2) AS financial_impact,
    ROUND(eq.breach_hours, 2) AS breach_hours,
    eq.detected_at AS exception_date,
    eq.exception_reason AS description
FROM controls.exception_queue AS eq
LEFT JOIN controls.business_control_matrix AS bcm
    ON eq.control_id = bcm.control_id

ORDER BY
    CASE eq.severity
        WHEN 'HIGH' THEN 1
        WHEN 'MEDIUM' THEN 2
        WHEN 'LOW' THEN 3
        ELSE 4
    END,
    COALESCE(eq.financial_impact, 0) DESC;
""")

# ------------------------------------------------------------
# 3. CONTROL PERFORMANCE VIEW
# ------------------------------------------------------------

con.execute("""
CREATE OR REPLACE VIEW controls.v_control_performance AS

SELECT
    eq.control_id,
    bcm.control_name,
    COUNT(*) AS control_hits,
    COUNT(DISTINCT eq.customer_id) AS unique_customers,
    COUNT(*) FILTER (
        WHERE eq.control_id = 'C001'
    ) AS duplicate_records_involved,
    COUNT(DISTINCT eq.customer_id) FILTER (
        WHERE eq.control_id = 'C001'
    ) AS duplicate_customer_cases,
    COUNT(DISTINCT eq.customer_id) AS affected_customers,
    ROUND(SUM(COALESCE(eq.financial_impact, 0)), 2) AS financial_impact,

    COUNT(*) FILTER (
        WHERE eq.status = 'OPEN'
    ) AS open_count,

    COUNT(*) FILTER (
        WHERE eq.status = 'REVIEWED'
    ) AS reviewed_count,

    COUNT(*) FILTER (
        WHERE eq.status = 'MONITOR'
    ) AS monitor_count,

    COUNT(*) FILTER (
        WHERE eq.severity = 'HIGH'
    ) AS high_severity_count

FROM controls.exception_queue AS eq
LEFT JOIN controls.business_control_matrix AS bcm
    ON eq.control_id = bcm.control_id

GROUP BY
    eq.control_id,
    bcm.control_name

ORDER BY
    financial_impact DESC;
""")

# ------------------------------------------------------------
# 4. SLA KPI VIEW
# ------------------------------------------------------------

con.execute("""
CREATE OR REPLACE VIEW controls.v_sla_kpis AS

SELECT
    COUNT(*) AS total_requests,

    COUNT(*) FILTER (
        WHERE sla_status = 'Met'
    ) AS sla_met,

    COUNT(*) FILTER (
        WHERE sla_status = 'At Risk'
    ) AS sla_at_risk,

    COUNT(*) FILTER (
        WHERE sla_status = 'Breached'
    ) AS sla_breached,

    ROUND(
        100.0 *
        COUNT(*) FILTER (
            WHERE sla_status = 'Met'
        )
        / NULLIF(COUNT(*), 0),
        2
    ) AS sla_met_rate_pct,

    ROUND(
        100.0 * (
            COUNT(*) FILTER (
                WHERE sla_status = 'Met'
            )
            + COUNT(*) FILTER (
                WHERE sla_status = 'At Risk'
            )
        )
        / NULLIF(COUNT(*), 0),
        2
    ) AS non_breach_rate_pct,

    ROUND(
        AVG(turnaround_hours),
        2
    ) AS avg_turnaround_hours,

    ROUND(
        AVG(
            CASE
                WHEN approval_level <> 'System'
                THEN turnaround_hours
            END
        ),
        2
    ) AS avg_review_turnaround_hours,

    ROUND(
        SUM(CASE
            WHEN sla_status = 'Breached'
            THEN breach_hours
            ELSE 0
        END),
        2
    ) AS total_breach_hours

FROM staging.discount_decisions_sla;
""")

# ------------------------------------------------------------
# 5. CUSTOMER RISK VIEW
# ------------------------------------------------------------

con.execute("""
CREATE OR REPLACE VIEW controls.v_customer_risk AS

SELECT
    customer_id,

    COUNT(*) AS control_hits,

    COUNT(DISTINCT control_id) AS controls_triggered,

    COUNT(*) FILTER (
        WHERE severity = 'HIGH'
    ) AS high_severity_hits,

    COUNT(*) FILTER (
        WHERE status = 'OPEN'
    ) AS open_exceptions,

    ROUND(
        SUM(COALESCE(financial_impact, 0)),
        2
    ) AS financial_impact,

    CASE
        WHEN COUNT(*) FILTER (
            WHERE severity = 'HIGH'
        ) >= 2
            THEN 'HIGH'

        WHEN COUNT(*) >= 2
            THEN 'MEDIUM'

        ELSE 'LOW'
    END AS customer_risk

FROM controls.exception_queue

WHERE customer_id IS NOT NULL

GROUP BY customer_id

ORDER BY
    CASE customer_risk
        WHEN 'HIGH' THEN 1
        WHEN 'MEDIUM' THEN 2
        WHEN 'LOW' THEN 3
    END,
    financial_impact DESC;
""")

# ------------------------------------------------------------
# 6. VALIDATION
# ------------------------------------------------------------

print("\nCREATED KPI VIEWS")

views = [
    "v_executive_kpis",
    "v_exception_queue",
    "v_control_performance",
    "v_sla_kpis",
    "v_customer_risk",
]

for view in views:
    exists = con.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = 'controls'
          AND table_name = ?
    """, [view]).fetchone()[0]

    if exists:
        print(f"  ✓ controls.{view}")
    else:
        raise RuntimeError(f"View missing: controls.{view}")

# ------------------------------------------------------------
# 7. EXECUTIVE KPI OUTPUT
# ------------------------------------------------------------

print("\nEXECUTIVE KPI SUMMARY")

kpi = con.execute("""
SELECT *
FROM controls.v_executive_kpis
""").fetchdf()

print(kpi.to_string(index=False))

# ------------------------------------------------------------
# 8. CONTROL PERFORMANCE OUTPUT
# ------------------------------------------------------------

print("\nCONTROL PERFORMANCE")

control_perf = con.execute("""
SELECT *
FROM controls.v_control_performance
""").fetchdf()

print(control_perf.to_string(index=False))

# ------------------------------------------------------------
# 9. SLA OUTPUT
# ------------------------------------------------------------

print("\nSLA KPI SUMMARY")

sla = con.execute("""
SELECT *
FROM controls.v_sla_kpis
""").fetchdf()

print(sla.to_string(index=False, formatters={
    "sla_met_rate_pct": "{:.2f}".format,
    "non_breach_rate_pct": "{:.2f}".format,
    "avg_turnaround_hours": "{:.2f}".format,
    "avg_review_turnaround_hours": "{:.2f}".format,
    "total_breach_hours": "{:.2f}".format
}))

# ------------------------------------------------------------
# 10. CUSTOMER RISK SUMMARY
# ------------------------------------------------------------

print("\nCUSTOMER RISK SUMMARY")

risk = con.execute("""
SELECT
    customer_risk,
    COUNT(*) AS customers,
    SUM(control_hits) AS control_hits,
    ROUND(SUM(financial_impact), 2) AS financial_impact
FROM controls.v_customer_risk
GROUP BY customer_risk
ORDER BY
    CASE customer_risk
        WHEN 'HIGH' THEN 1
        WHEN 'MEDIUM' THEN 2
        WHEN 'LOW' THEN 3
    END
""").fetchdf()

print(risk.to_string(index=False))

# ------------------------------------------------------------
# 11. SAMPLE EXCEPTION QUEUE
# ------------------------------------------------------------

print("\nTOP 10 EXCEPTIONS")

exceptions = con.execute("""
SELECT
    exception_id,
    control_id,
    control_name,
    customer_id,
    severity,
    status,
    financial_impact
FROM controls.v_exception_queue
LIMIT 10
""").fetchdf()

print(exceptions.to_string(index=False))

con.close()

print("\n" + "=" * 70)
print("PHASE 4.5 COMPLETED SUCCESSFULLY")
print("=" * 70)
print(f"Database updated: {DB_PATH}")