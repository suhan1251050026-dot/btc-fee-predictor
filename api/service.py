"""Statistics service for the web app. Every number comes from the functions in src/.

Analogy: src/ is the kitchen, this file is the pass. It plates results as JSON.
"""

import os
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from src import anova_slots, conf_interval, describe, exp_gaps, poisson_counts
from src.common import SLOTS, fee_rows, load_blocks, slot_of_hour
from src.regression import least_squares, predict

ROOT = Path(__file__).resolve().parents[1]
IST_LABELS = {
    "night (00-05 UTC)": "05:30-11:30 IST",
    "morning (06-11 UTC)": "11:30-17:30 IST",
    "afternoon (12-17 UTC)": "17:30-23:30 IST",
    "evening (18-23 UTC)": "23:30-05:30 IST",
}
CI_LEVELS = (0.80, 0.90, 0.95, 0.99)
ALPHAS = (0.10, 0.05, 0.01, 0.001)


class DataMissing(Exception):
    """The requested CSV is not on disk."""


def _data_dir():
    return Path(os.environ.get("BTC_DATA_DIR", ROOT / "data" / "raw"))


def dataset_paths():
    d = _data_dir()
    return {"real": d / "blocks.csv", "synthetic": d / "blocks_synthetic.csv"}


def available():
    return [name for name, p in dataset_paths().items() if p.exists()]


@lru_cache(maxsize=4)
def _load(path, mtime):
    df = load_blocks(path)
    return df, fee_rows(df)


def data(name):
    p = dataset_paths()[name]
    if not p.exists():
        raise DataMissing(name)
    return _load(str(p), p.stat().st_mtime)


def _f(x, nd=6):
    return round(float(x), nd)


def _hist(values, bins, density=False):
    counts, edges = np.histogram(
        np.asarray(values, dtype=float), bins=bins, density=density
    )
    return [
        {"x0": _f(a), "x1": _f(b), "y": _f(c)}
        for a, b, c in zip(edges[:-1], edges[1:], counts)
    ]


def _gaps(df):
    return exp_gaps.block_gaps(df["timestamp"].to_numpy())


def overview(name):
    df, fees = data(name)
    labels = {
        "tx_count": "Transactions per block",
        "size": "Block size (bytes)",
        "avg_fee": "Average fee (satoshi)",
    }
    table = [
        {"label": lab, **describe.summarize(fees[col])} for col, lab in labels.items()
    ]
    fee = table[2]
    gaps, _ = _gaps(df)
    recent = df.tail(121)
    replay = [
        {"h": int(h), "tx": int(tx), "fee": _f(fee_, 2), "gap": int(g)}
        for h, tx, fee_, g in zip(
            recent["height"],
            recent["tx_count"],
            recent["avg_fee"],
            recent["timestamp"].diff().fillna(0),
        )
    ][1:]
    return {
        "dataset": name,
        "n_blocks": len(df),
        "start": df["time_utc"].iloc[0].isoformat(),
        "end": df["time_utc"].iloc[-1].isoformat(),
        "table": [
            {k: (_f(v, 3) if k != "label" else v) for k, v in r.items()} for r in table
        ],
        "median_fee": _f(fee["median"], 2),
        "mean_fee": _f(fee["mean"], 2),
        "cv_percent": _f(fee["cv_percent"], 2),
        "mean_gap": _f(gaps.mean(), 2),
        "blocks_per_hour": _f(3600 / gaps.mean(), 3),
        "hist_raw": _hist(fees["avg_fee"], 60),
        "hist_log": _hist(np.log(fees["avg_fee"]), 60),
        "replay": replay,
    }


def exponential(name, t_min, s_min):
    df, _ = data(name)
    gaps, out_of_order = _gaps(df)
    mean_gap = float(gaps.mean())
    sd_gap = float(np.std(gaps, ddof=1))
    ks_p = stats.kstest(gaps, "expon", args=(0, mean_gap)).pvalue
    t = t_min * 60
    p_model = exp_gaps.exp_survival(t, mean_gap)
    p_real = float((gaps > t).mean())
    lam = 1 / mean_gap
    xs = np.linspace(0, np.percentile(gaps, 99.5), 200)
    s = s_min * 60
    waited = gaps[gaps > s]
    memory = None
    if len(waited) >= 20:
        memory = {"n": len(waited), "conditional": _f((waited > s + t).mean())}
    return {
        "mean_gap": _f(mean_gap, 3),
        "sd_over_mean": _f(sd_gap / mean_gap),
        "blocks_per_hour": _f(3600 / mean_gap),
        "ks_p": _f(ks_p),
        "t_min": t_min,
        "p_model": _f(p_model),
        "p_real": _f(p_real),
        "hist": _hist(gaps / 60, 60, density=True),
        "curve": [{"x": _f(x / 60), "y": _f(lam * 60 * np.exp(-lam * x))} for x in xs],
        "s_min": s_min,
        "memoryless": memory,
        "out_of_order": int(out_of_order),
    }


