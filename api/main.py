"""FastAPI app: JSON endpoints for the five syllabus topics, plus the built React site.

Run (in the project folder):  python -m uvicorn api.main:app --port 8000
"""

from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from api import service

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "frontend" / "dist"
Dataset = Literal["real", "synthetic"]

app = FastAPI(title="BTC Fee Predictor API", version="2.0")


@app.exception_handler(service.DataMissing)
def _missing(_: Request, exc: service.DataMissing):
    return JSONResponse(
        status_code=404,
        content={
            "detail": f"No {exc.args[0]} data file. Run `python -m src.collect --count 2000` "
            "(or `python -m src.synth` for practice data)."
        },
    )


@app.middleware("http")
async def landing_page_cors(request: Request, call_next):
    """ThreeUI landing pages run in a sandboxed iframe (opaque origin), so their
    module imports are cross-origin. Allow them for /landing-pages/ only."""
    response = await call_next(request)
    if request.url.path.startswith("/landing-pages/"):
        response.headers["Access-Control-Allow-Origin"] = "*"
    return response


@app.get("/api/health")
def health():
    return {"ok": True, "datasets": service.available()}


@app.get("/api/overview")
def overview(dataset: Dataset = "real"):
    return service.overview(dataset)


@app.get("/api/exponential")
def exponential(
    dataset: Dataset = "real",
    t_min: int = Query(20, ge=1, le=60),
    s_min: int = Query(10, ge=1, le=30),
):
    return service.exponential(dataset, t_min, s_min)


@app.get("/api/poisson")
def poisson(dataset: Dataset = "real", k: int = Query(10, ge=0, le=15)):
    return service.poisson(dataset, k)


@app.get("/api/regression")
def regression(dataset: Dataset = "real", tx: int = Query(3600, ge=1, le=20000)):
    return service.regression(dataset, tx)


@app.get("/api/anova")
def anova(
    dataset: Dataset = "real",
    alpha: Literal["0.1", "0.05", "0.01", "0.001"] = "0.05",
    tz: Literal["utc", "ist"] = "utc",
):
    return service.anova(dataset, float(alpha), tz)


@app.get("/api/confidence")
def confidence(
    dataset: Dataset = "real",
    level: Literal["0.8", "0.9", "0.95", "0.99"] = "0.95",
    n: int = Query(50, ge=10, le=500),
    reps: int = Query(100, ge=20, le=200),
    seed: int = Query(42, ge=0, le=9999),
):
    return service.confidence(dataset, float(level), n, reps, seed)


if DIST.exists():
    app.mount("/", StaticFiles(directory=DIST, html=True), name="web")
