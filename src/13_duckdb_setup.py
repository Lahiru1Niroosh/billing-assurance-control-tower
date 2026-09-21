from pathlib import Path
import duckdb


# ============================================================
# PHASE 4.1 — DUCKDB WAREHOUSE SETUP
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WAREHOUSE_DIR = PROJECT_ROOT / "data" / "warehouse"
DB_PATH = WAREHOUSE_DIR / "billing_assurance.duckdb"

WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)


print("=" * 70)
print("PHASE 4.1 — DUCKDB WAREHOUSE SETUP")
print("=" * 70)

print(f"\nDatabase path: {DB_PATH}")


# Connect/create DuckDB database
con = duckdb.connect(str(DB_PATH))


# ------------------------------------------------------------
# Create logical schemas
# ------------------------------------------------------------

con.execute("""
    CREATE SCHEMA IF NOT EXISTS staging;
""")

con.execute("""
    CREATE SCHEMA IF NOT EXISTS core;
""")

con.execute("""
    CREATE SCHEMA IF NOT EXISTS controls;
""")


# ------------------------------------------------------------
# Create warehouse metadata table
# ------------------------------------------------------------

con.execute("""
    CREATE TABLE IF NOT EXISTS core.warehouse_metadata (
        project_name VARCHAR,
        warehouse_name VARCHAR,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        purpose VARCHAR
    );
""")


# Insert metadata only if table is empty
existing = con.execute("""
    SELECT COUNT(*)
    FROM core.warehouse_metadata
""").fetchone()[0]

if existing == 0:
    con.execute("""
        INSERT INTO core.warehouse_metadata
        (
            project_name,
            warehouse_name,
            purpose
        )
        VALUES
        (
            'Billing Assurance & Revenue Protection Control Tower',
            'DuckDB Analytical Warehouse',
            'Operational billing controls, discount decisions, SLA monitoring and exception management'
        );
    """)


# ------------------------------------------------------------
# Verify schemas
# ------------------------------------------------------------

schemas = con.execute("""
    SELECT schema_name
    FROM information_schema.schemata
    WHERE schema_name IN ('staging', 'core', 'controls')
    ORDER BY schema_name;
""").fetchall()


print("\nCREATED SCHEMAS")

for schema in schemas:
    print(f"  ✓ {schema[0]}")


# ------------------------------------------------------------
# Verify metadata
# ------------------------------------------------------------

metadata = con.execute("""
    SELECT
        project_name,
        warehouse_name,
        purpose
    FROM core.warehouse_metadata;
""").fetchone()


print("\nWAREHOUSE METADATA")
print(f"  Project   : {metadata[0]}")
print(f"  Warehouse : {metadata[1]}")
print(f"  Purpose   : {metadata[2]}")


# ------------------------------------------------------------
# Close connection
# ------------------------------------------------------------

con.close()


print("\nDatabase created successfully.")
print(f"Saved: {DB_PATH}")