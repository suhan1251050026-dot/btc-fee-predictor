import type { ReactNode } from "react";
import type { Bin, Box } from "./api";

const INK = "#16101F", RED = "#E34234", LIME = "#D4FF4F", LAV = "#B79BDB";
const DATA = INK, MODEL = RED, FOCUS = LIME;
const W = 760, H = 340, M = { l: 58, r: 18, t: 14, b: 46 };

type S = (v: number) => number;
const lin = (d0: number, d1: number, r0: number, r1: number): S => {
  const k = (r1 - r0) / (d1 - d0 || 1);
  return (v) => r0 + (v - d0) * k;
};
function niceTicks(min: number, max: number, count = 5) {
  const span = max - min || 1, raw = span / count, mag = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => span / s <= count) ?? raw;
  const out: number[] = [];
  for (let v = Math.ceil(min / step) * step; v <= max + 1e-9; v += step) out.push(+v.toFixed(10));
  return out;
}
const tick = (v: number) => (Math.abs(v) >= 1000 ? `${+(v / 1000).toFixed(1)}k` : Math.abs(v) < 0.01 && v !== 0 ? v.toExponential(0) : `${+v.toFixed(3)}`);

type FrameProps = {
  x: [number, number]; y: [number, number]; xLabel: string; yLabel: string; h?: number;
  xTicks?: number[]; xFmt?: (v: number) => string; yTicks?: boolean;
  children: (sx: S, sy: S, glow: string) => ReactNode;
};
export function Frame({ x, y, xLabel, yLabel, h = H, xTicks, xFmt = tick, yTicks = true, children }: FrameProps) {
  const sx = lin(x[0], x[1], M.l, W - M.r), sy = lin(y[0], y[1], h - M.b, M.t);
  const xt = xTicks ?? niceTicks(x[0], x[1], 6), yt = niceTicks(y[0], y[1], 5);
  return (
    <svg viewBox={`0 0 ${W} ${h}`} role="img" aria-label={`${yLabel} against ${xLabel}`}>
            <g className="grid">{yt.map((v) => <line key={v} x1={M.l} x2={W - M.r} y1={sy(v)} y2={sy(v)} />)}</g>
      <g className="axis">
        <line x1={M.l} x2={W - M.r} y1={h - M.b} y2={h - M.b} />
        {xt.map((v) => (
          <text key={v} x={sx(v)} y={h - M.b + 18} textAnchor="middle">{xFmt(v)}</text>
        ))}
        {yTicks && yt.map((v) => <text key={v} x={M.l - 10} y={sy(v) + 4} textAnchor="end">{tick(v)}</text>)}
      </g>
      <text className="axis-label" x={(M.l + W - M.r) / 2} y={h - 6} textAnchor="middle">{xLabel}</text>
      <text className="axis-label" transform={`translate(14 ${(h - M.b + M.t) / 2}) rotate(-90)`} textAnchor="middle">{yLabel}</text>
      {children(sx, sy, "")}
    </svg>
  );
}

export function Histogram({ bins, xLabel, yLabel }: { bins: Bin[]; xLabel: string; yLabel: string }) {
  const ymax = Math.max(...bins.map((b) => b.y)) * 1.08;
  return (
    <Frame x={[bins[0].x0, bins[bins.length - 1].x1]} y={[0, ymax]} xLabel={xLabel} yLabel={yLabel}>
      {(sx, sy, g) => (
        <g>
          {bins.map((b, i) => (
            <rect key={i} x={sx(b.x0) + 0.6} width={Math.max(0.5, sx(b.x1) - sx(b.x0) - 1.2)} y={sy(b.y)} height={sy(0) - sy(b.y)}
              rx={1.5} fill={FOCUS} stroke={INK} strokeWidth={1} />
          ))}
        </g>
      )}
    </Frame>
  );
}

