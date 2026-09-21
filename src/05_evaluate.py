import numpy as np
import pandas as pd
from config import PROCESSED, INTERIM, REPORTS
from rules import score

res = pd.read_csv(PROCESSED / "validation_results.csv")
truth = pd.read_csv(INTERIM / "ground_truth.csv")

m = res.merge(truth, on="record_id", how="left")
m["is_error"] = m["injected_error_type"] != "none"
m["is_flagged"] = m["primary_rule"] != "none"

s = score(res, truth)
print("OVERALL:", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items()})

errs = m[m["is_error"]]
by_type = errs.groupby("injected_error_type").agg(
    records=("record_id", "count"), detected=("is_flagged", "sum"))
by_type["recall"] = (by_type["detected"] / by_type["records"]).round(3)
print("\nDetection by injected error type:\n", by_type)

flag_cols = [c for c in m.columns if c.startswith("flag_")]
print("\nWhich rules fired on each error type:\n",
      errs.groupby("injected_error_type")[flag_cols].sum())

fp = m[~m["is_error"] & m["is_flagged"]]
print("\nFalse positives by rule:\n", fp["primary_rule"].value_counts())

# value-weighted recall: how much money-at-stake did we catch?
t = m["injected_error_type"]
gap = np.select(
    [t == "overbilled_monthly", t == "zero_monthly", t == "total_missing",
     t == "total_decimal_shift", t == "duplicate_record"],
    [(m["MonthlyCharges"] - m["orig_monthly"]).abs() * 12, m["orig_monthly"] * 12,
     m["orig_total"], (m["TotalCharges"] - m["orig_total"]).abs(), m["orig_monthly"] * 12],
    default=0.0)
m["error_value"] = gap
caught = m.loc[m["is_flagged"], "error_value"].sum()
total = m["error_value"].sum()
print(f"\nValue-weighted recall: {caught / total:.1%}  (caught {caught:,.0f} of {total:,.0f})")

REPORTS.mkdir(exist_ok=True)
by_type.to_csv(REPORTS / "evaluation_by_type.csv")