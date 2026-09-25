from pathlib import Path
import duckdb


# ============================================================
# PHASE 4.4 — SQL CONTROL ENGINE
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "warehouse" / "billing_assurance.duckdb"


print("=" * 70)
print("PHASE 4.4 — SQL CONTROL ENGINE")
print("=" * 70)

print(f"\nDatabase: {DB_PATH}")


con = duckdb.connect(str(DB_PATH))


# ============================================================
# 1. C001 — DUPLICATE BILLING
# ============================================================

print("\n[C001] DUPLICATE BILLING")

con.execute("""
CREATE OR REPLACE TABLE controls.c001_duplicate_billing AS

WITH duplicate_customers AS (
    SELECT
        customerID,
        COUNT(*) AS duplicate_record_count
    FROM staging.billing_test_set
    WHERE customerID IS NOT NULL
    GROUP BY customerID
    HAVING COUNT(*) > 1
)

SELECT
    'C001' AS control_id,
    'Duplicate Billing Record' AS exception_type,
    'HIGH' AS severity,
    b.record_id,
    b.customerID AS customer_id,
    NULL::VARCHAR AS request_id,
    b.MonthlyCharges AS financial_impact,
    NULL::DOUBLE AS breach_hours,
    'OPEN' AS status,
    'Billing Operations' AS owner,
    CURRENT_TIMESTAMP AS detected_at,
    CONCAT(
        'Record involved in a duplicate customer case with ',
        d.duplicate_record_count,
        ' billing records; all records are retained for investigation'
    ) AS exception_reason

FROM staging.billing_test_set b

INNER JOIN duplicate_customers d
    ON b.customerID = d.customerID;
""")


c001_count = con.execute("""
    SELECT COUNT(*)
    FROM controls.c001_duplicate_billing
""").fetchone()[0]

c001_cases = con.execute("""
    SELECT COUNT(DISTINCT customer_id)
    FROM controls.c001_duplicate_billing
""").fetchone()[0]

print(f"  Duplicate records involved: {c001_count}")
print(f"  Duplicate customer cases : {c001_cases}")


# ============================================================
# 2. C002 — MISSING BILLING TOTAL
# ============================================================

print("\n[C002] MISSING BILLING TOTAL")

con.execute("""
CREATE OR REPLACE TABLE controls.c002_missing_billing_total AS

SELECT
    'C002' AS control_id,
    'Missing Billing Total' AS exception_type,
    'HIGH' AS severity,
    record_id,
    customerID AS customer_id,
    NULL::VARCHAR AS request_id,
    COALESCE(MonthlyCharges, 0) AS financial_impact,
    NULL::DOUBLE AS breach_hours,
    'OPEN' AS status,
    'Billing Operations' AS owner,
    CURRENT_TIMESTAMP AS detected_at,

    CASE
        WHEN tenure > 0 AND TotalCharges IS NULL
            THEN 'TotalCharges is missing'
        WHEN tenure > 0 AND TotalCharges = 0
            THEN 'TotalCharges is zero'
        WHEN MonthlyCharges <= 0
             AND (PhoneService OR InternetService <> 'No')
            THEN 'MonthlyCharges is non-positive while a service is active'
        ELSE 'Billing amount anomaly'
    END AS exception_reason

FROM staging.billing_test_set

WHERE
       ((TotalCharges IS NULL OR TotalCharges = 0) AND tenure > 0)
    OR (
        MonthlyCharges <= 0
        AND (PhoneService OR InternetService <> 'No')
    );
""")


c002_count = con.execute("""
    SELECT COUNT(*)
    FROM controls.c002_missing_billing_total
""").fetchone()[0]

print(f"  Validated missing/zero billing exceptions: {c002_count}")


# ============================================================
# 3. C003 — RATE MISMATCH
# ============================================================

print("\n[C003] RATE MISMATCH")

