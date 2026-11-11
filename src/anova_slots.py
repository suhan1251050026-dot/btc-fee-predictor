"""Unit 4: One-way ANOVA - does the fee change with the time of day (UTC)?

Analogy: you check the price of tea at 4 stalls. Prices always differ a little.
ANOVA asks: is the difference real, or only random wobble?
F = difference BETWEEN groups divided by noise INSIDE groups.
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from src.common import SLOTS, ensure_dir, fee_rows, slot_of_hour


def one_way_anova(groups):
    """F test written by hand. `groups` is a list of 1-D arrays."""
    groups = [np.asarray(g, dtype=float) for g in groups]
    k = len(groups)
    n = sum(len(g) for g in groups)
    grand = np.concatenate(groups).mean()
    ssb = sum(len(g) * (g.mean() - grand) ** 2 for g in groups)  # between groups
    ssw = sum(np.sum((g - g.mean()) ** 2) for g in groups)  # within groups
    df_b, df_w = k - 1, n - k
    msb, msw = ssb / df_b, ssw / df_w
    f = msb / msw
    p = float(stats.f.sf(f, df_b, df_w))
    return {
        "k_groups": k,
        "n": n,
        "ss_between": float(ssb),
        "ss_within": float(ssw),
        "df_between": df_b,
        "df_within": df_w,
        "F": float(f),
        "p_value": p,
    }


def run(df, out_dir):
    out = ensure_dir(out_dir)
    d = fee_rows(df)
    d["slot"] = d["hour_utc"].map(slot_of_hour)
    d["log_fee"] = np.log(d["avg_fee"])
    names = list(SLOTS.keys())
    groups = [d.loc[d["slot"] == s, "log_fee"].to_numpy() for s in names]
    groups_kept = [(n, g) for n, g in zip(names, groups) if len(g) >= 2]
    names = [n for n, _ in groups_kept]
    groups = [g for _, g in groups_kept]
    if len(groups) < 2:
        raise ValueError(
            "Need at least 2 time slots with data. Collect more days of blocks."
        )

    result = one_way_anova(groups)
    f_check, _ = stats.f_oneway(*groups)  # check only
    h, p_kw = stats.kruskal(*groups)  # second test. Does not assume a normal shape.
    result.update(
        {
            "check_scipy_F_diff": float(abs(f_check - result["F"])),
            "kruskal_H": float(h),
            "kruskal_p_value": float(p_kw),
            "slot_means_log_fee": {n: float(g.mean()) for n, g in zip(names, groups)},
            "slot_counts": {n: len(g) for n, g in zip(names, groups)},
        }
    )

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.boxplot(groups, tick_labels=[n.split(" ")[0] for n in names])
    ax.set_title("log(avg_fee) by time slot (UTC). India time = UTC + 5:30")
    ax.set_ylabel("log(avg_fee)")
    fig.tight_layout()
    fig.savefig(out / "anova_slots.png", dpi=150)
    plt.close(fig)
    return result
