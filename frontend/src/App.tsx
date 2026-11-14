import { lazy, Suspense, useEffect, useMemo, useState } from "react";
import { dur, fmt, useApi, type Dataset, type Overview, type Regression } from "./api";
import { ChartCard, COLORS, Key, ScatterChart } from "./charts";
import Tests from "./Tests";
import PocketQuest from "./PocketQuest";

const Chain3D = lazy(() => import("./Chain3D"));

export default function App() {
  const health = useApi<{ ok: boolean; datasets: Dataset[] }>("/api/health", 0);
  const [dataset, setDataset] = useState<Dataset>("real");
  const datasets = health.data?.datasets ?? [];
  useEffect(() => {
    if (datasets.length && !datasets.includes(dataset)) setDataset(datasets[0]);
  }, [datasets, dataset]);
  const ov = useApi<Overview>(health.data ? `/api/overview?dataset=${dataset}` : null, 0);

  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const on = () => setScrolled(scrollY > 30);
    addEventListener("scroll", on, { passive: true });
    return () => removeEventListener("scroll", on);
  }, []);
  useReveal([ov.data]);

  const fatal = health.error ?? ov.error;
  return (
    <>
      <nav className={`nav ${scrolled ? "scrolled" : ""}`} aria-label="Main">
        <div className="wrap nav-in">
          <a className="logo" href="#top">
            <span className="logo-mark" aria-hidden />
            <span>Fee Predictor<small>MM0501 · VIT Pune</small></span>
          </a>
          <div className="nav-links">
            <a href="#predict">Predict</a>
            <a href="#tests">Five tests</a>
            <a href="#play">Play</a>
            <a href="#about">About</a>
          </div>
          {datasets.length > 1 && (
            <div className="seg" role="group" aria-label="Data file">
              {datasets.map((d) => (
                <button key={d} aria-pressed={d === dataset} onClick={() => setDataset(d)}>{d === "real" ? "Real" : "Synthetic"}</button>
              ))}
            </div>
          )}
          <a className="btn btn-lime" href="#predict">Predict a fee <span className="arrow">→</span></a>
        </div>
      </nav>
      {dataset === "synthetic" && <div className="warn-strip" style={{ marginTop: 74 }}>You are looking at SYNTHETIC practice data. Never use these numbers in the report.</div>}

      <main id="top">
        <Hero ov={ov.data} error={fatal} retry={() => { health.retry(); ov.retry(); }} />
        <Band ov={ov.data} />
        {ov.data && (
          <>
            <Predict dataset={dataset} />
            <Band ov={ov.data} flip />
            <Tests dataset={dataset} overview={ov.data} />
          </>
        )}
        <PocketQuest />
      </main>
      <Footer ov={ov.data} />
    </>
  );
}

function useReveal(deps: unknown[]) {
  useEffect(() => {
    const io = new IntersectionObserver((es) => es.forEach((e) => e.isIntersecting && e.target.classList.add("in")), { threshold: 0.12 });
    document.querySelectorAll(".reveal:not(.in)").forEach((n) => io.observe(n));
    return () => io.disconnect();
  }, deps); // eslint-disable-line react-hooks/exhaustive-deps
}