export function ExpChart({ hist, curve, tMin }: { hist: Bin[]; curve: { x: number; y: number }[]; tMin: number }) {
  const xmax = curve[curve.length - 1].x, ymax = Math.max(...hist.map((b) => b.y), ...curve.map((c) => c.y)) * 1.06;
  const shown = hist.filter((b) => b.x0 < xmax);
  return (
    <Frame x={[0, xmax]} y={[0, ymax]} xLabel="gap between blocks (minutes, UTC data)" yLabel="density">
      {(sx, sy, g) => {
        const line = curve.map((c, i) => `${i ? "L" : "M"}${sx(c.x)},${sy(c.y)}`).join("");
        const tail = curve.filter((c) => c.x >= tMin);
        const area = tail.length > 1 ? `M${sx(tail[0].x)},${sy(0)}` + tail.map((c) => `L${sx(c.x)},${sy(c.y)}`).join("") + `L${sx(tail[tail.length - 1].x)},${sy(0)}Z` : "";
        return (
          <g>
            {shown.map((b, i) => (
              <rect key={i} x={sx(b.x0) + 0.5} width={Math.max(0.5, sx(Math.min(b.x1, xmax)) - sx(b.x0) - 1)} y={sy(b.y)} height={sy(0) - sy(b.y)} rx={1.5} fill={DATA} fillOpacity={0.28} />
            ))}
            {area && <path d={area} fill={MODEL} fillOpacity={0.18} />}
            <path d={line} fill="none" stroke={MODEL} strokeWidth={2.6} />
            {tMin <= xmax && (
              <g>
                <line x1={sx(tMin)} x2={sx(tMin)} y1={sy(0)} y2={sy(ymax)} stroke={INK} strokeDasharray="4 5" strokeOpacity={0.7} />
                <text x={sx(tMin) + 6} y={sy(ymax) + 14} fill={INK} fontSize={12}>t = {tMin} min</text>
              </g>
            )}
          </g>
        );
      }}
    </Frame>
  );
}

export function PoissonChart({ bars, k }: { bars: { k: number; real: number; model: number }[]; k: number }) {
  const ymax = Math.max(...bars.flatMap((b) => [b.real, b.model])) * 1.1, n = bars.length;
  return (
    <Frame x={[-0.6, n - 0.4]} y={[0, ymax]} xLabel="blocks in one hour" yLabel="share of hours" xTicks={bars.map((b) => b.k)} xFmt={(v) => `${v}`}>
      {(sx, sy, g) => {
        const w = (sx(1) - sx(0)) * 0.36;
        return (
          <g>
            {bars.map((b) => {
              const on = b.k === k;
              return (
                <g key={b.k}>
                  <rect x={sx(b.k) - w - 1} width={w} y={sy(b.real)} height={sy(0) - sy(b.real)} rx={2} fill={on ? FOCUS : DATA} fillOpacity={on ? 1 : 0.75} stroke={INK} strokeWidth={on ? 1.5 : 0} />
                  <rect x={sx(b.k) + 1} width={w} y={sy(b.model)} height={sy(0) - sy(b.model)} rx={2} fill="none" stroke={MODEL} strokeWidth={on ? 2.2 : 1.4} />
                </g>
              );
            })}
          </g>
        );
      }}
    </Frame>
  );
}

export function ScatterChart({ points, a, b, se, tx, pred }: { points: [number, number][]; a: number; b: number; se: number; tx: number; pred: number }) {
  const xs = points.map((p) => p[0]), ys = points.map((p) => p[1]);
  const x0 = 0, x1 = Math.max(...xs, tx) * 1.03;
  const y0 = Math.min(...ys, pred) - 0.4, y1 = Math.max(...ys, pred) + 0.4;
  return (
    <Frame x={[x0, x1]} y={[y0, y1]} xLabel="transactions in block" yLabel="log(average fee)" h={380}>
      {(sx, sy, g) => {
        const lx = [Math.min(...xs), Math.max(...xs)];
        const band = `M${sx(lx[0])},${sy(a + b * lx[0] + se)}L${sx(lx[1])},${sy(a + b * lx[1] + se)}L${sx(lx[1])},${sy(a + b * lx[1] - se)}L${sx(lx[0])},${sy(a + b * lx[0] - se)}Z`;
        return (
          <g>
            {points.map((p, i) => <circle key={i} cx={sx(p[0])} cy={sy(p[1])} r={1.9} fill={DATA} fillOpacity={0.32} />)}
            <path d={band} fill={MODEL} fillOpacity={0.12} />
            <line x1={sx(lx[0])} y1={sy(a + b * lx[0])} x2={sx(lx[1])} y2={sy(a + b * lx[1])} stroke={MODEL} strokeWidth={2.6} />
            <line x1={sx(tx)} x2={sx(tx)} y1={sy(y0)} y2={sy(pred)} stroke={INK} strokeOpacity={0.55} strokeDasharray="3 5" />
            <line x1={sx(x0)} x2={sx(tx)} y1={sy(pred)} y2={sy(pred)} stroke={INK} strokeOpacity={0.55} strokeDasharray="3 5" />
            <circle cx={sx(tx)} cy={sy(pred)} r={13} fill={FOCUS} fillOpacity={0.55} stroke={INK} strokeOpacity={0.4} />
            <circle cx={sx(tx)} cy={sy(pred)} r={7} fill={FOCUS} stroke={INK} strokeWidth={2.5} />
          </g>
        );
      }}
    </Frame>
  );
}

