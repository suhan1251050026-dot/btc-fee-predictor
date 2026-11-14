import { useState, type ReactNode } from "react";
import { fmt, pfmt, useApi, type Anova, type Confidence, type Dataset, type Exponential, type Overview, type Poisson, type Regression } from "./api";
import { BoxChart, ChartCard, COLORS, ExpChart, Histogram, IntervalsChart, Key, PoissonChart } from "./charts";

const TABS = [
  { id: "overview", name: "The data", unit: "Unit 1 · Descriptive" },
  { id: "exp", name: "Waiting time", unit: "Unit 2 · Exponential" },
  { id: "poisson", name: "Blocks per hour", unit: "Unit 2 · Poisson" },
  { id: "reg", name: "Fee vs. load", unit: "Unit 4 · Regression" },
  { id: "anova", name: "Time of day", unit: "Unit 4 · ANOVA" },
  { id: "ci", name: "The true mean", unit: "Unit 4 · Confidence interval" },
] as const;
type TabId = (typeof TABS)[number]["id"];

export default function Tests({ dataset, overview }: { dataset: Dataset; overview: Overview }) {
  const [tab, setTab] = useState<TabId>("overview");
  return (
    <section className="section" id="tests" aria-labelledby="tests-title">
      <div className="wrap">
        <div className="sec-head reveal">
          <span className="sec-no">02</span>
          <h2 id="tests-title" className="display">Five tests. One chain.</h2>
          <p>Each page runs one syllabus topic on the same blocks. Move the controls: the Python backend recomputes with the functions in <code>src/</code>.</p>
        </div>
        <div className="tabs reveal" role="tablist" aria-label="Statistics tests">
          {TABS.map((t, i) => (
            <button key={t.id} role="tab" id={`tab-${t.id}`} aria-selected={tab === t.id} aria-controls={`panel-${t.id}`} className="tab" onClick={() => setTab(t.id)}>
              <i>{String(i).padStart(2, "0")}</i><span><b>{t.name}</b><small>{t.unit}</small></span>
            </button>
          ))}
        </div>
        <div role="tabpanel" id={`panel-${tab}`} aria-labelledby={`tab-${tab}`}>
          {tab === "overview" && <OverviewPanel ov={overview} />}
          {tab === "exp" && <ExpPanel ds={dataset} />}
          {tab === "poisson" && <PoissonPanel ds={dataset} />}
          {tab === "reg" && <RegPanel ds={dataset} />}
          {tab === "anova" && <AnovaPanel ds={dataset} />}
          {tab === "ci" && <CiPanel ds={dataset} />}
        </div>
      </div>
    </section>
  );
}

function Head({ title, analogy }: { title: ReactNode; analogy: string }) {
  return (
    <div className="test-head">
      <h3 className="display">{title}</h3>
      <p className="analogy">{analogy}</p>
    </div>
  );
}
const M = ({ label, value, note, hot }: { label: string; value: ReactNode; note?: ReactNode; hot?: boolean }) => (
  <div className={`metric ${hot ? "hot" : ""}`}><small>{label}</small><b className="num">{value}</b>{note && <em>{note}</em>}</div>
);
function Slider({ label, value, min, max, step = 1, onChange, suffix = "" }: { label: string; value: number; min: number; max: number; step?: number; onChange: (v: number) => void; suffix?: string }) {
  return (
    <label className="control">
      <span className="control-top">{label}<b>{value}{suffix}</b></span>
      <input className="range" type="range" min={min} max={max} step={step} value={value} style={{ ["--p" as string]: `${((value - min) / (max - min)) * 100}%` }} onChange={(e) => onChange(+e.target.value)} />
    </label>
  );
}
function Seg<T extends string | number>({ label, options, value, onChange, show = String }: { label: string; options: readonly T[]; value: T; onChange: (v: T) => void; show?: (v: T) => string }) {
  return (
    <div className="control" style={{ minWidth: 0, flex: "0 0 auto" }}>
      <span className="control-top">{label}</span>
      <div className="seg" role="group" aria-label={label}>
        {options.map((o) => <button key={String(o)} aria-pressed={o === value} onClick={() => onChange(o)}>{show(o)}</button>)}
      </div>
    </div>
  );
}
function Load<T>({ q, children }: { q: { data?: T; error?: string; loading: boolean; retry: () => void }; children: (d: T) => ReactNode }) {
  if (q.error && !q.data) return <div className="error" role="alert"><h4>Couldn't run this test</h4><p>{q.error}</p><button className="btn btn-ghost" onClick={q.retry}>Try again</button></div>;
  if (!q.data) return <div className="skeleton" />;
  return <div style={{ position: "relative" }}>{q.loading && <div className="loading-bar" aria-hidden />}{children(q.data)}</div>;
}

