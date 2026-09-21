from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
INTERIM = ROOT / "data" / "interim"
PROCESSED = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"

SEED = 42
INJECTION_RATE = 0.03

# Columns derived from billing fields. They must be removed from the test set,
# otherwise they leak the correct values to the validation rules.
DERIVED_COLS = ["expected_total", "total_variance", "variance_pct",
                "avg_billed_per_month", "annual_revenue"]