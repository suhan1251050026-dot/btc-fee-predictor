"""The web API answers every topic without an error (synthetic data, no network)."""

from fastapi.testclient import TestClient

from api import main, service
from src.synth import make_blocks


def test_api_runs_on_synthetic_data(tmp_path, monkeypatch):
    make_blocks(1500).to_csv(tmp_path / "blocks_synthetic.csv", index=False)
    monkeypatch.setenv("BTC_DATA_DIR", str(tmp_path))
    service._load.cache_clear()
    c = TestClient(main.app)
    assert c.get("/api/health").json()["datasets"] == ["synthetic"]
    assert c.get("/api/overview?dataset=real").status_code == 404
    q = "dataset=synthetic"
    for path in (
        "overview",
        "exponential",
        "poisson",
        "regression",
        "anova",
        "confidence",
    ):
        r = c.get(f"/api/{path}?{q}")
        assert r.status_code == 200, (path, r.text)
    reg = c.get(f"/api/regression?{q}&tx=3000").json()
    assert reg["range_low"] < reg["pred_fee"] < reg["range_high"]
    ci = c.get(f"/api/confidence?{q}&n=40&reps=30").json()
    assert len(ci["intervals"]) == 30
    assert c.get(f"/api/regression?{q}&tx=0").status_code == 422