/* ---------------- Unit 1 */
function OverviewPanel({ ov }: { ov: Overview }) {
  const [log, setLog] = useState(false);
  const fee = ov.table[2];
  return (
    <>
      <Head title={<>The data at a glance</>} analogy="A doctor checks height, weight and pulse before any treatment. We check centre, spread and shape." />
      <div className="metrics">
        <M hot label="Mean fee" value={`${fmt(fee.mean)} sat`} note="per transaction" />
        <M label="Median fee" value={`${fmt(fee.median)} sat`} note="half the blocks pay less" />
        <M label="CV of fee" value={`${fmt(fee.cv_percent)} %`} note="standard deviation ÷ mean" />
        <M label="Blocks" value={fmt(ov.n_blocks)} note={`${fmt(fee.n)} with a fee`} />
      </div>
      <div className="callout blue" style={{ marginTop: 0, marginBottom: 20 }}>The mean sits above the median and the CV is near 100 %. The fee is <b>right-skewed</b>, which is why the other tests use the <b>log</b> of the fee.</div>
      <div className="split">
        <ChartCard title={log ? "log(average fee) per block" : "Average fee per block (raw, skewed)"}
          legend={<div className="seg" role="group" aria-label="Scale"><button aria-pressed={!log} onClick={() => setLog(false)}>Raw</button><button aria-pressed={log} onClick={() => setLog(true)}>Log</button></div>}>
          <Histogram bins={log ? ov.hist_log : ov.hist_raw} xLabel={log ? "log(avg_fee)" : "avg_fee (satoshi per transaction)"} yLabel="blocks" />
        </ChartCard>
        <div className="table-scroll">
          <table className="table">
            <thead><tr><th>Measure</th><th>Mean</th><th>Median</th><th>SD</th><th>CV %</th></tr></thead>
            <tbody>{ov.table.map((r) => <tr key={r.label}><td>{r.label}</td><td>{fmt(r.mean, 1)}</td><td>{fmt(r.median, 1)}</td><td>{fmt(r.sd, 1)}</td><td>{fmt(r.cv_percent, 1)}</td></tr>)}</tbody>
          </table>
          <table className="table">
            <thead><tr><th>Measure</th><th>n</th><th>Min</th><th>Max</th></tr></thead>
            <tbody>{ov.table.map((r) => <tr key={r.label}><td>{r.label}</td><td>{fmt(r.n)}</td><td>{fmt(r.min, 1)}</td><td>{fmt(r.max, 1)}</td></tr>)}</tbody>
          </table>
        </div>
      </div>
    </>
  );
}

