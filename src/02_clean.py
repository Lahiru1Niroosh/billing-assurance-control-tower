import numpy as np
import pandas as pd
from config import RAW, PROCESSED, REPORTS

audit = []

def record(rule, n, action):
    audit.append({"rule": rule, "rows_affected": int(n), "action": action})

df = pd.read_csv(RAW, dtype=str, keep_default_na=False)
df.columns = [c.strip() for c in df.columns]
for c in df.columns:
    df[c] = df[c].str.strip()

# --- types ---
df["tenure"] = pd.to_numeric(df["tenure"]).astype(int)
df["MonthlyCharges"] = pd.to_numeric(df["MonthlyCharges"])
tc = pd.to_numeric(df["TotalCharges"], errors="coerce")
record("TotalCharges blank/non-numeric", tc.isna().sum(), "converted to NaN")
df["TotalCharges"] = tc

# --- business rule: tenure 0 + blank total = new customer, not yet billed ---
new_unbilled = (df["tenure"] == 0) & df["TotalCharges"].isna()
df["is_new_unbilled"] = new_unbilled
df.loc[new_unbilled, "TotalCharges"] = 0.0
record("tenure=0 with blank TotalCharges", new_unbilled.sum(),
       "not an error: first bill pending; TotalCharges set to 0, flagged is_new_unbilled")
record("TotalCharges still missing after rule", df["TotalCharges"].isna().sum(),
       "left as NaN for pre-bill review")

# --- standardise categorical values ---
n_senior = df["SeniorCitizen"].isin(["0", "1"]).sum()
df["SeniorCitizen"] = df["SeniorCitizen"].map({"1": "Yes", "0": "No"})
record("SeniorCitizen 0/1", n_senior, "mapped to No/Yes")

svc = ["OnlineSecurity", "OnlineBackup", "DeviceProtection",
       "TechSupport", "StreamingTV", "StreamingMovies"]
n_ni = sum((df[c] == "No internet service").sum() for c in svc)
for c in svc:
    df[c] = df[c].replace({"No internet service": "No"})
record("'No internet service' in add-on columns", n_ni,
       "mapped to No (InternetService column still carries the truth)")

n_np = (df["MultipleLines"] == "No phone service").sum()
df["MultipleLines"] = df["MultipleLines"].replace({"No phone service": "No"})
record("'No phone service' in MultipleLines", n_np, "mapped to No")

# --- integrity checks ---
dup_ids = df["customerID"].duplicated().sum()
record("duplicate customerID", dup_ids, "none expected in clean base")
assert dup_ids == 0, "Duplicate customer IDs in raw data"

# --- derived business fields ---
df["churn_flag"] = (df["Churn"] == "Yes").astype(int)
df["contract_months"] = df["Contract"].map(
    {"Month-to-month": 1, "One year": 12, "Two year": 24})
df["tenure_band"] = pd.cut(df["tenure"], bins=[-1, 0, 12, 24, 48, 72],
                           labels=["New", "1-12m", "13-24m", "25-48m", "49-72m"])
df["expected_total"] = (df["tenure"] * df["MonthlyCharges"]).round(2)
df["total_variance"] = (df["TotalCharges"] - df["expected_total"]).round(2)
df["variance_pct"] = np.where(df["expected_total"] > 0,
                              df["total_variance"] / df["expected_total"], np.nan)
df["avg_billed_per_month"] = np.where(df["tenure"] > 0,
                                      df["TotalCharges"] / df["tenure"], np.nan)
df["annual_revenue"] = (df["MonthlyCharges"] * 12).round(2)

PROCESSED.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(exist_ok=True)
df.to_csv(PROCESSED / "customers_clean.csv", index=False)
pd.DataFrame(audit).to_csv(REPORTS / "cleaning_audit_log.csv", index=False)

print(pd.DataFrame(audit).to_string(index=False))
print("\nClean rows:", len(df))