import itertools
import numpy as np
import pandas as pd

from config import PROCESSED, INTERIM, REPORTS
from rules import apply_rules, score


# ============================================================
# PHASE 2B
# Independent Hold-Out Validation
# ============================================================

BASE_SEED = 2026
INJECTION_RATE = 0.03


def create_holdout(base_df, seed=BASE_SEED):
    """
    Create a fresh synthetic validation set using a different seed.

    The important principle:
    Phase 2 thresholds were selected before this dataset is evaluated.
    """

    rng = np.random.default_rng(seed)

    test = base_df.copy()

    test = test.drop(
        columns=[
            "expected_total",
            "total_variance",
            "variance_pct",
            "avg_billed_per_month",
            "annual_revenue",
        ],
        errors="ignore",
    )

    test.insert(
        0,
        "record_id",
        np.arange(1, len(test) + 1)
    )

    truth = test[
        ["record_id", "MonthlyCharges", "TotalCharges"]
    ].rename(
        columns={
            "MonthlyCharges": "orig_monthly",
            "TotalCharges": "orig_total",
        }
    )

    truth["injected_error_type"] = "none"

    eligible = test.index[
        test["tenure"] > 0
    ].to_numpy()

    n_inject = int(len(test) * INJECTION_RATE)

    selected = rng.choice(
        eligible,
        size=n_inject,
        replace=False
    )

    groups = np.array_split(selected, 5)

    # --------------------------------------------------------
    # 1. Overbilling
    # --------------------------------------------------------

    g0 = groups[0]

    test.loc[g0, "MonthlyCharges"] = (
        test.loc[g0, "MonthlyCharges"]
        * rng.uniform(1.10, 1.35, len(g0))
    ).round(2)

    truth.loc[g0, "injected_error_type"] = "overbilled_monthly"

    # --------------------------------------------------------
    # 2. Zero monthly charge
    # --------------------------------------------------------

    g1 = groups[1]

    test.loc[g1, "MonthlyCharges"] = 0.0

    truth.loc[g1, "injected_error_type"] = "zero_monthly"

    # --------------------------------------------------------
    # 3. Missing total
    # --------------------------------------------------------

    g2 = groups[2]

    test.loc[g2, "TotalCharges"] = np.nan

    truth.loc[g2, "injected_error_type"] = "total_missing"

    # --------------------------------------------------------
    # 4. Decimal shift
    # --------------------------------------------------------

    g3 = groups[3]

    test.loc[g3, "TotalCharges"] = (
        test.loc[g3, "TotalCharges"]
        * rng.choice(
            [0.1, 10.0],
            len(g3)
        )
    ).round(2)

    truth.loc[g3, "injected_error_type"] = "total_decimal_shift"

    # --------------------------------------------------------
    # 5. Duplicate records
    # --------------------------------------------------------

    g4 = groups[4]

    duplicates = test.loc[g4].copy()

    duplicates["record_id"] = np.arange(
        len(test) + 1,
        len(test) + 1 + len(duplicates)
    )

    duplicate_truth = duplicates[
        ["record_id", "MonthlyCharges", "TotalCharges"]
    ].rename(
        columns={
            "MonthlyCharges": "orig_monthly",
            "TotalCharges": "orig_total",
        }
    )

    duplicate_truth["injected_error_type"] = "duplicate_record"

    test = pd.concat(
        [test, duplicates],
        ignore_index=True
    )

    truth = pd.concat(
        [truth, duplicate_truth],
        ignore_index=True
    )

    return test, truth


def calculate_metrics(results, truth):

    merged = results.merge(
        truth,
        on="record_id",
        how="left"
    )

    merged["is_error"] = (
        merged["injected_error_type"] != "none"
    )

    merged["is_flagged"] = (
        merged["primary_rule"] != "none"
    )

    tp = (
        merged["is_error"]
        & merged["is_flagged"]
    ).sum()

    fp = (
        ~merged["is_error"]
        & merged["is_flagged"]
    ).sum()

    fn = (
        merged["is_error"]
        & ~merged["is_flagged"]
    ).sum()

    tn = (
        ~merged["is_error"]
        & ~merged["is_flagged"]
    ).sum()

    precision = (
        tp / (tp + fp)
        if (tp + fp) > 0
        else 0
    )

    recall = (
        tp / (tp + fn)
        if (tp + fn) > 0
        else 0
    )

    specificity = (
        tn / (tn + fp)
        if (tn + fp) > 0
        else 0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0
    )

    return {
        "records": len(merged),
        "errors": int(merged["is_error"].sum()),
        "flagged": int(merged["is_flagged"].sum()),
        "tp": int(tp),
        "fp": int(fp),
        "fn": int(fn),
        "tn": int(tn),
        "precision": precision,
        "recall": recall,
        "specificity": specificity,
        "f1": f1,
    }


# ============================================================
# MAIN
# ============================================================

print("=" * 70)
print("PHASE 2B — INDEPENDENT HOLD-OUT VALIDATION")
print("=" * 70)

base = pd.read_csv(
    PROCESSED / "customers_clean.csv"
)

holdout, truth = create_holdout(base)

INTERIM.mkdir(
    parents=True,
    exist_ok=True
)

holdout.to_csv(
    INTERIM / "holdout_test_set.csv",
    index=False
)

truth.to_csv(
    INTERIM / "holdout_ground_truth.csv",
    index=False
)

print(f"\nHold-out rows: {len(holdout):,}")
print(
    "Injected errors:",
    int((truth["injected_error_type"] != "none").sum())
)

print("\nError distribution:")
print(
    truth["injected_error_type"]
    .value_counts()
)

# ============================================================
# FIXED OPERATING POINT
# ============================================================

K_TOTAL = 10
K_RATE = 4

results = apply_rules(
    holdout,
    k_total=K_TOTAL,
    k_rate=K_RATE,
    verbose=True
)

metrics = calculate_metrics(
    results,
    truth
)

print("\n" + "=" * 70)
print("HOLD-OUT PERFORMANCE")
print("=" * 70)

for key, value in metrics.items():

    if isinstance(value, float):

        print(
            f"{key:15}: {value:.3%}"
        )

    else:

        print(
            f"{key:15}: {value:,}"
        )


# ============================================================
# ERROR-TYPE PERFORMANCE
# ============================================================

merged = results.merge(
    truth,
    on="record_id"
)

merged["is_error"] = (
    merged["injected_error_type"] != "none"
)

merged["is_flagged"] = (
    merged["primary_rule"] != "none"
)

error_rows = merged[
    merged["is_error"]
]

by_type = (
    error_rows
    .groupby("injected_error_type")
    .agg(
        records=("record_id", "count"),
        detected=("is_flagged", "sum")
    )
)

by_type["recall"] = (
    by_type["detected"]
    / by_type["records"]
)

print("\n" + "=" * 70)
print("DETECTION BY ERROR TYPE")
print("=" * 70)

print(
    by_type.to_string()
)


# ============================================================
# SAVE RESULTS
# ============================================================

REPORTS.mkdir(
    parents=True,
    exist_ok=True
)

pd.DataFrame(
    [metrics]
).to_csv(
    REPORTS / "holdout_summary.csv",
    index=False
)

by_type.to_csv(
    REPORTS / "holdout_detection_by_type.csv"
)

results.to_csv(
    PROCESSED / "holdout_validation_results.csv",
    index=False
)


print("\nSaved:")
print("  reports/holdout_summary.csv")
print("  reports/holdout_detection_by_type.csv")
print("  data/processed/holdout_validation_results.csv")