/* ---------------- Unit 2: exponential */
function ExpPanel({ ds }: { ds: Dataset }) {
  const [t, setT] = useState(20), [s, setS] = useState(10);
  const q = useApi<Exponential>(`/api/exponential?dataset=${ds}&t_min=${t}&s_min=${s}`);
  return (
    <>
      <Head title={<>How long until the next block?</>} analogy="You wait for the first raindrop on your hand. The rain has no memory: waiting longer doesn't make a drop 'due'." />
      <Load q={q}>{(d) => (
        <>
          <div className="metrics">
            <M hot label="Mean gap" value={`${Math.round(d.mean_gap)} s`} note={`${(d.mean_gap / 60).toFixed(1)} minutes`} />
            <M label="SD ÷ mean" value={d.sd_over_mean.toFixed(2)} note="about 1 for an exponential" />
            <M label="λ (blocks per hour)" value={d.blocks_per_hour.toFixed(2)} note="λ = 1 ÷ mean gap" />
            <M label="KS test p-value" value={d.ks_p.toFixed(3)} note={d.ks_p > 0.05 ? "above 0.05: no evidence against the model" : "below 0.05: the model is rejected"} />
          </div>
          <div className="controls"><Slider label="Wait longer than t minutes" value={t} min={1} max={60} onChange={setT} suffix=" min" /></div>
          <div className="metrics" style={{ gridTemplateColumns: "repeat(2, 1fr)" }}>
            <M hot label={`Model: P(wait > ${t} min)`} value={d.p_model.toFixed(3)} />
            <M label={`Real data: share of gaps > ${t} min`} value={d.p_real.toFixed(3)} note={`difference ${((d.p_real - d.p_model) * 100).toFixed(1)} percentage points`} />
          </div>
          <p className="formula">P(X &gt; t) = e<sup>−λt</sup> = e<sup>−{t * 60}/{Math.round(d.mean_gap)}</sup> = <b>{d.p_model.toFixed(4)}</b></p>
          <ChartCard title="Real gaps against the exponential model" legend={<><Key color={COLORS.DATA} label="real gaps" /><Key color={COLORS.MODEL} label="model + P(wait > t)" /></>}>
            <ExpChart hist={d.hist} curve={d.curve} tMin={t} />
          </ChartCard>
          <details className="more">
            <summary>Memoryless test: does waiting make a block "due"?</summary>
            <div>
              <div className="controls" style={{ marginTop: 6 }}><Slider label="We already waited s minutes" value={s} min={1} max={30} onChange={setS} suffix=" min" /></div>
              {d.memoryless ? (
                <p>Of the <b>{fmt(d.memoryless.n)}</b> gaps longer than {s} min, <b>{d.memoryless.conditional.toFixed(3)}</b> lasted another {t} min or more. Fresh start: P(wait &gt; {t} min) = <b>{d.p_real.toFixed(3)}</b>. If the two are close, the process has no memory.</p>
              ) : <p>Too few long gaps for this check. Choose a smaller s.</p>}
              <p>{d.out_of_order} block timestamps were out of order. We sort them before computing gaps and never drop negative gaps.</p>
            </div>
          </details>
        </>
      )}</Load>
    </>
  );
}

/* ---------------- Unit 2: Poisson */
function PoissonPanel({ ds }: { ds: Dataset }) {
  const [k, setK] = useState(10);
  const q = useApi<Poisson>(`/api/poisson?dataset=${ds}&k=${k}`);
  return (
    <>
      <Head title={<>How many blocks in one hour?</>} analogy="Count the raindrops on your hand in one hour. The wait between drops is exponential. The count is Poisson." />
      <Load q={q}>{(d) => (
        <>
          <div className="metrics">
            <M label="Full hours" value={fmt(d.hours)} note="first and last hour dropped" />
            <M hot label="λ (mean per hour)" value={d.lam.toFixed(2)} note={`theory: 6 · gaps say ${d.cross_check.toFixed(2)}`} />
            <M label="Variance ÷ mean" value={d.var_over_mean.toFixed(2)} note="about 1 for a Poisson" />
            <M label="Chi-square p-value" value={d.p_chi.toFixed(3)} note={`χ² = ${d.chi2.toFixed(2)}, df = ${d.dof}`} />
          </div>
          <div className="controls"><Slider label="Number of blocks k in one hour" value={k} min={0} max={15} onChange={setK} /></div>
          <div className="metrics">
            <M hot label={`Model: P(X = ${k})`} value={d.p_eq.toFixed(4)} />
            <M label={`Real: hours with ${k}`} value={d.real_eq.toFixed(4)} />
            <M hot label={`Model: P(X ≥ ${k})`} value={d.p_ge.toFixed(4)} />
            <M label={`Real: hours with ≥ ${k}`} value={d.real_ge.toFixed(4)} />
          </div>
          <p className="formula">P(X = {k}) = e<sup>−{d.lam.toFixed(2)}</sup> · {d.lam.toFixed(2)}<sup>{k}</sup> ÷ {k}! = <b>{d.p_eq.toFixed(4)}</b></p>
          <ChartCard title="Share of hours with k blocks" legend={<><Key color={COLORS.DATA} label="real hours" /><Key color={COLORS.INK} outline label={`Poisson λ = ${d.lam.toFixed(2)}`} /><Key color={COLORS.FOCUS} label="your k" /></>}>
            <PoissonChart bars={d.bars} k={k} />
          </ChartCard>
        </>
      )}</Load>
    </>
  );
}

