"""Known-answer tests for each topic module. No network."""

import math

import numpy as np
import pytest
from scipy import stats

from src import (
    anova_slots,
    conf_interval,
    describe,
    exp_gaps,
    poisson_counts,
    regression,
)
from src.synth import make_blocks


# ---------- Unit 1: descriptive ----------
def test_describe_known_values():
    s = describe.summarize([2, 4, 4, 4, 5, 5, 7, 9])
    assert s["mean"] == 5.0
    assert s["median"] == 4.5
    assert s["sd"] == pytest.approx(np.std([2, 4, 4, 4, 5, 5, 7, 9], ddof=1))
    assert s["cv_percent"] == pytest.approx(s["sd"] / 5.0 * 100)


# ---------- Unit 2: exponential ----------
def test_exp_survival_known_values():
    assert exp_gaps.exp_survival(600, 600) == pytest.approx(math.exp(-1))
    assert exp_gaps.exp_survival(1200, 600) == pytest.approx(math.exp(-2))
    assert exp_gaps.exp_cdf(300, 600) == pytest.approx(1 - math.exp(-0.5))


def test_block_gaps_drops_nonpositive():
    gaps, dropped = exp_gaps.block_gaps([0, 600, 1200, 1190, 1800])
    assert list(gaps) == [600, 600, 610]
    assert dropped == 1


def test_exp_recovers_mean_on_synthetic():
    df = make_blocks(3000)
    gaps, _ = exp_gaps.block_gaps(df["timestamp"].to_numpy())
    assert gaps.mean() == pytest.approx(600, rel=0.08)


# ---------- Unit 2: Poisson ----------
def test_poisson_pmf_known_values():
    assert poisson_counts.poisson_pmf(10, 6) == pytest.approx(0.0413030934, abs=1e-9)
    assert poisson_counts.poisson_sf(10, 6) == pytest.approx(0.0839240170, abs=1e-9)
    assert poisson_counts.poisson_pmf(3, 2.5) == pytest.approx(
        stats.poisson.pmf(3, 2.5)
    )


def test_hourly_counts_drops_partial_hours():
    # hour 0: 2 blocks (partial, dropped). hour 1: 3 blocks. hour 2: 1 block. hour 3: partial.
    ts = [100, 200, 3700, 3800, 3900, 7300, 10900]
    assert list(poisson_counts.hourly_counts(ts)) == [3, 1]


def test_merge_bins_expected_at_least_five():
    obs = [1, 3, 6, 9, 4, 2, 0]
    exp = [1.0, 3.5, 6.0, 8.0, 4.0, 2.0, 0.5]
    o, e = poisson_counts.merge_bins(obs, exp)
    assert o.sum() == sum(obs)
    assert e.sum() == pytest.approx(sum(exp))
    assert (e >= 5).all()


def test_poisson_fits_poisson_data():
    rng = np.random.default_rng(1)
    counts = rng.poisson(6, size=500)
    _, _, p, _ = poisson_counts.chi_square_gof(counts, counts.mean())
    assert p > 0.01


# ---------- Unit 4: regression ----------
def test_regression_textbook_example():
    res = regression.least_squares([1, 2, 3, 4, 5], [2, 4, 5, 4, 5])
    assert res["slope_b"] == pytest.approx(0.6)
    assert res["intercept_a"] == pytest.approx(2.2)
    assert res["correlation_r"] == pytest.approx(0.7745966692)
    assert res["r_squared"] == pytest.approx(0.6)
    assert res["std_error_of_estimate"] == pytest.approx(math.sqrt(2.4 / 3))


def test_regression_perfect_line():
    res = regression.least_squares([1, 2, 3, 4], [3, 5, 7, 9])
    assert res["slope_b"] == pytest.approx(2.0)
    assert res["intercept_a"] == pytest.approx(1.0)
    assert res["std_error_of_estimate"] == pytest.approx(0.0, abs=1e-9)


def test_regression_matches_scipy():
    rng = np.random.default_rng(3)
    x = rng.normal(50, 10, 200)
    y = 3 + 0.5 * x + rng.normal(0, 2, 200)
    ours = regression.least_squares(x, y)
    ref = stats.linregress(x, y)
    assert ours["slope_b"] == pytest.approx(ref.slope)
    assert ours["intercept_a"] == pytest.approx(ref.intercept)
    assert ours["correlation_r"] == pytest.approx(ref.rvalue)


def test_predict():
    model = {"intercept_a": 2.0, "slope_b": 0.5}
    assert regression.predict(model, 10) == 7.0


# ---------- Unit 4: ANOVA ----------
def test_anova_textbook_example():
    res = anova_slots.one_way_anova([[4, 5, 6], [6, 7, 8], [8, 9, 10]])
    assert res["ss_between"] == pytest.approx(24.0)
    assert res["ss_within"] == pytest.approx(6.0)
    assert (res["df_between"], res["df_within"]) == (2, 6)
    assert res["F"] == pytest.approx(12.0)
    assert res["p_value"] == pytest.approx(0.008, abs=1e-6)


def test_anova_matches_scipy():
    rng = np.random.default_rng(5)
    groups = [rng.normal(m, 1, 40) for m in (0.0, 0.2, 0.5, 0.1)]
    ours = anova_slots.one_way_anova(groups)
    f_ref, p_ref = stats.f_oneway(*groups)
    assert ours["F"] == pytest.approx(f_ref)
    assert ours["p_value"] == pytest.approx(p_ref)


# ---------- Unit 4: confidence interval ----------
def test_ci_known_example():
    # n = 25, mean 50, s = 10 -> margin = 2.0639 * 10 / 5 = 4.128
    x = np.array([50 + 10 * z for z in np.linspace(-1.7, 1.7, 25)])
    x = (x - x.mean()) / np.std(x, ddof=1) * 10 + 50
    ci = conf_interval.mean_ci(x)
    assert ci["mean"] == pytest.approx(50)
    assert ci["sd"] == pytest.approx(10)
    assert ci["lower"] == pytest.approx(45.8722, abs=1e-3)
    assert ci["upper"] == pytest.approx(54.1278, abs=1e-3)


def test_ci_matches_scipy():
    rng = np.random.default_rng(7)
    x = rng.normal(100, 15, 80)
    ours = conf_interval.mean_ci(x)
    lo, hi = stats.t.interval(0.95, len(x) - 1, loc=x.mean(), scale=stats.sem(x))
    assert ours["lower"] == pytest.approx(lo)
    assert ours["upper"] == pytest.approx(hi)


# ---------- end to end on synthetic data ----------
def test_full_pipeline_on_synthetic(tmp_path):
    from src.analyze import run_all

    csv = tmp_path / "blocks.csv"
    make_blocks(1500).to_csv(csv, index=False)
    summary = run_all(csv, tmp_path / "out")
    reg = summary["3_regression (Unit 4)"]["log_fee"]
    assert reg["slope_b"] == pytest.approx(
        0.0004, abs=0.0001
    )  # truth built into the fake data
    assert summary["4_anova (Unit 4)"]["p_value"] < 0.05  # evening boost is real
    assert (tmp_path / "out" / "summary.json").exists()
