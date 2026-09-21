import numpy as np
import pandas as pd

from config import PROCESSED, REPORTS

# ============================================================
# PHASE 3.1
# Synthetic Discount Request Generator
#
# All behaviour below is an ASSUMPTION, not observed data.
# Document these assumptions in the README / control matrix.
# ============================================================

SEED = 3030
N_REQUESTS = 500
START_DATE = "2026-01-01"
END_DATE = "2026-06-30"

DISCOUNT_OPTIONS = [5, 10, 15, 20, 25, 30]

# Assumption 1: why customers ask depends on contract type
REASON_BY_CONTRACT = {
    "Month-to-month": {
        "Competitor offer": 0.35, "Price complaint": 0.30,
        "Service issue": 0.15, "Billing dispute": 0.10,
        "Loyalty request": 0.10,
    },
    "One year": {
        "Competitor offer": 0.20, "Price complaint": 0.25,
        "Service issue": 0.15, "Billing dispute": 0.10,
        "Loyalty request": 0.30,
    },
    "Two year": {
        "Competitor offer": 0.10, "Price complaint": 0.20,
        "Service issue": 0.15, "Billing dispute": 0.10,
        "Loyalty request": 0.45,
    },
}
DEFAULT_REASON_PROBS = REASON_BY_CONTRACT["Month-to-month"]

# Assumption 2: how much they ask for depends on the reason
DISCOUNT_WEIGHTS_BY_REASON = {
    "Competitor offer": [0.05, 0.15, 0.25, 0.25, 0.15, 0.15],
    "Price complaint":  [0.15, 0.30, 0.25, 0.15, 0.10, 0.05],
    "Service issue":    [0.20, 0.35, 0.25, 0.10, 0.05, 0.05],
    "Billing dispute":  [0.30, 0.35, 0.20, 0.10, 0.03, 0.02],
    "Loyalty request":  [0.35, 0.35, 0.20, 0.07, 0.02, 0.01],
}


def find_col(df, candidates):
    return next((c for c in candidates if c in df.columns), None)


rng = np.random.default_rng(SEED)

base = pd.read_csv(PROCESSED / "customers_clean.csv")

id_col = find_col(base, ["customerID", "customer_id", "CustomerID"])
contract_col = find_col(base, ["Contract", "contract", "contract_type"])

if id_col is None:
    base["customer_id"] = [f"C-{i:05d}" for i in range(1, len(base) + 1)]
    id_col = "customer_id"

if contract_col is None:
    base["Contract"] = "Month-to-month"
    contract_col = "Contract"

# Only real, billable, unique customers can request a discount
eligible = (
    base[(base["tenure"] > 0) & (base["MonthlyCharges"] > 0)]
    .drop_duplicates(subset=id_col)
)

sample = eligible.sample(
    n=N_REQUESTS,
    random_state=SEED,
).reset_index(drop=True)

business_days = pd.bdate_range(START_DATE, END_DATE)

rows = []

for i, cust in sample.iterrows():

    contract = cust[contract_col]

    probs = REASON_BY_CONTRACT.get(contract, DEFAULT_REASON_PROBS)
    reason = rng.choice(list(probs.keys()), p=list(probs.values()))

    discount = int(
        rng.choice(
            DISCOUNT_OPTIONS,
            p=DISCOUNT_WEIGHTS_BY_REASON[reason],
        )
    )

    day = rng.choice(business_days)
    timestamp = (
        pd.Timestamp(day)
        + pd.Timedelta(
            hours=int(rng.integers(8, 18)),
            minutes=int(rng.integers(0, 60)),
        )
    )

    rows.append(
        {
            "request_id": f"DR-{i + 1:04d}",
            "customer_id": cust[id_col],
            "request_timestamp": timestamp,
            "request_date": timestamp.date(),
            "requested_discount_pct": discount,
            "reason": reason,
            "current_monthly_charge": round(float(cust["MonthlyCharges"]), 2),
            "contract_type": contract,
            "tenure_months": int(cust["tenure"]),
        }
    )

requests = (
    pd.DataFrame(rows)
    .sort_values("request_timestamp")
    .reset_index(drop=True)
)

# ------------------------------------------------------------
# Integrity checks (same discipline as the billing controls)
# ------------------------------------------------------------
assert requests["request_id"].is_unique
assert requests["customer_id"].is_unique
assert requests["requested_discount_pct"].between(5, 30).all()
assert (requests["current_monthly_charge"] > 0).all()

PROCESSED.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

requests.to_csv(PROCESSED / "discount_requests.csv", index=False)

print("=" * 70)
print("PHASE 3.1 — DISCOUNT REQUEST GENERATOR")
print("=" * 70)
print(f"\nRequests generated: {len(requests):,}")
print(f"Date range: {requests['request_date'].min()} to {requests['request_date'].max()}")

print("\nBy reason:")
print(requests["reason"].value_counts().to_string())

print("\nBy contract:")
print(requests["contract_type"].value_counts().to_string())

print("\nRequested discount %:")
print(requests["requested_discount_pct"].value_counts().sort_index().to_string())

print("\nAvg requested discount by reason:")
print(
    requests.groupby("reason")["requested_discount_pct"]
    .mean().round(1).to_string()
)

print("\nSample rows:")
print(requests.head(5).to_string(index=False))

print("\nSaved: data/processed/discount_requests.csv")