/* ---------------- Unit 4: regression */
function RegPanel({ ds }: { ds: Dataset }) {
  const q = useApi<Regression>(`/api/regression?dataset=${ds}&tx=3600`, 0);
  return (
    <>
      <Head title={<>Can load predict the fee?</>} analogy="Predict a taxi fare from the distance. Draw the best straight line. The standard error of estimate is the typical miss of a dart." />
      <Load q={q}>{(d) => (
        <>
          <div className="metrics">
            <M label="Slope b" value={d.b.toFixed(6)} note="per extra transaction (log units)" />
            <M label="Correlation r" value={d.r.toFixed(3)} />
            <M hot label="R²" value={d.r2.toFixed(3)} note={`${Math.round(d.r2 * 100)} % of log-fee variation explained`} />
            <M label="Std error of estimate" value={d.se.toFixed(3)} note="in log units" />
          </div>
          <p className="formula">log(fee) = <b>{d.a.toFixed(3)}</b> {d.b < 0 ? "−" : "+"} <b>{Math.abs(d.b).toFixed(6)}</b> × tx_count</p>
          <div className="callout lime" style={{ marginTop: 0 }}><b>The slope is negative.</b> We expected busy blocks to be expensive. Two checks with our data show why. (Try it in the predictor above.)</div>
          <div className="split" style={{ marginTop: 22 }}>
            <div className="panel">
              <h4 className="display" style={{ margin: "0 0 10px", fontSize: "1.2rem" }}>1. The ratio effect</h4>
              <p className="muted" style={{ margin: 0 }}>avg_fee = total_fee ÷ tx_count, so tx_count sits inside both x and y. Log-log slope of avg_fee on tx_count: <b className="lime">{d.loglog_avg.toFixed(2)}</b>. Of that, −1.00 comes only from the division. The real link between the total fee and tx_count is only <b className="lime">{d.loglog_total.toFixed(2)}</b>. Like sharing one pizza among more friends: each slice gets smaller.</p>
              <h4 className="display" style={{ margin: "22px 0 10px", fontSize: "1.2rem" }}>Conclusion</h4>
              <p className="muted" style={{ margin: 0 }}>tx_count is a poor measure of demand. A high R² does not prove a cause.</p>
            </div>
            <div>
              <h4 className="display" style={{ margin: "0 0 10px", fontSize: "1.2rem" }}>2. Small transactions</h4>
              <div className="table-scroll">
                <table className="table">
                  <thead><tr><th>Block size</th><th>Median bytes / tx</th><th>Median fee / tx (sat)</th></tr></thead>
                  <tbody>{d.quartiles.map((r) => <tr key={r.range}><td>{r.range}</td><td>{fmt(r.bytes_per_tx)}</td><td>{fmt(r.fee_per_tx)}</td></tr>)}</tbody>
                </table>
              </div>
            </div>
          </div>
        </>
      )}</Load>
    </>
  );
}

/* ---------------- Unit 4: ANOVA */
const ALPHAS = ["0.1", "0.05", "0.01", "0.001"] as const;
function AnovaPanel({ ds }: { ds: Dataset }) {
  const [alpha, setAlpha] = useState<(typeof ALPHAS)[number]>("0.05");
  const [tz, setTz] = useState<"utc" | "ist">("utc");
  const q = useApi<Anova>(`/api/anova?dataset=${ds}&alpha=${alpha}&tz=${tz}`, 0);
  return (
    <>
      <Head title={<>Does the clock change the fee?</>} analogy="Compare the price of tea at four stalls. ANOVA asks: is the difference real, or only random wobble? F = difference between groups ÷ noise inside groups." />
      <Load q={q}>{(d) => (
        <>
          <div className="metrics">
            <M hot label="F" value={d.F.toFixed(2)} note={`df = ${d.df_between}, ${d.df_within}`} />
            <M label="p-value" value={pfmt(d.p)} note="from the F distribution" />
            <M label="Kruskal-Wallis p" value={pfmt(d.p_kw)} note="second test, no normal shape needed" />
            <M label="Effect size η²" value={d.eta2.toFixed(3)} note={`slots explain ${Math.round(d.eta2 * 100)} % of the variation`} />
          </div>
          <div className="controls">
            <Seg label="Significance level α" options={ALPHAS} value={alpha} onChange={setAlpha} />
            <Seg label="Show slots in" options={["utc", "ist"] as const} value={tz} onChange={setTz} show={(v) => (v === "utc" ? "UTC" : "India (IST)")} />
          </div>
          <div className={`callout ${d.reject ? "lime" : "blue"}`} style={{ marginTop: 0, marginBottom: 20 }}>
            {d.reject ? <>p &lt; {alpha}: we <b>reject H₀</b>. At least one time slot has a different mean fee.</> : <>p ≥ {alpha}: we <b>cannot reject H₀</b>. No evidence that the slots differ.</>}
          </div>
          <div className="split">
            <ChartCard title={`log fee by time slot (${tz === "utc" ? "UTC" : "IST"})`} legend={<><Key color={COLORS.FOCUS} label="middle 50 %" /><Key color={COLORS.MODEL} label="median" /></>}>
              <BoxChart slots={d.slots} />
            </ChartCard>
            <div className="table-scroll">
              <table className="table">
                <thead><tr><th>Slot</th><th>Blocks</th><th>Mean log fee</th><th>Typical fee</th></tr></thead>
                <tbody>{d.slots.map((s) => <tr key={s.name}><td>{s.name} <span className="muted">{s.hours}</span></td><td>{fmt(s.blocks)}</td><td>{s.mean_log.toFixed(3)}</td><td>{fmt(s.typical_fee)} sat</td></tr>)}</tbody>
              </table>
            </div>
          </div>
          <p className="muted" style={{ marginTop: 18 }}>The p-value is tiny because we have many blocks. η² shows the size: the time slot explains only a small part of the fee variation.</p>
        </>
      )}</Load>
    </>
  );
}

