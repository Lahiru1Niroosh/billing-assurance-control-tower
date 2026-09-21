import pandas as pd
from config import PROCESSED, REPORTS
from rules import apply_rules

df = pd.read_csv(PROCESSED / "billing_test_set.csv")
assert "injected_error_type" not in df.columns, "Label leak: rules must not see ground truth"

res = apply_rules(df, verbose=True)
res.to_csv(PROCESSED / "validation_results.csv", index=False)

cols = ["record_id", "customerID", "primary_rule", "rules_fired", "severity", "exposure",
        "tenure", "MonthlyCharges", "expected_monthly", "TotalCharges",
        "Contract", "PaymentMethod"]
queue = (res[res["primary_rule"] != "none"]
         .sort_values("exposure", ascending=False)[cols])
REPORTS.mkdir(exist_ok=True)
queue.to_csv(REPORTS / "exception_queue.csv", index=False)

print("\nExceptions by rule:\n", queue["primary_rule"].value_counts())
print("\nRule x severity:\n", pd.crosstab(queue["primary_rule"], queue["severity"]))
print("\nTotal exceptions:", len(queue), " Total exposure:", round(queue["exposure"].sum(), 2))