con.execute("""
CREATE OR REPLACE TABLE controls.c003_rate_mismatch AS

SELECT
    'C003' AS control_id,
    'Rate Mismatch' AS exception_type,
    COALESCE(severity, 'HIGH') AS severity,
    record_id,
    customerID AS customer_id,
    NULL::VARCHAR AS request_id,
    COALESCE(exposure, ABS(rate_residual), 0) AS financial_impact,
    NULL::DOUBLE AS breach_hours,
    'OPEN' AS status,
    'Billing Operations' AS owner,
    CURRENT_TIMESTAMP AS detected_at,

    CONCAT(
        'Actual monthly charge differs from expected rate; residual = ',
        ROUND(rate_residual, 2)
    ) AS exception_reason

FROM staging.validation_results

WHERE flag_rate_mismatch = TRUE;
""")


c003_count = con.execute("""
    SELECT COUNT(*)
    FROM controls.c003_rate_mismatch
""").fetchone()[0]

print(f"  Exceptions detected: {c003_count}")


# ============================================================
# 4. C004 — DISCOUNT APPROVAL
# ============================================================

print("\n[C004] DISCOUNT APPROVAL")

con.execute("""
CREATE OR REPLACE TABLE controls.c004_discount_approval AS

SELECT
    'C004' AS control_id,
    'Discount Approval' AS exception_type,

    CASE
        WHEN decision = 'MANAGER_REVIEW'
            THEN 'HIGH'
        WHEN decision = 'DECLINE'
            THEN 'HIGH'
        ELSE 'MEDIUM'
    END AS severity,

    NULL::BIGINT AS record_id,
    customer_id,
    request_id,

    ABS(net_economic_impact) AS financial_impact,
    NULL::DOUBLE AS breach_hours,

    CASE
        WHEN decision = 'MANAGER_REVIEW'
            THEN 'OPEN'
        WHEN decision = 'DECLINE'
            THEN 'REVIEWED'
        ELSE 'APPROVED'
    END AS status,

    CASE
        WHEN approval_level = 'Senior Manager'
            THEN 'Senior Manager'
        WHEN approval_level = 'Manager'
            THEN 'Operations Manager'
        WHEN approval_level = 'Supervisor'
            THEN 'Billing Operations'
        ELSE 'System'
    END AS owner,

    CURRENT_TIMESTAMP AS detected_at,

    decision_reason AS exception_reason

FROM staging.discount_decisions

WHERE decision <> 'AUTO_APPROVE';
""")


c004_count = con.execute("""
    SELECT COUNT(*)
    FROM controls.c004_discount_approval
""").fetchone()[0]

print(f"  Exceptions detected: {c004_count}")


# ============================================================
# 5. C005 — SLA MONITORING
# ============================================================

print("\n[C005] SLA MONITORING")

con.execute("""
CREATE OR REPLACE TABLE controls.c005_sla_monitoring AS

SELECT
    'C005' AS control_id,

    CASE
        WHEN sla_status = 'Breached'
            THEN 'SLA Breach'
        ELSE 'SLA At Risk'
    END AS exception_type,

    CASE
        WHEN sla_status = 'Breached'
            THEN 'HIGH'
        ELSE 'MEDIUM'
    END AS severity,

    NULL::BIGINT AS record_id,
    customer_id,
    request_id,

    0.0::DOUBLE AS financial_impact,
    COALESCE(breach_hours, 0.0)::DOUBLE AS breach_hours,

    CASE
        WHEN sla_status = 'Breached'
            THEN 'OPEN'
        ELSE 'MONITOR'
    END AS status,

    CASE
        WHEN approval_level = 'Senior Manager'
            THEN 'Senior Manager'
        WHEN approval_level = 'Manager'
            THEN 'Operations Manager'
        WHEN approval_level = 'Supervisor'
            THEN 'Billing Operations'
        ELSE 'Operations'
    END AS owner,

    CURRENT_TIMESTAMP AS detected_at,

    CONCAT(
        'SLA target = ',
        sla_target_hours,
        ' hours; turnaround = ',
        ROUND(turnaround_hours, 2),
        ' hours'
    ) AS exception_reason

FROM staging.discount_decisions_sla

WHERE sla_status IN ('Breached', 'At Risk');
""")


