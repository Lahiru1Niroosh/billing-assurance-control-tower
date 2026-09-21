from pathlib import Path
import duckdb


# ============================================================
# PHASE 4.3 — BUSINESS CONTROL MATRIX
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "warehouse" / "billing_assurance.duckdb"


print("=" * 70)
print("PHASE 4.3 — BUSINESS CONTROL MATRIX")
print("=" * 70)

con = duckdb.connect(str(DB_PATH))


# ------------------------------------------------------------
# Control register
# ------------------------------------------------------------

con.execute("""
CREATE TABLE IF NOT EXISTS controls.business_control_matrix (
    control_id VARCHAR PRIMARY KEY,
    control_name VARCHAR NOT NULL,
    business_objective VARCHAR NOT NULL,
    control_type VARCHAR NOT NULL,
    source_table VARCHAR NOT NULL,
    detection_logic VARCHAR NOT NULL,
    exception_output VARCHAR NOT NULL,
    owner VARCHAR NOT NULL,
    frequency VARCHAR NOT NULL,
    severity VARCHAR NOT NULL,
    status VARCHAR NOT NULL
);
""")


# ------------------------------------------------------------
# Define controls
# ------------------------------------------------------------

controls = [
    (
        "C001",
        "Duplicate Billing",
        "Prevent duplicate customer billing",
        "Detective",
        "staging.billing_test_set",
        "Identify repeated customer billing records",
        "Duplicate billing exception",
        "Billing Operations",
        "Per billing cycle",
        "High",
        "Active",
    ),
    (
        "C002",
        "Missing Billing Total",
        "Detect incomplete or missing billing amounts",
        "Detective",
        "staging.billing_test_set",
        "Identify missing or zero billing totals",
        "Missing billing exception",
        "Billing Operations",
        "Per billing cycle",
        "High",
        "Active",
    ),
    (
        "C003",
        "Rate Mismatch",
        "Detect potential revenue leakage from incorrect rates",
        "Detective",
        "staging.validation_results",
        "Compare actual billing rate with expected rate",
        "Rate mismatch exception",
        "Billing Operations",
        "Per billing cycle",
        "High",
        "Active",
    ),
    (
        "C004",
        "Discount Approval",
        "Protect revenue and margin during discount decisions",
        "Preventive",
        "staging.discount_decisions",
        "Evaluate benefit-cost economics and approval policy",
        "Discount approval exception",
        "Operations Manager",
        "Per request",
        "High",
        "Active",
    ),
    (
        "C005",
        "SLA Monitoring",
        "Monitor approval turnaround and operational efficiency",
        "Detective",
        "staging.discount_decisions_sla",
        "Identify breached or at-risk approval requests",
        "SLA exception",
        "Operations",
        "Continuous",
        "Medium",
        "Active",
    ),
]


# ------------------------------------------------------------
# Replace existing definitions
# ------------------------------------------------------------

con.execute("""
DELETE FROM controls.business_control_matrix;
""")


for control in controls:
    con.execute("""
        INSERT INTO controls.business_control_matrix
        (
            control_id,
            control_name,
            business_objective,
            control_type,
            source_table,
            detection_logic,
            exception_output,
            owner,
            frequency,
            severity,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, control)


# ------------------------------------------------------------
# Display matrix
# ------------------------------------------------------------

print("\nBUSINESS CONTROL MATRIX")
print("-" * 70)

rows = con.execute("""
    SELECT
        control_id,
        control_name,
        control_type,
        owner,
        severity,
        status
    FROM controls.business_control_matrix
    ORDER BY control_id;
""").fetchall()


for row in rows:
    print(
        f"  {row[0]} | "
        f"{row[1]:<25} | "
        f"{row[2]:<10} | "
        f"{row[3]:<20} | "
        f"{row[4]:<6} | "
        f"{row[5]}"
    )


print("\nCONTROL DETAILS")
print("-" * 70)

details = con.execute("""
    SELECT
        control_id,
        business_objective,
        source_table,
        detection_logic,
        exception_output
    FROM controls.business_control_matrix
    ORDER BY control_id;
""").fetchall()


for row in details:
    print(f"\n[{row[0]}]")
    print(f"  Objective : {row[1]}")
    print(f"  Source    : {row[2]}")
    print(f"  Logic     : {row[3]}")
    print(f"  Exception : {row[4]}")


# ------------------------------------------------------------
# Validation
# ------------------------------------------------------------

control_count = con.execute("""
    SELECT COUNT(*)
    FROM controls.business_control_matrix;
""").fetchone()[0]

assert control_count == 5, (
    f"Expected 5 controls, found {control_count}"
)


print("\nValidation passed: 5 controls registered.")


con.close()

print(f"\nDatabase updated: {DB_PATH}")
print("Phase 4.3 completed successfully.")