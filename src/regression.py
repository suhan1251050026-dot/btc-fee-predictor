"""Unit 4: Regression and standard error of estimate - predict the fee.

Analogy: predict a taxi fare from the distance. Draw the best straight line through the points.
The standard error of estimate is the typical miss of a dart around the target.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from src.common import ensure_dir, fee_rows


def least_squares(x, y):
    """Fit y = a + b*x by least squares. Every formula is written by hand."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    xbar, ybar = x.mean(), y.mean()
    sxx = np.sum((x - xbar) ** 2)
    sxy = np.sum((x - xbar) * (y - ybar))
    syy = np.sum((y - ybar) ** 2)
    b = sxy / sxx
    a = ybar - b * xbar
    r = sxy / np.sqrt(sxx * syy) if syy > 0 else float("nan")
    sse = float(np.sum((y - (a + b * x)) ** 2))
    se_est = float(np.sqrt(sse / (n - 2)))  # standard error of estimate
    return {
        "n": n,
        "intercept_a": float(a),
        "slope_b": float(b),
        "correlation_r": float(r),
        "r_squared": float(r**2) if not np.isnan(r) else float("nan"),
        "std_error_of_estimate": se_est,
    }


def run(df, out_dir):
    out = ensure_dir(out_dir)
    d = fee_rows(df)
    x = d["tx_count"].to_numpy()
    y_raw = d["avg_fee"].to_numpy()
    y_log = np.log(y_raw)

    raw = least_squares(x, y_raw)
    log = least_squares(x, y_log)

    check = stats.linregress(x, y_log)  # check only. The numbers above are our own.
    log["check_scipy_slope_diff"] = float(abs(check.slope - log["slope_b"]))
    log["slope_p_value"] = float(check.pvalue)

    pd.DataFrame({"raw_fee": raw, "log_fee": log}).round(6).to_csv(
        out / "regression.csv"
    )

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for ax, y, res, name in (
        (axes[0], y_raw, raw, "avg_fee (raw)"),
        (axes[1], y_log, log, "log(avg_fee)"),
    ):
        ax.scatter(x, y, s=6, alpha=0.4)
        xs = np.array([x.min(), x.max()])
        ax.plot(xs, res["intercept_a"] + res["slope_b"] * xs, "r-")
        ax.set_title(
            f"{name}: R2 = {res['r_squared']:.3f}, SE = {res['std_error_of_estimate']:.3g}"
        )
        ax.set_xlabel("transactions in block")
        ax.set_ylabel(name)
    fig.tight_layout()
    fig.savefig(out / "regression.png", dpi=150)
    plt.close(fig)
    return {"raw_fee": raw, "log_fee": log}


def predict(result_model, tx_count):
    """Predict with a fitted model dict from least_squares()."""
    return result_model["intercept_a"] + result_model["slope_b"] * tx_count
