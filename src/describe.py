"""Unit 1: Descriptive statistics (the health report of the data).

Analogy: before a doctor treats you, the doctor checks height, weight, and pulse.
We do the same for the data: centre, spread, and shape.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.common import ensure_dir, fee_rows, sample_sd


def summarize(values):
    """Mean, median, SD, coefficient of variation (CV), min, max. All by hand."""
    x = np.sort(np.asarray(values, dtype=float))
    n = len(x)
    mean = float(x.sum() / n)
    mid = n // 2
    median = float(x[mid]) if n % 2 == 1 else float((x[mid - 1] + x[mid]) / 2)
    sd = sample_sd(x)
    return {
        "n": n,
        "mean": mean,
        "median": median,
        "sd": sd,
        "cv_percent": sd / mean * 100 if mean != 0 else float("nan"),
        "min": float(x[0]),
        "max": float(x[-1]),
    }


def run(df, out_dir):
    out = ensure_dir(out_dir)
    d = fee_rows(df)
    rows = {}
    for col in ("tx_count", "size", "avg_fee"):
        rows[col] = summarize(d[col])
    rows["log_avg_fee"] = summarize(np.log(d["avg_fee"]))
    table = pd.DataFrame(rows).T
    table.round(4).to_csv(out / "descriptive.csv")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].hist(d["avg_fee"], bins=50)
    axes[0].set_title("Average fee per block (raw, skewed)")
    axes[0].set_xlabel("avg_fee (satoshi per transaction)")
    axes[1].hist(np.log(d["avg_fee"]), bins=50)
    axes[1].set_title("Log of average fee (closer to symmetric)")
    axes[1].set_xlabel("log(avg_fee)")
    fig.tight_layout()
    fig.savefig(out / "hist_fee.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(5, 4))
    ax.boxplot(np.log(d["avg_fee"]), tick_labels=["log(avg_fee)"])
    ax.set_title("Box plot of log fee")
    fig.tight_layout()
    fig.savefig(out / "box_fee.png", dpi=150)
    plt.close(fig)
    return rows
