from pathlib import Path
import duckdb
import pandas as pd

# ============================================================
# BILLING ASSURANCE CONTROL TOWER
# DATABASE CONNECTION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "warehouse"
    / "billing_assurance.duckdb"
)

def get_connection():
    """Create a read-only DuckDB connection."""
    return duckdb.connect(
        str(DATABASE_PATH),
        read_only=True
    )

def run_query(query: str) -> pd.DataFrame:
    """Execute a SQL query and return a pandas DataFrame."""
    con = get_connection()

    try:
        return con.execute(query).df()
    finally:
        con.close()

def get_executive_kpis():
    return run_query(
        """
        SELECT *
        FROM controls.v_executive_kpis
        """
    )

def get_exception_queue():
    return run_query(
        """
        SELECT *
        FROM controls.v_exception_queue
        """
    )

def get_control_performance():
    return run_query(
        """
        SELECT *
        FROM controls.v_control_performance
        """
    )

def get_sla_kpis():
    return run_query(
        """
        SELECT *
        FROM controls.v_sla_kpis
        """
    )

def get_customer_risk():
    return run_query(
        """
        SELECT *
        FROM controls.v_customer_risk
        """
    )

def get_operational_report():
    return run_query(
        """
        SELECT *
        FROM controls.v_operational_report
        """
    )