/* ---------------- hero */
const SPEEDS = [60, 300, 1200];
function Hero({ ov, error, retry }: { ov?: Overview; error?: string; retry: () => void }) {
  const blocks = ov?.replay ?? [];
  const [idx, setIdx] = useState(8);
  const [since, setSince] = useState(0);
  const [speed, setSpeed] = useState(300);

  useEffect(() => {
    if (!blocks.length) return;
    let last = performance.now(), acc = 0, i = Math.min(8, blocks.length - 1), raf = 0, shown = 0;
    setIdx(i);
    const loop = (now: number) => {
      raf = requestAnimationFrame(loop);
      const dt = Math.min((now - last) / 1000, 0.25);
      last = now;
      if (document.hidden) return;
      acc += dt * speed;
      const need = Math.max(blocks[(i + 1) % blocks.length].gap, 1);
      if (acc >= need) { i = (i + 1) % blocks.length; acc = 0; setIdx(i); }
      if (now - shown > 90) { shown = now; setSince(acc); }
    };
    raf = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(raf);
  }, [blocks, speed]);

  const cur = blocks[idx];
  const day = (iso: string) => new Date(iso).toUTCString().slice(5, 16);
  return (
    <section className="hero" aria-labelledby="hero-title">
      <div className="wrap hero-grid">
        <div>
          <span className="eyebrow"><span className="dot" />MM0501 Probability &amp; Statistics, VIT Pune</span>
          <h1 id="hero-title" className="display">What does a Bitcoin block cost?</h1>
          {ov && (
            <p className="answer">Usually about <b className="num">{fmt(ov.median_fee)} sat</b> per transaction. But it swings by {fmt(ov.cv_percent)}&nbsp;% from block to block.</p>
          )}
          <p className="lede">
            {ov ? <>We took <b>{fmt(ov.n_blocks)}</b> real blocks mined between <b>{day(ov.start)}</b> and <b>{day(ov.end)}</b> (UTC) and ran five tests from our syllabus on them. Every number on this page is computed live from that data.</>
              : <>Five tests from our syllabus, run live on real Bitcoin blocks.</>}
          </p>
          <div className="cta-row">
            <a className="btn btn-lime" href="#predict">Predict a fee <span className="arrow">→</span></a>
            <a className="btn btn-ghost" href="#tests">See the five tests</a>
          </div>
          {error && (
            <div className="error" role="alert" style={{ marginTop: 28 }}>
              <h4>Data unavailable</h4>
              <p>{error}</p>
              <button className="btn btn-ghost" onClick={retry}>Try again</button>
            </div>
          )}
        </div>

        {cur ? (
          <div className="hud">
            <div className="hud-top">
              <span className="live"><span className="dot" />Replaying the last {blocks.length} blocks</span>
              <span className="speed" role="group" aria-label="Replay speed">
                {SPEEDS.map((s) => <button key={s} aria-pressed={s === speed} onClick={() => setSpeed(s)}>{s}×</button>)}
              </span>
            </div>
            <div className="hud-stage">
              <Suspense fallback={null}><Chain3D blocks={blocks} index={idx} /></Suspense>
            </div>
            <div className="hud-fee"><b className="num">{fmt(cur.fee)} sat</b><span>per transaction in block {fmt(cur.h)}</span></div>
            <div className="hud-row">
              <div><small>Transactions</small><strong className="num">{fmt(cur.tx)}</strong></div>
              <div><small>Waited for it</small><strong className="num">{dur(cur.gap)}</strong></div>
              <div><small>Since last block</small><strong className="num">{dur(since)}</strong></div>
            </div>
            <div className="timebar" aria-hidden>
              <i style={{ width: `${Math.min(since / 1800, 1) * 100}%` }} />
              {ov && <em style={{ left: `${Math.min(ov.mean_gap / 1800, 1) * 100}%` }} />}
            </div>
            <p className="hud-note">
              {cur.gap < 0
                ? "This block's timestamp is earlier than the one before it. Miner clocks disagree; we keep these gaps."
                : "Black mark: the average gap. Waiting longer doesn't make the next block due."}
            </p>
          </div>
        ) : !error && <div className="skeleton" style={{ minHeight: 420 }} />}
      </div>
      {ov && (
        <div className="wrap hero-stats">
          <div><b className="num">{fmt(ov.n_blocks)}</b><span>real blocks studied</span></div>
          <div><b className="num">{dur(ov.mean_gap)}</b><span>average wait for a block</span></div>
          <div><b className="num">{ov.blocks_per_hour.toFixed(2)}</b><span>blocks per hour (λ)</span></div>
          <div><b className="num">{fmt(ov.mean_fee)} sat</b><span>mean fee (median {fmt(ov.median_fee)})</span></div>
        </div>
      )}
    </section>
  );
}

function Band({ ov, flip }: { ov?: Overview; flip?: boolean }) {
  const items = ov
    ? [`${fmt(ov.n_blocks)} real blocks`, `median ${fmt(ov.median_fee)} sat`, `λ = ${ov.blocks_per_hour.toFixed(2)} / hour`, `mean gap ${dur(ov.mean_gap)}`, "five syllabus tests", "computed live"]
    : ["Bitcoin fee predictor", "five syllabus tests", "computed live"];
  const row = items.map((t, i) => <span key={i}>{t}<i>✦</i></span>);
  return (
    <div className={`band ${flip ? "flip" : ""}`} aria-hidden>
      <div className="band-track">{row}{row}{row}{row}</div>
    </div>
  );
}

