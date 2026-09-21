import numpy as np
import pandas as pd

from config import PROCESSED

# ============================================================
# PHASE 3.2
# Customer Economics for Discount Requests
#
# Every number below comes from an EXPLICIT ASSUMPTION.
# These are the policy levers we will test in Phase 3.3.
# ============================================================

# --- Assumption A: how long a granted discount lasts -----------
DISCOUNT_DURATION_MONTHS = 12

# --- Assumption B: expected remaining customer lifetime --------
REMAINING_MONTHS_BY_CONTRACT = {
    "Month-to-month": 24,
    "One year": 36,
    "Two year": 48,
}
DEFAULT_REMAINING_MONTHS = 24

# --- Assumption C: baseline churn risk -------------------------
# Uses observed churn by contract if the cleaned data has a Churn
# column; otherwise falls back to these typical telecom values.
FALLBACK_CHURN = {
    "Month-to-month": 0.42,
    "One year": 0.11,
    "Two year": 0.03,
}
DEFAULT_CHURN = 0.25

# --- Assumption D: the reason changes real churn risk ----------
REASON_RISK_MULTIPLIER = {
    "Competitor offer": 1.5,   # actively shopping around
    "Price complaint": 1.2,
    "Service issue": 1.0,
    "Loyalty request": 0.8,
    "Billing dispute": 0.6,    # should be fixed by correction, not discount
}
MAX_CHURN_RISK = 0.90

# --- Assumption E: chance a discount actually saves the customer
# Bigger discounts help more, with diminishing returns.
SAVE_RATE_BY_DISCOUNT = {
    5: 0.10, 10: 0.20, 15: 0.30, 20: 0.36, 25: 0.40, 30: 0.42,
}


def observed_churn_by_contract(base):
    churn_col = next((c for c in ["Churn", "churn"] if c in base.columns), None)
    contract_col = next((c for c in ["Contract", "contract"] if c in base.columns), None)

    if churn_col is None or contract_col is None:
        return None

    flag = (
        base[churn_col].astype(str).str.strip().str.lower()
        .isin(["yes", "1", "true"])
    )
    return flag.groupby(base[contract_col]).mean().round(4).to_dict()


req = pd.read_csv(PROCESSED / "discount_requests.csv")
base = pd.read_csv(PROCESSED / "customers_clean.csv")

observed = observed_churn_by_contract(base)

if observed:
    churn_by_contract = observed
    churn_source = "observed from customers_clean.csv"
else:
    churn_by_contract = FALLBACK_CHURN
    churn_source = "assumed fallback values"

# ------------------------------------------------------------
# Economics
# ------------------------------------------------------------
monthly = req["current_monthly_charge"]
pct = req["requested_discount_pct"]

req["expected_remaining_months"] = (
    req["contract_type"]
    .map(REMAINING_MONTHS_BY_CONTRACT)
    .fillna(DEFAULT_REMAINING_MONTHS)
)

req["customer_value"] = (monthly * req["expected_remaining_months"]).round(2)

req["monthly_discount_amount"] = (monthly * pct / 100).round(2)

req["discount_cost"] = (
    req["monthly_discount_amount"] * DISCOUNT_DURATION_MONTHS
).round(2)

req["baseline_churn_risk"] = (
    req["contract_type"].map(churn_by_contract).fillna(DEFAULT_CHURN)
    * req["reason"].map(REASON_RISK_MULTIPLIER).fillna(1.0)
).clip(upper=MAX_CHURN_RISK).round(4)

req["save_rate"] = pct.map(SAVE_RATE_BY_DISCOUNT)

req["retention_uplift"] = (
    req["baseline_churn_risk"] * req["save_rate"]
).round(4)

req["estimated_retention_value"] = (
    req["customer_value"] * req["retention_uplift"]
).round(2)

req["net_economic_impact"] = (
    req["estimated_retention_value"] - req["discount_cost"]
).round(2)

req["benefit_cost_ratio"] = (
    req["estimated_retention_value"] / req["discount_cost"]
).round(3)

# Relative revenue tier inside the request population (contract-independent)
req["value_tier"] = pd.qcut(
    req["current_monthly_charge"].rank(method="first"),
    q=[0, 0.5, 0.8, 1.0],
    labels=["Standard", "High", "Strategic"],
)

# ------------------------------------------------------------
# Integrity checks
# ------------------------------------------------------------
econ_cols = [
    "customer_value", "discount_cost", "baseline_churn_risk",
    "save_rate", "retention_uplift", "estimated_retention_value",
    "net_economic_impact", "benefit_cost_ratio",
]
assert req[econ_cols].notna().all().all()
assert (req["discount_cost"] > 0).all()

req.to_csv(PROCESSED / "discount_requests_enriched.csv", index=False)

# ------------------------------------------------------------
# Report
# ------------------------------------------------------------
req["net_positive"] = req["net_economic_impact"] > 0

print("=" * 70)
print("PHASE 3.2 — CUSTOMER ECONOMICS")
print("=" * 70)
print(f"\nChurn risk source: {churn_source}")
print("Baseline churn by contract:", churn_by_contract)

print("\nPORTFOLIO TOTALS (if every request were approved)")
print(f"  Total discount cost          : ${req['discount_cost'].sum():,.0f}")
print(f"  Total est. retention value   : ${req['estimated_retention_value'].sum():,.0f}")
print(f"  Net economic impact          : ${req['net_economic_impact'].sum():,.0f}")
print(f"  Requests with positive net   : {req['net_positive'].sum()} of {len(req)}")

print("\nBY CONTRACT")
print(
    req.groupby("contract_type").agg(
        requests=("request_id", "count"),
        avg_cost=("discount_cost", "mean"),
        avg_retention_value=("estimated_retention_value", "mean"),
        pct_net_positive=("net_positive", "mean"),
    ).round(2).to_string()
)

print("\nBY REASON")
print(
    req.groupby("reason").agg(
        requests=("request_id", "count"),
        avg_cost=("discount_cost", "mean"),
        avg_retention_value=("estimated_retention_value", "mean"),
        pct_net_positive=("net_positive", "mean"),
    ).round(2).to_string()
)

print("\nBY REQUESTED DISCOUNT %")
print(
    req.groupby("requested_discount_pct").agg(
        requests=("request_id", "count"),
        pct_net_positive=("net_positive", "mean"),
        median_bcr=("benefit_cost_ratio", "median"),
    ).round(2).to_string()
)

print("\nVALUE TIERS")
print(req["value_tier"].value_counts().to_string())

print("\nBENEFIT-COST RATIO DISTRIBUTION")
print(req["benefit_cost_ratio"].describe().round(3).to_string())

print("\nSample rows:")
print(
    req[[
        "request_id", "contract_type", "reason", "requested_discount_pct",
        "customer_value", "discount_cost", "estimated_retention_value",
        "net_economic_impact", "value_tier",
    ]].head(5).to_string(index=False)
)

print("\nSaved: data/processed/discount_requests_enriched.csv")