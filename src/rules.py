import numpy as np
import pandas as pd
from sklearn.linear_model import HuberRegressor

RATE_FEATURES = ["InternetService", "PhoneService", "MultipleLines", "OnlineSecurity",
                 "OnlineBackup", "DeviceProtection", "TechSupport",
                 "StreamingTV", "StreamingMovies"]

# Policy parameters: tune with the business, not just with statistics
MIN_ABS_RESID = 2.0      # ignore rate residuals smaller than this
SEV_HIGH, SEV_MED = 1000, 250   # exposure tiers


def robust_sigma(x):
    med = np.median(x)
    return 1.4826 * np.median(np.abs(x - med)), med


def apply_rules(df, k_total=6.0, k_rate=4.0, verbose=False):
    df = df.copy()

    # R1: duplicate customer record (later occurrence is the suspect)
    df["flag_duplicate_id"] = df["customerID"].duplicated(keep="first")

    # R2: cumulative total missing/zero for a customer who has been billed
    df["flag_total_missing"] = (
        (df["TotalCharges"].isna() | (df["TotalCharges"] == 0)) & (df["tenure"] > 0))

    # R3: zero monthly charge while a service is active
    has_service = (df["PhoneService"] == "Yes") | (df["InternetService"] != "No")
    df["flag_zero_monthly"] = (df["MonthlyCharges"] <= 0) & has_service

    # R4: TotalCharges vs tenure x MonthlyCharges, tolerance learned from the data
    valid = (df["tenure"] > 0) & (df["MonthlyCharges"] > 0) & (df["TotalCharges"] > 0)
    expected_total = df["tenure"] * df["MonthlyCharges"]
    log_ratio = np.log(df["TotalCharges"] / expected_total.where(valid))
    sig_t, med_t = robust_sigma(log_ratio[valid].to_numpy())
    df["log_ratio"] = log_ratio
    df["flag_total_variance"] = valid & ((log_ratio - med_t).abs() > k_total * sig_t)

    # R5: MonthlyCharges vs reconstructed rate card (robust regression on services)
    X = pd.get_dummies(df[RATE_FEATURES], drop_first=True).astype(float)
    fit_mask = (~df["flag_duplicate_id"]) & (df["MonthlyCharges"] > 0)
    model = HuberRegressor(epsilon=1.35, alpha=0.0, max_iter=2000)
    model.fit(X[fit_mask], df.loc[fit_mask, "MonthlyCharges"])
    df["expected_monthly"] = model.predict(X).round(2)
    resid = df["MonthlyCharges"] - df["expected_monthly"]
    sig_r, med_r = robust_sigma(resid[fit_mask].to_numpy())
    thr = max(MIN_ABS_RESID, k_rate * sig_r)
    df["rate_residual"] = resid.round(2)
    df["flag_rate_mismatch"] = (resid - med_r).abs() > thr

    if verbose:
        print(f"[R4] median log-ratio={med_t:.3f}  robust sigma={sig_t:.3f}  "
              f"threshold=+/-{k_total * sig_t:.3f}")
        r2 = model.score(X[fit_mask], df.loc[fit_mask, "MonthlyCharges"])
        print(f"[R5] rate-card R2={r2:.4f}  residual sigma={sig_r:.3f}  threshold=+/-{thr:.2f}")

    # primary rule (most specific first), all rules fired, exposure, severity
    order = ["duplicate_id", "zero_monthly", "total_missing", "rate_mismatch", "total_variance"]
    flag_cols = [f"flag_{r}" for r in order]
    conds = [df[c] for c in flag_cols]
    df["primary_rule"] = np.select(conds, order, default="none")
    df["rules_fired"] = df[flag_cols].apply(
        lambda r: ",".join(c[5:] for c in flag_cols if r[c]), axis=1)

    exposure_vals = [
        df["MonthlyCharges"] * 12,                      # duplicate: annual double-billing
        df["expected_monthly"] * 12,                    # zero monthly: annual leakage
        df["tenure"] * df["MonthlyCharges"],            # missing total: unverifiable balance
        resid.abs() * 12,                               # rate mismatch: annualised gap
        (df["TotalCharges"] - expected_total).abs(),    # total variance: balance gap
    ]
    df["exposure"] = np.select(conds, exposure_vals, default=0.0).astype(float).round(2)
    df["severity"] = np.select(
        [df["exposure"] >= SEV_HIGH, df["exposure"] >= SEV_MED], ["HIGH", "MEDIUM"],
        default="LOW")
    df.loc[df["primary_rule"] == "none", "severity"] = "NONE"
    return df


def score(res, truth):
    m = res[["record_id", "primary_rule"]].merge(
        truth[["record_id", "injected_error_type"]], on="record_id")
    err = m["injected_error_type"] != "none"
    flg = m["primary_rule"] != "none"
    tp, fp, fn = int((err & flg).sum()), int((~err & flg).sum()), int((err & ~flg).sum())
    return {"flagged": tp + fp, "tp": tp, "fp": fp, "fn": fn,
            "precision": tp / (tp + fp) if tp + fp else 0.0,
            "recall": tp / (tp + fn) if tp + fn else 0.0}