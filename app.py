"""BTC Fee Predictor - interactive Streamlit app for the 5 syllabus topics.

Run (PowerShell, in the project folder):
    python -m streamlit run app.py

Every number on these pages comes from the same functions in `src/` that the tests check.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats

from src import anova_slots, conf_interval, describe, exp_gaps, poisson_counts
from src.common import SLOTS, fee_rows, load_blocks, slot_of_hour
from src.regression import least_squares, predict

REAL_CSV = Path("data/raw/blocks.csv")
SYNTH_CSV = Path("data/raw/blocks_synthetic.csv")
IST_LABELS = {
    "night (00-05 UTC)": "05:30-11:30 IST",
    "morning (06-11 UTC)": "11:30-17:30 IST",
    "afternoon (12-17 UTC)": "17:30-23:30 IST",
    "evening (18-23 UTC)": "23:30-05:30 IST",
}

st.set_page_config(page_title="BTC Fee Predictor", page_icon="₿", layout="wide")


@st.cache_data
def get_data(path):
    return load_blocks(path)


def new_fig(w=7, h=3.6):
    return plt.subplots(figsize=(w, h))


def show(fig):
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)
    plt.close(fig)


def note(col, label, value, hint):
    """A metric with a small grey note under it (no up/down arrow)."""
    col.metric(label, value)
    col.caption(hint)


# ---------------------------------------------------------------- data choice
st.sidebar.title("₿ BTC Fee Predictor")
st.sidebar.caption("MM0501 Probability and Statistics course project")
choices = [p for p in (REAL_CSV, SYNTH_CSV) if p.exists()]
if not choices:
    st.error(
        "No data found. Run `python -m src.collect --count 2000` "
        "(or `python -m src.synth` for practice data)."
    )
    st.stop()
csv_path = st.sidebar.radio(
    "Data file",
    choices,
    format_func=lambda p: (
        "Real Bitcoin blocks" if p == REAL_CSV else "SYNTHETIC (practice only)"
    ),
)
df = get_data(str(csv_path))
fees = fee_rows(df)
if csv_path == SYNTH_CSV:
    st.warning(
        "You are looking at SYNTHETIC data. Never use these numbers in the report."
    )

st.sidebar.metric("Blocks", f"{len(df):,}")
st.sidebar.write(f"**From:** {df['time_utc'].iloc[0]:%d %b %Y %H:%M} UTC")
st.sidebar.write(f"**To:** {df['time_utc'].iloc[-1]:%d %b %Y %H:%M} UTC")
st.sidebar.write("**Source:** mempool.space public API")
st.sidebar.divider()
st.sidebar.markdown(
    "**Team split**\n"
    "- A: Exponential + Poisson\n"
    "- B: Regression\n"
    "- C: ANOVA\n"
    "- D: Confidence interval + data"
)

st.title("Bitcoin Fee Predictor")
st.write(
    "Five topics from our Probability and Statistics syllabus, applied to real Bitcoin blocks. "
    "Use the controls on each tab. Every number is computed live from the data."
)

tabs = st.tabs(
    [
        "📊 Overview (Unit 1)",
        "⏱ Exponential (Unit 2)",
        "🔢 Poisson (Unit 2)",
        "📈 Regression (Unit 4)",
        "🕒 ANOVA (Unit 4)",
        "🎯 Confidence interval (Unit 4)",
    ]
)

# ---------------------------------------------------------------- overview
with tabs[0]:
    st.subheader("The data at a glance")
    st.caption(
        "Analogy: a doctor checks height, weight and pulse before any treatment. "
        "We check centre, spread and shape."
    )
    rows = {
        "Transactions per block": describe.summarize(fees["tx_count"]),
        "Block size (bytes)": describe.summarize(fees["size"]),
        "Average fee (satoshi)": describe.summarize(fees["avg_fee"]),
    }
    table = pd.DataFrame(rows).T[
        ["n", "mean", "median", "sd", "cv_percent", "min", "max"]
    ]
    table.columns = ["n", "Mean", "Median", "SD", "CV %", "Min", "Max"]
    st.dataframe(table.style.format("{:,.1f}"), width="stretch")

    fee = rows["Average fee (satoshi)"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Mean fee", f"{fee['mean']:,.0f} sat")
    c2.metric("Median fee", f"{fee['median']:,.0f} sat")
    c3.metric("CV of fee", f"{fee['cv_percent']:.0f} %")
    st.info(
        "The mean is above the median, and the CV is about 100 %. The fee is **right-skewed**. "
        "That is why the other tabs use the **log** of the fee."
    )
    use_log = st.toggle("Show the log of the fee", value=False)
    fig, ax = new_fig()
    values = np.log(fees["avg_fee"]) if use_log else fees["avg_fee"]
    ax.hist(values, bins=60, color="#4c78a8")
    ax.set_xlabel("log(avg_fee)" if use_log else "avg_fee (satoshi per transaction)")
    ax.set_ylabel("blocks")
    ax.set_title(
        "Average fee per block" + (" (log scale)" if use_log else " (raw, skewed)")
    )
    show(fig)

# ---------------------------------------------------------------- exponential
with tabs[1]:
    st.subheader("How long do we wait for the next block?")
    st.caption(
        "Analogy: you wait for the first raindrop on your hand. The rain has no memory. "
        "Waiting longer does not make a drop 'due'."
    )
    gaps, out_of_order = exp_gaps.block_gaps(df["timestamp"].to_numpy())
    mean_gap = float(gaps.mean())
    sd_gap = float(np.std(gaps, ddof=1))
    ks_p = stats.kstest(gaps, "expon", args=(0, mean_gap)).pvalue

    c1, c2, c3, c4 = st.columns(4)
    note(c1, "Mean gap", f"{mean_gap:.0f} s", f"{mean_gap / 60:.1f} minutes")
    note(c2, "SD / mean", f"{sd_gap / mean_gap:.2f}", "about 1 for an exponential")
    note(c3, "λ (blocks per hour)", f"{3600 / mean_gap:.2f}", "λ = 1 / mean gap")
    note(
        c4,
        "KS test p-value",
        f"{ks_p:.3f}",
        "above 0.05: no evidence against the model",
    )

    t_min = st.slider("Wait longer than t minutes", 1, 60, 20)
    t = t_min * 60
    p_model = exp_gaps.exp_survival(t, mean_gap)
    p_real = float((gaps > t).mean())
    c1, c2 = st.columns(2)
    c1.metric(f"Model: P(wait > {t_min} min)", f"{p_model:.3f}")
    note(
        c2,
        f"Real data: share of gaps > {t_min} min",
        f"{p_real:.3f}",
        f"difference: {(p_real - p_model) * 100:+.1f} percentage points",
    )
    st.latex(
        rf"P(X > t) = e^{{-\lambda t}} = e^{{-{t}/{mean_gap:.0f}}} = {p_model:.4f}"
    )

    fig, ax = new_fig()
    xs = np.linspace(0, np.percentile(gaps, 99.5), 400)
    lam = 1 / mean_gap
    ax.hist(
        gaps / 60, bins=60, density=True, alpha=0.55, color="#4c78a8", label="real gaps"
    )
    ax.plot(
        xs / 60,
        lam * 60 * np.exp(-lam * xs),
        color="#e45756",
        label="exponential model",
    )
    tail = xs[xs >= t]
    ax.fill_between(
        tail / 60,
        0,
        lam * 60 * np.exp(-lam * tail),
        color="#e45756",
        alpha=0.25,
        label=f"P(wait > {t_min} min)",
    )
    ax.set_xlabel("gap between blocks (minutes)")
    ax.set_ylabel("density")
    ax.legend()
    show(fig)

    with st.expander("Memoryless test: does waiting longer make a block 'due'?"):
        s_min = st.slider("We already waited s minutes", 1, 30, 10)
        s = s_min * 60
        waited = gaps[gaps > s]
        if len(waited) >= 20:
            cond = float((waited > s + t).mean())
            st.write(
                f"Of the **{len(waited)}** gaps longer than {s_min} min, "
                f"**{cond:.3f}** lasted another {t_min} min or more. "
                f"Fresh start: P(wait > {t_min} min) = **{p_real:.3f}**."
            )
            st.caption("If the two numbers are close, the process has no memory.")
        else:
            st.write("Too few long gaps for this check. Choose a smaller s.")
    st.caption(
        f"{out_of_order} block timestamps were out of order. We sort them before we compute gaps."
    )

# ---------------------------------------------------------------- poisson
with tabs[2]:
    st.subheader("How many blocks arrive in one hour?")
    st.caption(
        "Analogy: count the raindrops on your hand in one hour. "
        "The wait between drops is exponential. The count is Poisson."
    )
    counts = poisson_counts.hourly_counts(df["timestamp"].to_numpy())
    lam_h = float(counts.mean())
    var_h = float(counts.var(ddof=1))
    chi2, dof, p_chi, _ = poisson_counts.chi_square_gof(counts, lam_h)

    c1, c2, c3, c4 = st.columns(4)
    note(c1, "Full hours", f"{len(counts)}", "first and last hour dropped")
    note(c2, "λ (mean blocks per hour)", f"{lam_h:.2f}", "theory: 6 per hour")
    note(c3, "Variance / mean", f"{var_h / lam_h:.2f}", "about 1 for a Poisson")
    note(c4, "Chi-square p-value", f"{p_chi:.3f}", f"χ² = {chi2:.2f}, df = {dof}")
    st.caption(
        f"Cross-check with the exponential tab: 3600 / {mean_gap:.0f} s = "
        f"{3600 / mean_gap:.2f} blocks per hour."
    )

    k = st.slider("Number of blocks k in one hour", 0, 15, 10)
    p_eq = poisson_counts.poisson_pmf(k, lam_h)
    p_ge = poisson_counts.poisson_sf(k, lam_h)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"Model: P(X = {k})", f"{p_eq:.4f}")
    c2.metric(f"Real: share of hours = {k}", f"{(counts == k).mean():.4f}")
    c3.metric(f"Model: P(X ≥ {k})", f"{p_ge:.4f}")
    c4.metric(f"Real: share of hours ≥ {k}", f"{(counts >= k).mean():.4f}")
    st.latex(
        rf"P(X = {k}) = \frac{{e^{{-{lam_h:.2f}}}\,{lam_h:.2f}^{{{k}}}}}{{{k}!}} = {p_eq:.4f}"
    )

    ks_axis = np.arange(0, max(16, int(counts.max()) + 1))
    real = np.array([(counts == i).mean() for i in ks_axis])
    model = np.array([poisson_counts.poisson_pmf(int(i), lam_h) for i in ks_axis])
    fig, ax = new_fig()
    colors = ["#e45756" if i == k else "#4c78a8" for i in ks_axis]
    ax.bar(ks_axis - 0.2, real, width=0.4, color=colors, label="real hours")
    ax.bar(
        ks_axis + 0.2,
        model,
        width=0.4,
        color="#9ecae9",
        label=f"Poisson λ = {lam_h:.2f}",
    )
    ax.set_xlabel("blocks in one hour")
    ax.set_ylabel("share of hours")
    ax.set_xticks(ks_axis)
    ax.legend()
    show(fig)

# ---------------------------------------------------------------- regression
with tabs[3]:
    st.subheader("Can we predict the fee from the number of transactions?")
    st.caption(
        "Analogy: predict a taxi fare from the distance. Draw the best straight line. "
        "The standard error of estimate is the typical miss of a dart."
    )
    x = fees["tx_count"].to_numpy()
    y = np.log(fees["avg_fee"].to_numpy())
    model_log = least_squares(x, y)
    b = model_log["slope_b"]
    a = model_log["intercept_a"]
    se = model_log["std_error_of_estimate"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Slope b", f"{b:.6f}")
    c2.metric("Correlation r", f"{model_log['correlation_r']:.3f}")
    c3.metric("R²", f"{model_log['r_squared']:.3f}")
    note(c4, "Std error of estimate", f"{se:.3f}", "in log units")
    st.latex(rf"\log(\text{{fee}}) = {a:.3f} {b:+.6f}\times \text{{tx\_count}}")

    lo_x, hi_x = int(np.percentile(x, 1)), int(np.percentile(x, 99))
    tx_in = st.number_input(
        f"Transactions in a block (our data range: {lo_x:,} to {hi_x:,})",
        min_value=1,
        max_value=20000,
        value=int(np.median(x)),
        step=100,
    )
    pred_log = predict(model_log, tx_in)
    c1, c2 = st.columns(2)
    c1.metric("Predicted typical fee", f"{np.exp(pred_log):,.0f} sat per transaction")
    c2.metric(
        "Typical range (± 1 standard error)",
        f"{np.exp(pred_log - se):,.0f} to {np.exp(pred_log + se):,.0f} sat",
    )
    if not lo_x <= tx_in <= hi_x:
        st.warning(
            "This value is outside our data range. A line should not predict far outside its data."
        )

    fig, ax = new_fig()
    ax.scatter(x, y, s=6, alpha=0.35, color="#4c78a8", label="blocks")
    xs = np.array([x.min(), x.max()])
    ax.plot(xs, a + b * xs, color="#e45756", label="least-squares line")
    ax.fill_between(
        xs,
        a + b * xs - se,
        a + b * xs + se,
        color="#e45756",
        alpha=0.12,
        label="± 1 std error",
    )
    ax.scatter([tx_in], [pred_log], color="black", s=60, zorder=5, label="your input")
    ax.set_xlabel("transactions in block")
    ax.set_ylabel("log(avg_fee)")
    ax.legend()
    show(fig)

    st.warning(
        "**Surprise: the slope is negative.** We expected busy blocks to be expensive. "
        "Open the box below to see why the data says the opposite."
    )
    with st.expander("Why is the slope negative? (two checks with our data)"):
        logx = np.log(x)
        total = np.log(fees["total_fee"].to_numpy())
        ll_avg = stats.linregress(logx, y).slope
        ll_total = stats.linregress(logx, total).slope
        st.markdown(
            "**1. The ratio effect.** `avg_fee = total_fee / tx_count`, "
            "so `tx_count` is inside both x and y.  \n"
            f"Log-log slope of avg_fee on tx_count: **{ll_avg:.2f}**. "
            "Of this, **−1.00** comes only from the division.  \n"
            f"The real link between the total fee and tx_count is only **{ll_total:.2f}**.  \n"
            "Analogy: share one pizza among more friends. Each slice gets smaller."
        )
        q = pd.qcut(fees["tx_count"], 4)
        grp = pd.DataFrame(
            {
                "Median bytes per transaction": (fees["size"] / fees["tx_count"])
                .groupby(q, observed=True)
                .median(),
                "Median fee per transaction (sat)": fees["avg_fee"]
                .groupby(q, observed=True)
                .median(),
            }
        )
        grp.index = [f"{int(i.left) + 1:,} to {int(i.right):,} tx" for i in grp.index]
        st.markdown(
            "**2. Small transactions.** Blocks with many transactions hold small, cheap ones."
        )
        st.dataframe(grp.style.format("{:,.0f}"), width="stretch")
        st.markdown(
            "**Conclusion:** `tx_count` is a poor measure of demand. A high R² does not prove a cause."
        )

# ---------------------------------------------------------------- anova
with tabs[4]:
    st.subheader("Does the fee change with the time of day?")
    st.caption(
        "Analogy: compare the price of tea at 4 stalls. ANOVA asks: is the difference real, "
        "or only random wobble? F = difference BETWEEN groups / noise INSIDE groups."
    )
    d = fees.copy()
    d["slot"] = d["hour_utc"].map(slot_of_hour)
    d["log_fee"] = np.log(d["avg_fee"])
    names = [n for n in SLOTS if (d["slot"] == n).sum() >= 2]
    groups = [d.loc[d["slot"] == n, "log_fee"].to_numpy() for n in names]
    res = anova_slots.one_way_anova(groups)
    _, p_kw = stats.kruskal(*groups)
    eta2 = res["ss_between"] / (res["ss_between"] + res["ss_within"])

    c1, c2, c3, c4 = st.columns(4)
    note(c1, "F", f"{res['F']:.2f}", f"df = {res['df_between']}, {res['df_within']}")
    note(c2, "p-value", f"{res['p_value']:.2e}", "from the F distribution")
    note(c3, "Kruskal-Wallis p", f"{p_kw:.2e}", "second test, no normal shape needed")
    note(
        c4,
        "Effect size η²",
        f"{eta2:.3f}",
        f"slots explain {eta2 * 100:.0f} % of the variation",
    )

    alpha = st.select_slider(
        "Significance level α", options=[0.10, 0.05, 0.01, 0.001], value=0.05
    )
    if res["p_value"] < alpha:
        st.success(
            f"p < {alpha}: we **reject H0**. At least one time slot has a different mean fee."
        )
    else:
        st.info(
            f"p ≥ {alpha}: we **cannot reject H0**. No evidence that the slots differ."
        )

    tz = st.radio("Show slot labels in", ["UTC", "India time (IST)"], horizontal=True)
    labels = [
        n.split(" ")[0].title()
        + "\n"
        + (n.split("(")[1].rstrip(")") if tz == "UTC" else IST_LABELS[n])
        for n in names
    ]
    slot_table = pd.DataFrame(
        {
            "Slot": [lbl.replace("\n", "  ") for lbl in labels],
            "Blocks": [len(g) for g in groups],
            "Mean log fee": [g.mean() for g in groups],
            "Typical fee (sat)": [np.exp(g.mean()) for g in groups],
        }
    )
    st.dataframe(
        slot_table.style.format(
            {"Mean log fee": "{:.3f}", "Typical fee (sat)": "{:,.0f}"}
        ),
        width="stretch",
        hide_index=True,
    )

    fig, ax = new_fig()
    ax.boxplot(groups, tick_labels=labels)
    ax.set_ylabel("log(avg_fee)")
    ax.set_title(f"log fee by time slot ({tz})")
    show(fig)
    st.caption(
        "The p-value is tiny because we have many blocks. η² shows the size: the time slot "
        "explains only a small part of the fee variation."
    )

# ---------------------------------------------------------------- confidence interval
with tabs[5]:
    st.subheader("What is the true mean fee?")
    st.caption(
        "Analogy: you cannot see the true average. You throw a net over it. "
        "A 95 % net catches the true value in about 95 of 100 repeated studies."
    )
    level = st.select_slider(
        "Confidence level",
        options=[0.80, 0.90, 0.95, 0.99],
        value=0.95,
        format_func=lambda v: f"{v:.0%}",
    )
    full = conf_interval.mean_ci(fees["avg_fee"], confidence=level)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sample size n", f"{full['n']:,}")
    c2.metric("Mean fee", f"{full['mean']:,.1f} sat")
    c3.metric("Margin", f"± {full['margin']:,.1f} sat")
    c4.metric(f"{level:.0%} interval", f"{full['lower']:,.0f} to {full['upper']:,.0f}")
    st.latex(
        rf"\bar x \pm t\frac{{s}}{{\sqrt n}} = {full['mean']:.1f} \pm {full['t_critical']:.3f}"
        rf"\times\frac{{{full['sd']:.1f}}}{{\sqrt{{{full['n']}}}}} = "
        rf"{full['mean']:.1f} \pm {full['margin']:.1f}"
    )

    st.divider()
    st.markdown("#### Classroom experiment: does the net really catch the mean?")
    st.write(
        "We treat all blocks as the 'population'. Its mean is the true value. "
        "We draw many small random samples, build an interval from each one, "
        "and count how many catch it."
    )
    c1, c2 = st.columns(2)
    n_small = c1.slider("Blocks in each sample (n)", 10, 500, 50, step=10)
    reps = c2.slider("Number of samples", 20, 200, 100, step=10)
    seed = st.number_input("Random seed (change it to draw new samples)", 0, 9999, 42)
    rng = np.random.default_rng(int(seed))
    pop = fees["avg_fee"].to_numpy()
    true_mean = float(pop.mean())
    cis = [
        conf_interval.mean_ci(
            rng.choice(pop, size=n_small, replace=False), confidence=level
        )
        for _ in range(reps)
    ]
    hit = np.array([c["lower"] <= true_mean <= c["upper"] for c in cis])
    note(
        st,
        f"Intervals that caught the true mean ({true_mean:,.0f} sat)",
        f"{hit.sum()} of {reps}",
        f"hit rate {hit.mean():.0%}, target {level:.0%}",
    )

    fig, ax = new_fig(7, 4.5)
    for i, (c, ok) in enumerate(zip(cis, hit)):
        ax.plot(
            [c["lower"], c["upper"]],
            [i, i],
            color="#4c78a8" if ok else "#e45756",
            lw=1.4,
        )
    ax.axvline(true_mean, color="black", ls="--", label="true mean")
    ax.set_xlabel("avg_fee (satoshi)")
    ax.set_ylabel("sample number")
    ax.set_yticks([])
    ax.set_title("Blue = caught the true mean. Red = missed.")
    ax.legend()
    show(fig)
    st.caption(
        "Fee data is skewed, so with small n the hit rate can fall below the target. "
        "Increase n and watch it move closer: this is the central limit theorem at work."
    )
