import itertools
import pandas as pd
from config import PROCESSED, INTERIM, REPORTS
from rules import apply_rules, score

df = pd.read_csv(PROCESSED / "billing_test_set.csv")
truth = pd.read_csv(INTERIM / "ground_truth.csv")

rows = []
for k_total, k_rate in itertools.product([3, 6, 10], [2, 3, 4, 5, 6]):
    s = score(apply_rules(df, k_total, k_rate), truth)
    rows.append({"k_total": k_total, "k_rate": k_rate, **s})

out = pd.DataFrame(rows)
out["f1"] = 2 * out["precision"] * out["recall"] / (out["precision"] + out["recall"])
out = out.round(3)
REPORTS.mkdir(exist_ok=True)
out.to_csv(REPORTS / "threshold_sweep.csv", index=False)
print(out.to_string(index=False))