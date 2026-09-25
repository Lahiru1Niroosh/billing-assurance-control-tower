import numpy as np
import pandas as pd

from config import PROCESSED

# ============================================================
# PHASE 3.4
# Discount Approval SLA Simulation (control C005)
#
# All turnaround behaviour is an ASSUMPTION (synthetic operations data).
# Human turnaround is measured in BUSINESS hours (Mon-Fri, 08:00-18:00).
# ============================================================

SEED = 4040
SIGMA = 0.5                        # spread of human turnaround times
CONGESTION_PER_EXTRA_CASE = 0.08   # +8% slower per review case above a typical day
OPEN_HOUR, CLOSE_HOUR = 8, 18
AT_RISK_FRACTION = 0.80            # >=80% of target consumed = "At Risk"

SLA_TARGET_HOURS = {
    "System": 1,
    "Supervisor": 8,
    "Manager": 16,
    "Senior Manager": 24,
}
MEDIAN_TURNAROUND_HOURS = {
    "Supervisor": 4,
    "Manager": 8,
    "Senior Manager": 14,
}


def add_business_hours(start, hours):
    """Advance a timestamp by N working hours, skipping nights and weekends."""
    t = start
    remaining = hours

    while remaining > 1e-9:
        if t.weekday() >= 5:
            t = (t + pd.Timedelta(days=7 - t.weekday())).replace(
                hour=OPEN_HOUR, minute=0, second=0
            )
        if t.hour < OPEN_HOUR:
            t = t.replace(hour=OPEN_HOUR, minute=0, second=0)
        if t.hour >= CLOSE_HOUR:
            t = (t + pd.Timedelta(days=1)).replace(
                hour=OPEN_HOUR, minute=0, second=0
            )
            continue

        close = t.replace(hour=CLOSE_HOUR, minute=0, second=0)
        step = min((close - t).total_seconds() / 3600, remaining)
        t += pd.Timedelta(hours=step)
        remaining -= step

    return t


df = pd.read_csv(
    PROCESSED / "discount_decisions.csv",
    parse_dates=["request_timestamp"],
)

rng = np.random.default_rng(SEED)

df["sla_target_hours"] = df["approval_level"].map(SLA_TARGET_HOURS)

# ------------------------------------------------------------
# Workload effect: busy days slow reviewers down
# ------------------------------------------------------------
is_review = df["decision"].eq("MANAGER_REVIEW")
daily_load = df[is_review].groupby("request_date").size()
typical_load = daily_load.median()

df["daily_review_load"] = (
    df["request_date"].map(daily_load).fillna(0).astype(int)
)

congestion = 1 + CONGESTION_PER_EXTRA_CASE * (
    df["daily_review_load"] - typical_load
).clip(lower=0)

# ------------------------------------------------------------
# Turnaround simulation
# ------------------------------------------------------------
median = df["approval_level"].map(MEDIAN_TURNAROUND_HOURS) * congestion

human_turnaround = np.exp(
    np.log(median) + SIGMA * rng.standard_normal(len(df))
)
system_turnaround = rng.uniform(0.01, 0.10, len(df))

df["turnaround_hours"] = np.where(
    df["approval_level"].eq("System"),
    system_turnaround,
    human_turnaround,
).round(2)


def decision_time(row):
    if row["approval_level"] == "System":
        return row["request_timestamp"] + pd.Timedelta(hours=row["turnaround_hours"])
    return add_business_hours(row["request_timestamp"], row["turnaround_hours"])


df["decision_timestamp"] = df.apply(decision_time, axis=1)

df["sla_status"] = np.select(
    [
        df["turnaround_hours"] > df["sla_target_hours"],
        df["turnaround_hours"] >= AT_RISK_FRACTION * df["sla_target_hours"],
    ],
    ["Breached", "At Risk"],
    default="Met",
)

df["breach_hours"] = (
    df["turnaround_hours"] - df["sla_target_hours"]
).clip(lower=0).round(2)

# ------------------------------------------------------------
# Integrity checks
# ------------------------------------------------------------
assert (df["decision_timestamp"] >= df["request_timestamp"]).all()
assert (df.loc[df["approval_level"] == "System", "sla_status"] == "Met").all()
assert df["sla_status"].notna().all()

df["request_month"] = df["request_timestamp"].dt.to_period("M").astype(str)

df.to_csv(PROCESSED / "discount_decisions_sla.csv", index=False)

# ------------------------------------------------------------
# Report
# ------------------------------------------------------------
n = len(df)
met = int((df["sla_status"] == "Met").sum())
at_risk = int((df["sla_status"] == "At Risk").sum())
breaches = int((df["sla_status"] == "Breached").sum())
dec = df["decision"].value_counts()

print("=" * 70)
print("PHASE 3.4 — DISCOUNT APPROVAL SLA")
print("=" * 70)

print("\nHEADLINE")
print(f"  Requests           : {n}")
print(f"  Auto-approved      : {dec.get('AUTO_APPROVE', 0)}")
print(f"  Manager review     : {dec.get('MANAGER_REVIEW', 0)}")
print(f"  Declined           : {dec.get('DECLINE', 0)}")
print(f"  SLA met rate       : {met / n:.1%}")
print(f"  Non-breach rate    : {(met + at_risk) / n:.1%}")
print(f"  SLA breaches       : {breaches}")
print(f"  At risk            : {at_risk}")
print(f"  Avg turnaround (all)     : {df['turnaround_hours'].mean():.2f} h")
print(f"  Avg turnaround (reviews) : {df.loc[is_review, 'turnaround_hours'].mean():.2f} business h")

print("\nBY APPROVAL LEVEL")
lvl = df.groupby("approval_level").agg(
    requests=("request_id", "count"),
    met=("sla_status", lambda s: (s == "Met").sum()),
    at_risk=("sla_status", lambda s: (s == "At Risk").sum()),
    target_h=("sla_target_hours", "first"),
    avg_turnaround_h=("turnaround_hours", "mean"),
    breaches=("sla_status", lambda s: (s == "Breached").sum()),
).round(2)
lvl["sla_met_rate"] = (lvl["met"] / lvl["requests"]).round(3)
lvl["non_breach_rate"] = (
    (lvl["met"] + lvl["at_risk"]) / lvl["requests"]
).round(3)
print(lvl.to_string())

print("\nBY MONTH")
mon = df.groupby("request_month").agg(
    requests=("request_id", "count"),
    met=("sla_status", lambda s: (s == "Met").sum()),
    at_risk=("sla_status", lambda s: (s == "At Risk").sum()),
    review_cases=("decision", lambda s: (s == "MANAGER_REVIEW").sum()),
    breaches=("sla_status", lambda s: (s == "Breached").sum()),
)
mon["sla_met_rate"] = (mon["met"] / mon["requests"]).round(3)
mon["non_breach_rate"] = (
    (mon["met"] + mon["at_risk"]) / mon["requests"]
).round(3)
print(mon.to_string())

print("\nDOES WORKLOAD DRIVE BREACHES? (avg same-day review cases, review requests)")
print(df[is_review].groupby("sla_status")["daily_review_load"].mean().round(2).to_string())

print("\nSAMPLE BREACHES")
print(
    df[df["sla_status"] == "Breached"][[
        "request_id", "decision", "approval_level", "sla_target_hours",
        "turnaround_hours", "breach_hours", "request_timestamp", "decision_timestamp",
    ]].head(5).to_string(index=False)
)

print("\nSaved: data/processed/discount_decisions_sla.csv")