/* ---------------- Unit 4: confidence interval */
const LEVELS = ["0.8", "0.9", "0.95", "0.99"] as const;
function CiPanel({ ds }: { ds: Dataset }) {
  const [level, setLevel] = useState<(typeof LEVELS)[number]>("0.95");
  const [n, setN] = useState(50), [reps, setReps] = useState(100), [seed, setSeed] = useState(42);
  const q = useApi<Confidence>(`/api/confidence?dataset=${ds}&level=${level}&n=${n}&reps=${reps}&seed=${seed}`);
  const pct = (v: string) => `${Math.round(+v * 100)} %`;
  return (
    <>
      <Head title={<>Where is the true mean?</>} analogy="You cannot see the true average. You throw a net over it. A 95 % net catches the true value in about 95 of 100 repeated studies." />
      <Load q={q}>{(d) => (
        <>
          <div className="controls"><Seg label="Confidence level" options={LEVELS} value={level} onChange={setLevel} show={pct} /></div>
          <div className="metrics">
            <M label="Sample size n" value={fmt(d.full.n)} />
            <M label="Mean fee" value={`${fmt(d.full.mean, 1)} sat`} />
            <M label="Margin" value={`± ${fmt(d.full.margin, 1)}`} note="t × s ÷ √n" />
            <M hot label={`${pct(level)} interval`} value={`${fmt(d.full.lower)}–${fmt(d.full.upper)}`} note="satoshi per transaction" />
          </div>
          <p className="formula">x̄ ± t·s/√n = {d.full.mean.toFixed(1)} ± {d.full.t_critical.toFixed(3)} × {d.full.sd.toFixed(1)} / √{d.full.n} = <b>{d.full.mean.toFixed(1)} ± {d.full.margin.toFixed(1)}</b></p>
          <h4 className="display" style={{ margin: "34px 0 6px", fontSize: "1.5rem" }}>Classroom experiment: does the net catch the mean?</h4>
          <p className="muted" style={{ marginTop: 0 }}>Treat all blocks as the population. Draw many small random samples, build an interval from each, count how many catch the true mean.</p>
          <div className="controls">
            <Slider label="Blocks in each sample (n)" value={n} min={10} max={500} step={10} onChange={setN} />
            <Slider label="Number of samples" value={reps} min={20} max={200} step={10} onChange={setReps} />
            <button className="btn btn-ghost" onClick={() => setSeed(Math.floor(Math.random() * 10000))}>Draw new samples · seed {seed}</button>
          </div>
          <div className="metrics" style={{ gridTemplateColumns: "1fr" }}>
            <M hot label={`Intervals that caught the true mean (${fmt(d.true_mean)} sat)`} value={`${d.hits} of ${d.reps}`} note={`hit rate ${Math.round((d.hits / d.reps) * 100)} %, target ${pct(level)}`} />
          </div>
          <ChartCard title="Each line is one sample's interval" legend={<><Key color={COLORS.DATA} label="caught the mean" /><Key color={COLORS.MODEL} label="missed" /><Key color={COLORS.INK} outline label="true mean" /></>}>
            <IntervalsChart intervals={d.intervals} trueMean={d.true_mean} />
          </ChartCard>
          <p className="muted" style={{ marginTop: 16 }}>Fee data is skewed, so with small n the hit rate can fall below the target. Increase n and watch it move closer: the central limit theorem at work.</p>
        </>
      )}</Load>
    </>
  );
}
