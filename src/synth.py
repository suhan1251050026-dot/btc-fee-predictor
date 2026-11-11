"""Make SYNTHETIC (fake) block data to test the code before you collect real data.

    python -m src.synth

The output is NOT real Bitcoin data. Never put synthetic results in the report.
Known truth built into the fake data (the analysis should find it):
- gaps are exponential with mean 600 s
- fee goes up with the number of transactions
- the evening slot has a higher fee than the other slots
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def make_blocks(n=2000, seed=42):
    rng = np.random.default_rng(seed)
    gaps = rng.exponential(600, size=n)
    start = 1_760_000_000  # a fixed Unix time
    timestamps = (start + np.cumsum(gaps)).astype(np.int64)
    tx_count = np.clip(rng.normal(2500, 700, size=n), 200, 6000).astype(int)
    hour = (timestamps // 3600) % 24
    evening_boost = np.where((hour >= 18) & (hour < 24), 0.35, 0.0)
    log_fee = 2.0 + 0.0004 * tx_count + evening_boost + rng.normal(0, 0.5, size=n)
    avg_fee = np.exp(log_fee)
    return pd.DataFrame(
        {
            "height": np.arange(900_000, 900_000 + n),
            "timestamp": timestamps,
            "tx_count": tx_count,
            "size": (tx_count * 450).astype(int),
            "total_fee": (avg_fee * tx_count).round().astype(int),
            "avg_fee": avg_fee,
        }
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--out", default="data/raw/blocks_synthetic.csv")
    args = ap.parse_args()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    make_blocks(args.n).to_csv(args.out, index=False)
    print(f"Wrote SYNTHETIC data to {args.out}. Do not use it in the report.")


if __name__ == "__main__":
    main()
