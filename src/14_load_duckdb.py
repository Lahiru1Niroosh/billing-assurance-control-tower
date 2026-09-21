from pathlib import Path
import duckdb


# ============================================================
# PHASE 4.2 — LOAD PROCESSED DATA INTO DUCKDB
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DB_PATH = PROJECT_ROOT / "data" / "warehouse" / "billing_assurance.duckdb"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


print("=" * 70)
print("PHASE 4.2 — LOAD PROCESSED DATA INTO DUCKDB")
print("=" * 70)

print(f"\nDatabase : {DB_PATH}")
print(f"Source   : {PROCESSED_DIR}")


# ------------------------------------------------------------
# Connect to DuckDB
# ------------------------------------------------------------

con = duckdb.connect(str(DB_PATH))


# ------------------------------------------------------------
# Source files
# ------------------------------------------------------------

files = {
    "customers_clean": "customers_clean.csv",
    "billing_test_set": "billing_test_set.csv",
    "validation_results": "validation_results.csv",
    "holdout_validation_results": "holdout_validation_results.csv",
    "discount_requests": "discount_requests.csv",
    "discount_requests_enriched": "discount_requests_enriched.csv",
    "discount_decisions": "discount_decisions.csv",
    "discount_decisions_sla": "discount_decisions_sla.csv",
}


# ------------------------------------------------------------
# Load each CSV into staging
# ------------------------------------------------------------

print("\nLOADING TABLES")
print("-" * 70)

loaded_tables = []

for table_name, filename in files.items():

    file_path = PROCESSED_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required source file not found: {file_path}"
        )

    # Read CSV automatically and create/replace staging table
    con.execute(
        f"""
        CREATE OR REPLACE TABLE staging.{table_name} AS
        SELECT *
        FROM read_csv_auto(
            '{file_path.as_posix()}',
            header = true,
            sample_size = -1
        );
        """
    )

    row_count = con.execute(
        f"""
        SELECT COUNT(*)
        FROM staging.{table_name};
        """
    ).fetchone()[0]

    column_count = con.execute(
        f"""
        SELECT COUNT(*)
        FROM information_schema.columns
        WHERE table_schema = 'staging'
          AND table_name = '{table_name}';
        """
    ).fetchone()[0]

    loaded_tables.append(table_name)

    print(
        f"  ✓ {table_name:<30} "
        f"{row_count:>6} rows | "
        f"{column_count:>3} columns"
    )


# ------------------------------------------------------------
# Create staging load audit table
# ------------------------------------------------------------

con.execute("""
    CREATE TABLE IF NOT EXISTS core.staging_load_audit (
        table_name VARCHAR,
        source_file VARCHAR,
        row_count BIGINT,
        column_count BIGINT,
        loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")


# Clear previous audit records for these tables
con.execute("""
    DELETE FROM core.staging_load_audit
    WHERE table_name IN (
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'staging'
    );
""")


# Record current load
for table_name, filename in files.items():

    row_count = con.execute(
        f"""
        SELECT COUNT(*)
        FROM staging.{table_name};
        """
    ).fetchone()[0]

    column_count = con.execute(
        f"""
        SELECT COUNT(*)
        FROM information_schema.columns
        WHERE table_schema = 'staging'
          AND table_name = '{table_name}';
        """
    ).fetchone()[0]

    con.execute(
        """
        INSERT INTO core.staging_load_audit
        (
            table_name,
            source_file,
            row_count,
            column_count
        )
        VALUES (?, ?, ?, ?);
        """,
        [
            table_name,
            filename,
            row_count,
            column_count,
        ],
    )


# ------------------------------------------------------------
# Verify staging tables
# ------------------------------------------------------------

print("\nSTAGING TABLES")
print("-" * 70)

tables = con.execute("""
    SELECT
        table_name
    FROM information_schema.tables
    WHERE table_schema = 'staging'
      AND table_type = 'BASE TABLE'
    ORDER BY table_name;
""").fetchall()

for table in tables:
    print(f"  ✓ staging.{table[0]}")


# ------------------------------------------------------------
# Load audit summary
# ------------------------------------------------------------

print("\nLOAD AUDIT")
print("-" * 70)

audit = con.execute("""
    SELECT
        table_name,
        row_count,
        column_count
    FROM core.staging_load_audit
    ORDER BY table_name;
""").fetchall()

for row in audit:
    print(
        f"  {row[0]:<30} "
        f"{row[1]:>6} rows | "
        f"{row[2]:>3} columns"
    )


# ------------------------------------------------------------
# Close
# ------------------------------------------------------------

con.close()

print("\nPhase 4.2 completed successfully.")
print(f"Database updated: {DB_PATH}")