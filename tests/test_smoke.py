"""Smoke test: the project packages import and the folders exist."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_folders_exist():
    for name in ("src", "tests", "data/raw", "docs/plans"):
        assert (ROOT / name).is_dir(), name


def test_scipy_basics():
    from scipy import stats

    assert round(stats.norm.cdf(0), 3) == 0.5