export function BoxChart({ slots }: { slots: { name: string; hours: string; box: Box }[] }) {
  const all = slots.flatMap((s) => [s.box.lo, s.box.hi, ...s.box.outliers]);
  const y0 = Math.floor(Math.min(...all)), y1 = Math.ceil(Math.max(...all));
  return (
    <Frame x={[-0.5, slots.length - 0.5]} y={[y0, y1]} xLabel="time slot" yLabel="log(average fee)" xTicks={slots.map((_, i) => i)} xFmt={(i) => `${slots[i]?.name ?? ""} ${slots[i]?.hours ?? ""}`}>
      {(sx, sy, g) => (
        <g>
          {slots.map((s, i) => {
            const c = sx(i), w = (sx(1) - sx(0)) * 0.34, bx = s.box;
            return (
              <g key={s.name}>
                <line x1={c} x2={c} y1={sy(bx.lo)} y2={sy(bx.q1)} stroke={INK} strokeOpacity={0.6} />
                <line x1={c} x2={c} y1={sy(bx.q3)} y2={sy(bx.hi)} stroke={INK} strokeOpacity={0.6} />
                <line x1={c - w / 2} x2={c + w / 2} y1={sy(bx.lo)} y2={sy(bx.lo)} stroke={INK} strokeOpacity={0.6} />
                <line x1={c - w / 2} x2={c + w / 2} y1={sy(bx.hi)} y2={sy(bx.hi)} stroke={INK} strokeOpacity={0.6} />
                <rect x={c - w} width={w * 2} y={sy(bx.q3)} height={sy(bx.q1) - sy(bx.q3)} rx={6} fill={FOCUS} stroke={INK} strokeWidth={1.4} />
                <line x1={c - w} x2={c + w} y1={sy(bx.median)} y2={sy(bx.median)} stroke={MODEL} strokeWidth={3.2} />
                {bx.outliers.map((o, j) => <circle key={j} cx={c + ((j % 5) - 2) * 2} cy={sy(o)} r={2} fill={INK} fillOpacity={0.5} />)}
              </g>
            );
          })}
        </g>
      )}
    </Frame>
  );
}

export function IntervalsChart({ intervals, trueMean }: { intervals: { lower: number; upper: number; hit: boolean }[]; trueMean: number }) {
  const x0 = Math.min(...intervals.map((i) => i.lower), trueMean), x1 = Math.max(...intervals.map((i) => i.upper), trueMean);
  const pad = (x1 - x0) * 0.04, n = intervals.length;
  return (
    <Frame x={[x0 - pad, x1 + pad]} y={[-1, n]} xLabel="average fee (satoshi per transaction)" yLabel="sample number" h={420} yTicks={false}>
      {(sx, sy, g) => (
        <g>
          {intervals.map((iv, i) => (
            <line key={i} x1={sx(iv.lower)} x2={sx(iv.upper)} y1={sy(i)} y2={sy(i)} strokeLinecap="round"
              stroke={iv.hit ? DATA : MODEL} strokeOpacity={iv.hit ? 0.55 : 1} strokeWidth={iv.hit ? 1.6 : 2.6} />
          ))}
          <line x1={sx(trueMean)} x2={sx(trueMean)} y1={sy(-1)} y2={sy(n)} stroke={INK} strokeDasharray="5 5" />
        </g>
      )}
    </Frame>
  );
}

export function ChartCard({ title, legend, children, loading }: { title: ReactNode; legend?: ReactNode; children: ReactNode; loading?: boolean }) {
  return (
    <figure className="chart" style={{ margin: 0 }}>
      {loading && <div className="loading-bar" aria-hidden />}
      <figcaption className="chart-title"><b>{title}</b>{legend && <span className="legend">{legend}</span>}</figcaption>
      {children}
    </figure>
  );
}
export const Key = ({ color, label, outline }: { color: string; label: string; outline?: boolean }) => (
  <span><i style={outline ? { border: `1.5px solid ${color}`, height: 8 } : { background: color, outline: color === LIME ? `1px solid ${INK}` : undefined }} />{label}</span>
);
export const COLORS = { DATA, MODEL, FOCUS, INK, LAV };
