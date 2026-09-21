import numpy as np
import pandas as pd

from config import PROCESSED, INTERIM, REPORTS
from rules import apply_rules


SEED = 909
LEVELS = [0.02, 0.05, 0.10, 0.20]
SAMPLE_SIZE = 150


base = pd.read_csv(
    PROCESSED / "customers_clean.csv"
)

rng = np.random.default_rng(SEED)

eligible = base.index[
    (base["tenure"] > 0)
    & (base["MonthlyCharges"] > 0)
].to_numpy()


rows = []

for level in LEVELS:

    selected = rng.choice(
        eligible,
        size=SAMPLE_SIZE,
        replace=False
    )

    test = base.copy()

    test = test.drop(
        columns=[
            "expected_total",
            "total_variance",
            "variance_pct",
            "avg_billed_per_month",
            "annual_revenue",
        ],
        errors="ignore"
    )

    original = (
        test.loc[selected, "MonthlyCharges"]
        .copy()
    )

    test.loc[selected, "MonthlyCharges"] = (
        original * (1 + level)
    ).round(2)

    results = apply_rules(
        test,
        k_total=10,
        k_rate=4
    )

    detected = (
        results.loc[selected, "primary_rule"]
        != "none"
    )

    recall = detected.mean()

    rows.append(
        {
            "overcharge_level": level,
            "sample_size": SAMPLE_SIZE,
            "detected": int(detected.sum()),
            "missed": int((~detected).sum()),
            "recall": recall,
        }
    )


curve = pd.DataFrame(rows)

REPORTS.mkdir(
    parents=True,
    exist_ok=True
)

curve.to_csv(
    REPORTS / "overbilling_difficulty_curve.csv",
    index=False
)

print("\nOVERBILLING DIFFICULTY CURVE")
print("=" * 60)

print(
    curve.to_string(index=False)
)