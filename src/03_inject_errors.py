import numpy as np
import pandas as pd
from config import PROCESSED, INTERIM, SEED, INJECTION_RATE, DERIVED_COLS

rng = np.random.default_rng(SEED)
clean = pd.read_csv(PROCESSED / "customers_clean.csv")

test = clean.drop(columns=DERIVED_COLS).copy()
n = len(test)
test.insert(0, "record_id", np.arange(1, n + 1))

truth = test[["record_id", "MonthlyCharges", "TotalCharges"]].rename(
    columns={"MonthlyCharges": "orig_monthly", "TotalCharges": "orig_total"})
truth["injected_error_type"] = "none"

n_inject = int(n * INJECTION_RATE)
eligible = test.index[test["tenure"] > 0].to_numpy()
picked = rng.choice(eligible, size=n_inject, replace=False)
g0, g1, g2, g3, g4 = np.array_split(picked, 5)

# 1 overbilled monthly charge (+10% to +35%)
test.loc[g0, "MonthlyCharges"] = (
    test.loc[g0, "MonthlyCharges"] * rng.uniform(1.10, 1.35, len(g0))).round(2)
truth.loc[g0, "injected_error_type"] = "overbilled_monthly"

# 2 unbilled: monthly charge zeroed while services remain active
test.loc[g1, "MonthlyCharges"] = 0.0
truth.loc[g1, "injected_error_type"] = "zero_monthly"

# 3 missing cumulative total
test.loc[g2, "TotalCharges"] = np.nan
truth.loc[g2, "injected_error_type"] = "total_missing"

# 4 decimal-shift error on cumulative total (x10 or /10)
test.loc[g3, "TotalCharges"] = (
    test.loc[g3, "TotalCharges"] * rng.choice([0.1, 10.0], len(g3))).round(2)
truth.loc[g3, "injected_error_type"] = "total_decimal_shift"

# 5 duplicate customer records appended as new rows
dups = test.loc[g4].copy()
dups["record_id"] = np.arange(n + 1, n + 1 + len(dups))
dup_truth = dups[["record_id", "MonthlyCharges", "TotalCharges"]].rename(
    columns={"MonthlyCharges": "orig_monthly", "TotalCharges": "orig_total"})
dup_truth["injected_error_type"] = "duplicate_record"
test = pd.concat([test, dups], ignore_index=True)
truth = pd.concat([truth, dup_truth], ignore_index=True)

INTERIM.mkdir(parents=True, exist_ok=True)
test.to_csv(PROCESSED / "billing_test_set.csv", index=False)
truth.to_csv(INTERIM / "ground_truth.csv", index=False)

print("Test set rows:", len(test))
print(truth["injected_error_type"].value_counts())
print("Injected error rate:",
      round((truth["injected_error_type"] != "none").mean() * 100, 2), "%")