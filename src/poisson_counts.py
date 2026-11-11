"""Unit 2: Poisson distribution - the number of blocks found in one hour.

Analogy: count the raindrops that hit your hand in one hour.
The waiting time between drops is exponential. The count of drops is Poisson.
"""

import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from src.common import ensure_dir


def hourly_counts(timestamps):
    """Count blocks in each full clock hour. The first and last hours are partial, so drop them."""
    hours = np.asarray(timestamps, dtype=np.int64) // 3600
    counts = pd.Series(hours).value_counts().sort_index()
    full_range = range(int(counts.index.min()) + 1, int(counts.index.max()))
    counts = counts.reindex(full_range, fill_value=0)
    return counts.to_numpy()


def poisson_pmf(k, lam):
    """P(X = k) = e^(-lambda) * lambda^k / k!"""
    return math.exp(-lam) * lam**k / math.factorial(k)


def poisson_sf(k, lam):
    """P(X >= k) = 1 - P(X <= k - 1)."""
    return 1 - sum(poisson_pmf(i, lam) for i in range(k))


def merge_bins(observed, expected, min_expected=5.0):
    """Merge neighbouring bins until each expected count is at least 5 (chi-square rule)."""
    obs_out, exp_out = [], []
    acc_o = acc_e = 0.0
    for o, e in zip(observed, expected):
        acc_o += o
        acc_e += e
        if acc_e >= min_expected:
            obs_out.append(acc_o)
            exp_out.append(acc_e)
            acc_o = acc_e = 0.0
    if acc_e > 0:  # small rest goes into the last bin
        if exp_out:
            obs_out[-1] += acc_o
            exp_out[-1] += acc_e
        else:
            obs_out.append(acc_o)
            exp_out.append(acc_e)
    return np.array(obs_out), np.array(exp_out)


def chi_square_gof(counts, lam):
    """Chi-square goodness of fit for a Poisson model. Lambda was estimated, so df = bins - 2."""
    n = len(counts)
    kmax = int(counts.max())
    observed = [float((counts == k).sum()) for k in range(kmax + 1)]
    expected = [n * poisson_pmf(k, lam) for k in range(kmax + 1)]
    observed.append(0.0)  # tail bin: P(X > kmax)
    expected.append(n * poisson_sf(kmax + 1, lam))
    obs, exp = merge_bins(observed, expected)
    chi2 = float(np.sum((obs - exp) ** 2 / exp))
    df = len(obs) - 1 - 1
    p = float(stats.chi2.sf(chi2, df)) if df > 0 else float("nan")
    return chi2, df, p, len(obs)


def run(df, out_dir):
    out = ensure_dir(out_dir)
    counts = hourly_counts(df["timestamp"].to_numpy())
    lam = float(counts.mean())
    var = float(counts.var(ddof=1))
    chi2, dof, p, n_bins = chi_square_gof(counts, lam)
    result = {
        "n_hours": len(counts),
        "lambda_blocks_per_hour": lam,
        "variance": var,
        "dispersion_var_over_mean": var / lam,  # about 1 for a Poisson model
        "p_10_or_more_model": poisson_sf(10, lam),
        "p_10_or_more_real": float((counts >= 10).mean()),
        "chi2": chi2,
        "chi2_df": dof,
        "chi2_p_value": p,
        "bins_after_merge": n_bins,
    }

    ks = np.arange(0, int(counts.max()) + 1)
    real = np.array([(counts == k).mean() for k in ks])
    model = np.array([poisson_pmf(int(k), lam) for k in ks])
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(ks - 0.2, real, width=0.4, label="real")
    ax.bar(ks + 0.2, model, width=0.4, label=f"Poisson, lambda = {lam:.2f}")
    ax.set_title("Blocks per hour")
    ax.set_xlabel("blocks in one hour")
    ax.set_ylabel("share of hours")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "poisson_counts.png", dpi=150)
    plt.close(fig)
    return result