def poisson(name, k):
    df, _ = data(name)
    counts = poisson_counts.hourly_counts(df["timestamp"].to_numpy())
    lam = float(counts.mean())
    var = float(counts.var(ddof=1))
    chi2, dof, p_chi, _ = poisson_counts.chi_square_gof(counts, lam)
    axis = np.arange(0, max(16, int(counts.max()) + 1))
    gaps, _ = _gaps(df)
    return {
        "hours": len(counts),
        "lam": _f(lam),
        "var_over_mean": _f(var / lam),
        "chi2": _f(chi2),
        "dof": int(dof),
        "p_chi": _f(p_chi),
        "cross_check": _f(3600 / gaps.mean()),
        "k": k,
        "p_eq": _f(poisson_counts.poisson_pmf(k, lam)),
        "p_ge": _f(poisson_counts.poisson_sf(k, lam)),
        "real_eq": _f((counts == k).mean()),
        "real_ge": _f((counts >= k).mean()),
        "bars": [
            {
                "k": int(i),
                "real": _f((counts == i).mean()),
                "model": _f(poisson_counts.poisson_pmf(int(i), lam)),
            }
            for i in axis
        ],
    }


def regression(name, tx):
    _, fees = data(name)
    x = fees["tx_count"].to_numpy()
    y = np.log(fees["avg_fee"].to_numpy())
    m = least_squares(x, y)
    a, b, se = m["intercept_a"], m["slope_b"], m["std_error_of_estimate"]
    lo_x, hi_x = int(np.percentile(x, 1)), int(np.percentile(x, 99))
    pred_log = predict(m, tx)
    logx = np.log(x)
    total = np.log(fees["total_fee"].to_numpy())
    q = pd.qcut(fees["tx_count"], 4)
    bpt = (fees["size"] / fees["tx_count"]).groupby(q, observed=True).median()
    fpt = fees["avg_fee"].groupby(q, observed=True).median()
    quartiles = [
        {
            "range": f"{int(i.left) + 1:,} to {int(i.right):,} tx",
            "bytes_per_tx": _f(bpt[i], 1),
            "fee_per_tx": _f(fpt[i], 1),
        }
        for i in bpt.index
    ]
    return {
        "a": _f(a),
        "b": _f(b, 9),
        "r": _f(m["correlation_r"]),
        "r2": _f(m["r_squared"]),
        "se": _f(se),
        "lo_x": lo_x,
        "hi_x": hi_x,
        "median_x": int(np.median(x)),
        "x_min": int(x.min()),
        "x_max": int(x.max()),
        "tx": tx,
        "pred_log": _f(pred_log),
        "pred_fee": _f(np.exp(pred_log), 2),
        "range_low": _f(np.exp(pred_log - se), 2),
        "range_high": _f(np.exp(pred_log + se), 2),
        "in_range": bool(lo_x <= tx <= hi_x),
        "points": [[int(xi), round(float(yi), 4)] for xi, yi in zip(x, y)],
        "loglog_avg": _f(stats.linregress(logx, y).slope, 4),
        "loglog_total": _f(stats.linregress(logx, total).slope, 4),
        "quartiles": quartiles,
    }


def _box(g):
    q1, med, q3 = np.percentile(g, [25, 50, 75])
    iqr = q3 - q1
    lo = g[g >= q1 - 1.5 * iqr].min()
    hi = g[g <= q3 + 1.5 * iqr].max()
    out = g[(g < lo) | (g > hi)]
    return {
        "q1": _f(q1),
        "median": _f(med),
        "q3": _f(q3),
        "lo": _f(lo),
        "hi": _f(hi),
        "outliers": [_f(v, 4) for v in out],
    }


def anova(name, alpha, tz):
    _, fees = data(name)
    d = fees.copy()
    d["slot"] = d["hour_utc"].map(slot_of_hour)
    d["log_fee"] = np.log(d["avg_fee"])
    names = [n for n in SLOTS if (d["slot"] == n).sum() >= 2]
    groups = [d.loc[d["slot"] == n, "log_fee"].to_numpy() for n in names]
    res = anova_slots.one_way_anova(groups)
    _, p_kw = stats.kruskal(*groups)
    eta2 = res["ss_between"] / (res["ss_between"] + res["ss_within"])
    slots = []
    for n, g in zip(names, groups):
        hours = n.split("(")[1].rstrip(")") if tz == "utc" else IST_LABELS[n]
        slots.append(
            {
                "name": n.split(" ")[0].title(),
                "hours": hours,
                "blocks": len(g),
                "mean_log": _f(g.mean()),
                "typical_fee": _f(np.exp(g.mean()), 1),
                "box": _box(g),
            }
        )
    return {
        "F": _f(res["F"]),
        "p": float(res["p_value"]),
        "df_between": int(res["df_between"]),
        "df_within": int(res["df_within"]),
        "p_kw": float(p_kw),
        "eta2": _f(eta2),
        "alpha": alpha,
        "reject": bool(res["p_value"] < alpha),
        "tz": tz,
        "slots": slots,
    }


def confidence(name, level, n, reps, seed):
    _, fees = data(name)
    full = conf_interval.mean_ci(fees["avg_fee"], confidence=level)
    rng = np.random.default_rng(int(seed))
    pop = fees["avg_fee"].to_numpy()
    true_mean = float(pop.mean())
    cis = [
        conf_interval.mean_ci(rng.choice(pop, size=n, replace=False), confidence=level)
        for _ in range(reps)
    ]
    intervals = [
        {
            "lower": _f(c["lower"], 2),
            "upper": _f(c["upper"], 2),
            "hit": bool(c["lower"] <= true_mean <= c["upper"]),
        }
        for c in cis
    ]
    hits = sum(i["hit"] for i in intervals)
    return {
        "level": level,
        "full": {k: (_f(v, 4) if k != "n" else int(v)) for k, v in full.items()},
        "true_mean": _f(true_mean, 2),
        "n": n,
        "reps": reps,
        "seed": seed,
        "hits": int(hits),
        "intervals": intervals,
    }
