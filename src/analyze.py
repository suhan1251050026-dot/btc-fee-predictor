"""Run the whole analysis: descriptive step plus the 5 syllabus topics.

python -m src.analyze                       (uses data/raw/blocks.csv)
python -m src.analyze --csv data/raw/blocks_synthetic.csv --out output/synthetic
"""

import argparse
import json

from src import (
    anova_slots,
    conf_interval,
    describe,
    exp_gaps,
    poisson_counts,
    regression,
)
from src.common import ensure_dir, load_blocks

STEPS = [
    ("0_descriptive (Unit 1)", describe),
    ("1_exponential (Unit 2)", exp_gaps),
    ("2_poisson (Unit 2)", poisson_counts),
    ("3_regression (Unit 4)", regression),
    ("4_anova (Unit 4)", anova_slots),
    ("5_confidence_interval (Unit 4)", conf_interval),
]


def run_all(csv_path, out_dir):
    df = load_blocks(csv_path)
    out = ensure_dir(out_dir)
    summary = {"n_blocks": len(df), "csv": str(csv_path)}
    for name, module in STEPS:
        summary[name] = module.run(df, out)
    with open(out / "summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=float)
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/raw/blocks.csv")
    ap.add_argument("--out", default="output")
    args = ap.parse_args()
    summary = run_all(args.csv, args.out)

    e = summary["1_exponential (Unit 2)"]
    p = summary["2_poisson (Unit 2)"]
    r = summary["3_regression (Unit 4)"]["log_fee"]
    a = summary["4_anova (Unit 4)"]
    c = summary["5_confidence_interval (Unit 4)"]["raw_fee"]
    print(f"Blocks: {summary['n_blocks']}")
    print(
        f"[Exponential] mean gap {e['mean_gap_s']:.0f} s, SD/mean {e['sd_over_mean']:.2f}, KS p = {e['ks_p_value']:.3f}"
    )
    print(
        f"[Exponential] P(wait > 20 min): model {e['p_wait_over_20min_model']:.4f}, real {e['p_wait_over_20min_real']:.4f}"
    )
    print(
        f"[Poisson] lambda {p['lambda_blocks_per_hour']:.2f} blocks/hour, var/mean {p['dispersion_var_over_mean']:.2f}, chi2 p = {p['chi2_p_value']:.3f}"
    )
    print(
        f"[Poisson] P(>= 10 blocks): model {p['p_10_or_more_model']:.4f}, real {p['p_10_or_more_real']:.4f}"
    )
    print(
        f"[Regression, log fee] slope {r['slope_b']:.6f}, r {r['correlation_r']:.3f}, R2 {r['r_squared']:.3f}, SE {r['std_error_of_estimate']:.3f}"
    )
    print(
        f"[ANOVA] F = {a['F']:.2f}, p = {a['p_value']:.4g}; Kruskal-Wallis p = {a['kruskal_p_value']:.4g}"
    )
    print(
        f"[Confidence interval] mean fee {c['mean']:.1f}, 95% CI ({c['lower']:.1f}, {c['upper']:.1f})"
    )
    print(f"Charts and tables are in {args.out}/")


if __name__ == "__main__":
    main()
