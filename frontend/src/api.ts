import { useCallback, useEffect, useState } from "react";

export type Dataset = "real" | "synthetic";
export type Bin = { x0: number; x1: number; y: number };
export type Block = { h: number; tx: number; fee: number; gap: number };
export type Summary = { label: string; n: number; mean: number; median: number; sd: number; cv_percent: number; min: number; max: number };

export type Overview = {
  dataset: Dataset; n_blocks: number; start: string; end: string; table: Summary[];
  median_fee: number; mean_fee: number; cv_percent: number; mean_gap: number; blocks_per_hour: number;
  hist_raw: Bin[]; hist_log: Bin[]; replay: Block[];
};
export type Exponential = {
  mean_gap: number; sd_over_mean: number; blocks_per_hour: number; ks_p: number; t_min: number;
  p_model: number; p_real: number; hist: Bin[]; curve: { x: number; y: number }[]; s_min: number;
  memoryless: { n: number; conditional: number } | null; out_of_order: number;
};
export type Poisson = {
  hours: number; lam: number; var_over_mean: number; chi2: number; dof: number; p_chi: number; cross_check: number;
  k: number; p_eq: number; p_ge: number; real_eq: number; real_ge: number; bars: { k: number; real: number; model: number }[];
};
export type Regression = {
  a: number; b: number; r: number; r2: number; se: number; lo_x: number; hi_x: number; median_x: number; x_min: number; x_max: number;
  tx: number; pred_log: number; pred_fee: number; range_low: number; range_high: number; in_range: boolean;
  points: [number, number][]; loglog_avg: number; loglog_total: number;
  quartiles: { range: string; bytes_per_tx: number; fee_per_tx: number }[];
};
export type Box = { q1: number; median: number; q3: number; lo: number; hi: number; outliers: number[] };
export type Anova = {
  F: number; p: number; df_between: number; df_within: number; p_kw: number; eta2: number; alpha: number; reject: boolean;
  tz: "utc" | "ist"; slots: { name: string; hours: string; blocks: number; mean_log: number; typical_fee: number; box: Box }[];
};
export type Confidence = {
  level: number; full: { n: number; mean: number; sd: number; t_critical: number; margin: number; lower: number; upper: number };
  true_mean: number; n: number; reps: number; seed: number; hits: number; intervals: { lower: number; upper: number; hit: boolean }[];
};

export const OFFLINE =
  "Can't reach the statistics server. Start it in the project folder with: python -m uvicorn api.main:app --port 8000";

export function useApi<T>(path: string | null, debounceMs = 140) {
  const [state, setState] = useState<{ data?: T; error?: string; loading: boolean }>({ loading: !!path });
  const [nonce, setNonce] = useState(0);
  const retry = useCallback(() => setNonce((n) => n + 1), []);

  useEffect(() => {
    if (!path) return;
    const ctrl = new AbortController();
    setState((s) => ({ ...s, loading: true, error: undefined }));
    const timer = window.setTimeout(async () => {
      try {
        const res = await fetch(path, { signal: ctrl.signal, headers: { Accept: "application/json" } });
        const body = await res.json().catch(() => null);
        if (!res.ok) {
          const detail = body?.detail;
          throw new Error(typeof detail === "string" ? detail : res.status >= 500 ? OFFLINE : "That input is out of range.");
        }
        if (body === null) throw new Error(OFFLINE);
        setState({ data: body as T, loading: false });
      } catch (e) {
        if ((e as Error).name === "AbortError") return;
        const msg = e instanceof TypeError ? OFFLINE : (e as Error).message;
        setState((s) => ({ ...s, loading: false, error: msg }));
      }
    }, debounceMs);
    return () => {
      ctrl.abort();
      window.clearTimeout(timer);
    };
  }, [path, nonce, debounceMs]);

  return { ...state, retry };
}

export const fmt = (v: number, d = 0) => v.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
export const pfmt = (p: number) => (p < 0.001 ? p.toExponential(2) : p.toFixed(3));
export function dur(sec: number) {
  const s = Math.abs(sec), m = Math.floor(s / 60), r = Math.floor(s % 60);
  return (sec < 0 ? "−" : "") + (m ? `${m}m ${String(r).padStart(2, "0")}s` : `${r}s`);
}