/* ---------------- predictor */
function Predict({ dataset }: { dataset: Dataset }) {
  const [tx, setTx] = useState(3600);
  const r = useApi<Regression>(`/api/regression?dataset=${dataset}&tx=${tx}`);
  const d = r.data;
  const presets = d ? [["Quiet block", d.lo_x], ["Typical block", d.median_x], ["Busy block", d.hi_x]] as const : [];
  const yRange = useMemo(() => {
    if (!d) return null;
    let lo = Infinity, hi = -Infinity;
    for (const p of d.points) { lo = Math.min(lo, p[1]); hi = Math.max(hi, p[1]); }
    return [lo, hi] as const;
  }, [d?.points]); // eslint-disable-line react-hooks/exhaustive-deps
  const pos = (v: number) => (yRange ? Math.max(0, Math.min(100, ((Math.log(v) - yRange[0]) / (yRange[1] - yRange[0])) * 100)) : 50);
  const sliderMax = 12000, pct = (Math.min(tx, sliderMax) / sliderMax) * 100;

  return (
    <section className="section predict" id="predict" aria-labelledby="predict-title">
      <div className="wrap">
        <div className="sec-head reveal">
          <span className="sec-no">01</span>
          <h2 id="predict-title" className="display">Predict the fee</h2>
          <p>Tell us how many transactions the next block carries. Our least-squares line on the log fee returns the typical fee and a ±1 standard-error range, straight from <code>src/regression.py</code>.</p>
        </div>

        <div className="predict-grid reveal">
          <div className="panel">
            <span className="label">Transactions in the block</span>
            <div className="tx-big num">{fmt(tx)}<small>tx</small></div>
            <input className="range" type="range" min={100} max={sliderMax} step={25} value={Math.min(tx, sliderMax)} style={{ ["--p" as string]: `${pct}%` }}
              aria-label="Transactions in the block" onChange={(e) => setTx(+e.target.value)} />
            <div className="range-ends"><span>100</span><span>{fmt(sliderMax)}</span></div>
            <div className="chips">
              {presets.map(([label, v]) => (
                <button key={label} className="chip" aria-pressed={tx === v} onClick={() => setTx(v)}>{label} · {fmt(v)}</button>
              ))}
              <label className="chip" style={{ display: "inline-flex", gap: 8, alignItems: "center" }}>
                Exact
                <input className="num-input" type="number" min={1} max={20000} value={tx} aria-label="Exact transaction count"
                  onChange={(e) => { const v = Math.round(+e.target.value); if (v >= 1 && v <= 20000) setTx(v); }} />
              </label>
            </div>
            {d && <p className="eq">log(fee) = <b>{d.a.toFixed(3)}</b> {d.b < 0 ? "−" : "+"} <b>{Math.abs(d.b).toFixed(6)}</b> × transactions &nbsp;·&nbsp; R² = <b>{d.r2.toFixed(3)}</b></p>}
          </div>

          <div className="panel result" aria-live="polite">
            {r.loading && <div className="loading-bar" aria-hidden />}
            <span className="label">Predicted typical fee</span>
            {r.error && !d ? (
              <div className="error" style={{ marginTop: 16 }}><h4>No prediction</h4><p>{r.error}</p><button className="btn btn-ghost" onClick={r.retry}>Try again</button></div>
            ) : d ? (
              <>
                <div className={`fee-big num ${r.loading ? "stale" : ""}`}>{fmt(d.pred_fee)}</div>
                <div className="fee-unit">satoshi per transaction</div>
                <div className="band-bar" aria-hidden>
                  <div className="track" />
                  <div className="fill" style={{ left: `${pos(d.range_low)}%`, width: `${pos(d.range_high) - pos(d.range_low)}%` }} />
                  <div className="pin" style={{ left: `calc(${pos(d.pred_fee)}% - 2px)` }} />
                </div>
                <div className="band-labels"><span>cheapest block in data</span><span>Typical range <b>{fmt(d.range_low)} – {fmt(d.range_high)} sat</b></span><span>priciest</span></div>
                {!d.in_range && <div className="callout blue"><b>Outside our data.</b> We saw {fmt(d.lo_x)}–{fmt(d.hi_x)} transactions per block. A straight line shouldn't be trusted far outside its data.</div>}
                <div className="callout lime"><b>Surprise: busier blocks are cheaper per transaction.</b> The slope is negative because avg fee = total fee ÷ transactions. See the regression test below.</div>
              </>
            ) : <div className="skeleton" style={{ minHeight: 300, marginTop: 16 }} />}
          </div>
        </div>

        {d && (
          <div className="reveal" style={{ marginTop: 28 }}>
            <ChartCard title={`${fmt(d.points.length)} real blocks · least-squares line · your input`} loading={r.loading}
              legend={<><Key color={COLORS.DATA} label="blocks" /><Key color={COLORS.MODEL} label="fitted line ± 1 SE" /><Key color={COLORS.FOCUS} label="your input" /></>}>
              <ScatterChart points={d.points} a={d.a} b={d.b} se={d.se} tx={tx} pred={d.pred_log} />
            </ChartCard>
          </div>
        )}
      </div>
    </section>
  );
}

/* ---------------- footer */
function Footer({ ov }: { ov?: Overview }) {
  return (
    <footer className="foot" id="about">
      <div className="wrap">
        <div className="foot-word">Bitcoin Fee Predictor</div>
        <div className="foot-grid">
          <div>
            <h5>The project</h5>
            <p style={{ margin: 0 }}>A course project for MM0501 Probability and Statistics at VIT Pune. Five syllabus topics applied to real Bitcoin blocks. Every formula is written in plain code in <code>src/</code>; SciPy is only used to check results.</p>
          </div>
          <div>
            <h5>Data</h5>
            <ul>
              <li>Source: mempool.space public API</li>
              {ov && <li>{fmt(ov.n_blocks)} blocks, {new Date(ov.start).toUTCString().slice(5, 16)} – {new Date(ov.end).toUTCString().slice(5, 16)}</li>}
              <li>All times UTC (India is UTC+5:30)</li>
            </ul>
          </div>
          <div>
            <h5>Team split</h5>
            <ul>
              <li>A — Exponential + Poisson</li>
              <li>B — Regression</li>
              <li>C — ANOVA</li>
              <li>D — Confidence interval + data</li>
            </ul>
          </div>
        </div>
      </div>
    </footer>
  );
}
