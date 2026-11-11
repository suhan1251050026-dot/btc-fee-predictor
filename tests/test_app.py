"""Smoke test: the Streamlit app runs every tab without an error (no browser, no network)."""

from pathlib import Path

import pytest

st_testing = pytest.importorskip("streamlit.testing.v1")

ROOT = Path(__file__).resolve().parents[1]


def test_app_runs_on_synthetic_data(tmp_path, monkeypatch):
    from src.synth import make_blocks

    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    make_blocks(1500).to_csv(raw / "blocks_synthetic.csv", index=False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(ROOT))

    at = st_testing.AppTest.from_file(str(ROOT / "app.py"), default_timeout=60)
    at.run()
    assert not at.exception, at.exception
    assert len(at.tabs) == 6
