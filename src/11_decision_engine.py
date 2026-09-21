import numpy as np
import pandas as pd

from config import PROCESSED

# ============================================================
# PHASE 3.3
# Discount Decision Engine (control C004)
#
# Policy thresholds are derived from break-even economics:
#   Benefit-Cost Ratio (BCR) = 1.0 is break-even.
#   Our inputs are assumptions, so we require a 50% margin
#   of safety on both sides:
#       BCR >= 1.5  -> clearly attractive
#       BCR <  0.5  -> clearly uneconomic
#       in between  -> human judgement
# ============================================================

AUTO_MIN_BCR = 1.5          # margin of safety above break-even
AUTO_MAX_PCT = 15           # largest discount the system may approve alone
AUTO_MAX_COST = 150         # largest 12-month cost the system may approve alone
DECLINE_MAX_BCR = 0.5       # recovers less than half the cost
STRATEGIC_CHURN_TRIGGER = 0.20   # strategic customer AND at real risk
MANAGER_PCT_LIMIT = 20      # above this, a manager must decide

# rule_id -> (decision, approval_level)
RULES = {
    "R1_AUTO_APPROVE":         ("AUTO_APPROVE",   "System"),
    "R2_STRATEGIC_ESCALATION": ("MANAGER_REVIEW", "Senior Manager"),
    "R3_DECLINE_UNECONOMIC":   ("DECLINE",        "System"),
    "R4_REVIEW_OVER_LIMIT":    ("MANAGER_REVIEW", "Manager"),
    "R5_REVIEW_MARGINAL":      ("MANAGER_REVIEW", "Supervisor"),
}


def classify(df, bcr_mult=1.0):
    """First matching rule wins. bcr_mult is used for sensitivity tests."""
    bcr = df["benefit_cost_ratio"] * bcr_mult
    pct = df["requested_discount_pct"]
    cost = df["discount_cost"]

    strategic_at_risk = (
        df["value_tier"].eq("Strategic")
        & (df["baseline_churn_risk"] >= STRATEGIC_CHURN_TRIGGER)
    )

    conditions = [
        (bcr >= AUTO_MIN_BCR) & (pct <= AUTO_MAX_PCT) & (cost <= AUTO_MAX_COST),
        strategic_at_risk,
        bcr < DECLINE_MAX_BCR,
        pct > MANAGER_PCT_LIMIT,
    ]

    return pd.Series(
        np.select(conditions, list(RULES.keys())[:4], default="R5_REVIEW_MARGINAL"),
        index=df.index,
    )


def explain(row):
    bcr = row["benefit_cost_ratio"]
    pct = row["requested_discount_pct"]
    cost = row["discount_cost"]
    rule = row["decision_rule"]

    if rule == "R1_AUTO_APPROVE":
        detail = (f"benefit-cost ratio {bcr:.2f} clears the {AUTO_MIN_BCR} threshold; "
                  f"{pct}% discount (${cost:,.0f} over 12 months) is within auto-approval limits.")
    elif rule == "R2_STRATEGIC_ESCALATION":
        detail = (f"strategic-value customer with elevated churn risk "
                  f"({row['baseline_churn_risk']:.0%}); escalated to senior manager. "
                  f"Benefit-cost ratio {bcr:.2f}.")
    elif rule == "R3_DECLINE_UNECONOMIC":
        detail = (f"estimated retention value recovers only {bcr:.0%} of the "
                  f"${cost:,.0f} discount cost (minimum {DECLINE_MAX_BCR:.0%}).")
    elif rule == "R4_REVIEW_OVER_LIMIT":
        detail = (f"requested {pct}% exceeds the {MANAGER_PCT_LIMIT}% discount limit; "
                  f"economics ({bcr:.2f}x) justify review rather than decline.")
    else:
        detail = (f"benefit-cost ratio {bcr:.2f}, discount {pct}% (${cost:,.0f}); "
                  f"outside auto-approval limits but not clearly uneconomic.")

    return f"{row['decision'].replace('_', ' ')} — {detail}"


df = pd.read_csv(PROCESSED / "discount_requests_enriched.csv")

df["decision_rule"] = classify(df)
df["decision"] = df["decision_rule"].map(lambda r: RULES[r][0])
df["approval_level"] = df["decision_rule"].map(lambda r: RULES[r][1])
df["decision_reason"] = df.apply(explain, axis=1)

# ------------------------------------------------------------
# Integrity checks: the policy must never contradict the economics
# ------------------------------------------------------------
auto = df[df["decision"] == "AUTO_APPROVE"]
declined = df[df["decision"] == "DECLINE"]
assert (auto["net_economic_impact"] > 0).all(), "auto-approved a loss-making request"
assert (declined["net_economic_impact"] < 0).all(), "declined a profitable request"
assert df["decision_reason"].notna().all()

df.to_csv(PROCESSED / "discount_decisions.csv", index=False)

# ------------------------------------------------------------
# Report
# ------------------------------------------------------------
print("=" * 70)
print("PHASE 3.3 — DISCOUNT DECISION ENGINE")
print("=" * 70)

print("\nDECISIONS")
dec = df["decision"].value_counts()
print(pd.DataFrame({"requests": dec, "share": (dec / len(df)).round(3)}).to_string())

print("\nBY RULE")
print(df.groupby(["decision", "decision_rule"]).size().to_string())

print("\nBY APPROVAL LEVEL")
print(df["approval_level"].value_counts().to_string())

print("\nDECISION BY CONTRACT")
print(pd.crosstab(df["contract_type"], df["decision"]).to_string())

print("\nFINANCIAL VIEW BY DECISION")
fin = df.groupby("decision").agg(
    requests=("request_id", "count"),
    discount_cost=("discount_cost", "sum"),
    retention_value=("estimated_retention_value", "sum"),
    net_impact=("net_economic_impact", "sum"),
).round(0)
print(fin.to_string())

net = df.groupby("decision")["net_economic_impact"].sum()
approve_all = df["net_economic_impact"].sum()
policy_low = net.get("AUTO_APPROVE", 0)
policy_high = net.get("AUTO_APPROVE", 0) + net.get("MANAGER_REVIEW", 0)

print("\nPOLICY VS APPROVE-EVERYTHING (net economic impact)")
print(f"  Approve every request                 : ${approve_all:,.0f}")
print(f"  Policy, review queue all rejected     : ${policy_low:,.0f}")
print(f"  Policy, review queue all approved     : ${policy_high:,.0f}")
print(f"  Value destroyed avoided by declines   : ${-net.get('DECLINE', 0):,.0f}")

print("\nSENSITIVITY: what if our retention-value assumptions are off?")
sens = {}
for m in [0.8, 1.0, 1.2]:
    d = classify(df, m).map(lambda r: RULES[r][0])
    sens[f"retention x{m}"] = d.value_counts()
print(pd.DataFrame(sens).fillna(0).astype(int).to_string())

print("\nSAMPLE EXPLANATIONS (one per rule)")
for rule in RULES:
    match = df[df["decision_rule"] == rule]
    if len(match):
        r = match.iloc[0]
        print(f"\n[{rule}] {r['request_id']}")
        print(f"  {r['decision_reason']}")

print("\nSaved: data/processed/discount_decisions.csv")