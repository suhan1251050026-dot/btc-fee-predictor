"""Unit 4: Confidence interval for the mean fee.

Analogy: you cannot see the true average fee. You throw a net over it.
A 95% net catches the true value in 95 of 100 repeated studies.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from src.common import ensure_dir, fee_rows, sample_sd


def mean_ci(values, confidence=0.95):
    """t-interval: mean +/- t * s / sqrt(n). The formula is written by hand."""
    x = np.asarray(values, dtype=float)
    n = len(x)
    mean = float(x.mean())
    s = sample_sd(x)
    se = s / np.sqrt(n)  # standard error of the mean
    t_crit = float(stats.t.ppf(1 - (1 - confidence) / 2, n - 1))
    margin = t_crit * se
    return {
        "n": n,
        "mean": mean,
        "sd": s,
        "std_error": float(se),
        "t_critical": t_crit,
        "margin": float(margin),
        "lower": mean - float(margin),
        "upper": mean + float(margin),
        "confidence": confidence,
    }


def run(df, out_dir):
    out = ensure_dir(out_dir)
    d = fee_rows(df)
    raw = mean_ci(d["avg_fee"])
    log = mean_ci(np.log(d["avg_fee"]))
    # Back-transform: exp(mean of log fee) is the geometric mean. It is NOT the arithmetic mean.
    log["geometric_mean_fee"] = float(np.exp(log["mean"]))
    log["geometric_lower"] = float(np.exp(log["lower"]))
    log["geometric_upper"] = float(np.exp(log["upper"]))

    check = stats.t.interval(
        0.95, raw["n"] - 1, loc=raw["mean"], scale=stats.sem(d["avg_fee"])
    )
    raw["check_scipy_lower_diff"] = float(abs(check[0] - raw["lower"]))

    pd.DataFrame({"raw_fee": raw, "log_fee": log}).to_csv(
        out / "confidence_interval.csv"
    )

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.errorbar(
        [raw["mean"]], [0], xerr=[[raw["margin"]], [raw["margin"]]], fmt="o", capsize=6
    )
    ax.set_yticks([])
    ax.set_title(
        f"95% CI for mean fee: {raw['lower']:.1f} to {raw['upper']:.1f} (n = {raw['n']})"
    )
    ax.set_xlabel("avg_fee (satoshi per transaction)")
    fig.tight_layout()
    fig.savefig(out / "confidence_interval.png", dpi=150)
    plt.close(fig)
    return {"raw_fee": raw, "log_fee": log}