c005_count = con.execute("""
    SELECT COUNT(*)
    FROM controls.c005_sla_monitoring
""").fetchone()[0]

print(f"  Exceptions detected: {c005_count}")


# ============================================================
# 6. UNIFIED EXCEPTION QUEUE
# ============================================================

print("\nBUILDING UNIFIED EXCEPTION QUEUE")

con.execute("""
CREATE OR REPLACE TABLE controls.exception_queue AS

SELECT * FROM controls.c001_duplicate_billing

UNION ALL

SELECT * FROM controls.c002_missing_billing_total

UNION ALL

SELECT * FROM controls.c003_rate_mismatch

UNION ALL

SELECT * FROM controls.c004_discount_approval

UNION ALL

SELECT * FROM controls.c005_sla_monitoring;
""")


# ============================================================
# 7. EXCEPTION ID
# ============================================================

con.execute("""
CREATE OR REPLACE TABLE controls.exception_queue AS

SELECT
    ROW_NUMBER() OVER (
        ORDER BY detected_at, control_id, customer_id, request_id
    ) AS exception_id,

    *

FROM controls.exception_queue;
""")


# ============================================================
# 8. CONTROL SUMMARY
# ============================================================

print("\nCONTROL RESULTS")
print("-" * 70)

summary = con.execute("""
SELECT
    control_id,
    exception_type,
    COUNT(*) AS exceptions
FROM controls.exception_queue
GROUP BY
    control_id,
    exception_type
ORDER BY control_id;
""").fetchall()


for row in summary:
    print(
        f"  {row[0]} | "
        f"{row[1]:<25} | "
        f"{row[2]:>5}"
    )


# ============================================================
# 9. SEVERITY SUMMARY
# ============================================================

print("\nBY SEVERITY")
print("-" * 70)

severity_summary = con.execute("""
SELECT
    severity,
    COUNT(*) AS exceptions
FROM controls.exception_queue
GROUP BY severity
ORDER BY
    CASE severity
        WHEN 'HIGH' THEN 1
        WHEN 'MEDIUM' THEN 2
        WHEN 'LOW' THEN 3
        ELSE 4
    END;
""").fetchall()


for row in severity_summary:
    print(f"  {row[0]:<10} {row[1]:>5}")


# ============================================================
# 10. STATUS SUMMARY
# ============================================================

print("\nBY STATUS")
print("-" * 70)

status_summary = con.execute("""
SELECT
    status,
    COUNT(*) AS exceptions
FROM controls.exception_queue
GROUP BY status
ORDER BY status;
""").fetchall()


for row in status_summary:
    print(f"  {row[0]:<10} {row[1]:>5}")


# ============================================================
# 11. FINANCIAL EXPOSURE
# ============================================================

print("\nFINANCIAL IMPACT")
print("-" * 70)

financial = con.execute("""
SELECT
    COUNT(*) AS exceptions,
    ROUND(SUM(COALESCE(financial_impact, 0)), 2) AS total_financial_impact
FROM controls.exception_queue;
""").fetchone()


print(f"  Exceptions        : {financial[0]}")
print(f"  Financial impact  : ${financial[1]:,.2f}")


# ============================================================
# 12. VALIDATION
# ============================================================

total_exceptions = con.execute("""
SELECT COUNT(*)
FROM controls.exception_queue;
""").fetchone()[0]


assert total_exceptions > 0, (
    "Control engine produced zero exceptions. "
    "Review the control logic."
)


required_tables = [
    "c001_duplicate_billing",
    "c002_missing_billing_total",
    "c003_rate_mismatch",
    "c004_discount_approval",
    "c005_sla_monitoring",
    "exception_queue",
]


for table in required_tables:

    exists = con.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = 'controls'
          AND table_name = ?;
    """, [table]).fetchone()[0]

    assert exists == 1, (
        f"Required control table missing: controls.{table}"
    )


print("\nVALIDATION PASSED")
print(f"  Total exceptions: {total_exceptions}")
print("  All 5 control outputs exist.")


con.close()

print("\nDatabase updated:")
print(DB_PATH)

print("\nPhase 4.4 completed successfully.")