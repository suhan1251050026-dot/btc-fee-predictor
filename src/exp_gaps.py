"""Unit 2: Exponential distribution - the waiting time for the next Bitcoin block.

Analogy: you wait for the first raindrop on your hand. The rain has no memory.
Waiting longer does not make a drop "due".
"""

import math

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from src.common import ensure_dir, sample_sd


def block_gaps(timestamps):
    """Gaps in seconds between blocks, taken in TIME order.

    Miners set the timestamps, so a few blocks are out of order by height.
    Dropping the negative gaps would keep their too-long neighbours and push the mean up.
    So we sort the timestamps first. Then no gap is negative, and the mean gap
    equals (last time - first time) / (number of blocks - 1).
    Returns (gaps, number_out_of_order_in_height_order).
    """
    ts = np.asarray(timestamps, dtype=float)
    out_of_order = int((np.diff(ts) < 0).sum())
    gaps = np.diff(np.sort(ts))
    return gaps, out_of_order


def exp_survival(t, mean_gap):
    """P(X > t) = e^(-lambda * t), with lambda = 1 / mean gap."""
    return math.exp(-t / mean_gap)


def exp_cdf(t, mean_gap):
    """P(X <= t) = 1 - e^(-lambda * t)."""
    return 1 - exp_survival(t, mean_gap)


def run(df, out_dir, long_wait_seconds=1200):
    out = ensure_dir(out_dir)
    gaps, out_of_order = block_gaps(df["timestamp"].to_numpy())
    mean_gap = float(gaps.mean())
    sd_gap = sample_sd(gaps)
    lam = 1 / mean_gap

    ks_stat, ks_p = stats.kstest(gaps, "expon", args=(0, mean_gap))
    result = {
        "n_gaps": len(gaps),
        "out_of_order_timestamps": out_of_order,
        "zero_gaps": int((gaps == 0).sum()),
        "mean_gap_s": mean_gap,
        "sd_gap_s": sd_gap,
        "sd_over_mean": sd_gap / mean_gap,  # about 1 for an exponential model
        "lambda_per_s": lam,
        "p_wait_over_20min_model": exp_survival(long_wait_seconds, mean_gap),
        "p_wait_over_20min_real": float((gaps > long_wait_seconds).mean()),
        "ks_statistic": float(ks_stat),
        "ks_p_value": float(ks_p),
    }

    xs = np.linspace(0, gaps.max(), 300)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(gaps, bins=50, density=True, alpha=0.6, label="real gaps")
    ax.plot(
        xs, lam * np.exp(-lam * xs), "r-", label=f"exponential, mean = {mean_gap:.0f} s"
    )
    ax.set_title("Time between Bitcoin blocks (seconds)")
    ax.set_xlabel("gap (s)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "exp_gaps.png", dpi=150)
    plt.close(fig)
    return result
