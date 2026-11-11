"""Shared helpers: load the block CSV and prepare columns.

Analogy: this is the kitchen prep. All topic modules get the same clean ingredients.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # save charts to files. No window needed.

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = ["height", "timestamp", "tx_count", "size", "total_fee", "avg_fee"]
SLOTS = {
    "night (00-05 UTC)": range(6),
    "morning (06-11 UTC)": range(6, 12),
    "afternoon (12-17 UTC)": range(12, 18),
    "evening (18-23 UTC)": range(18, 24),
}


def load_blocks(csv_path):
    """Read the CSV. Sort by block height. Check the columns."""
    df = pd.read_csv(csv_path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"CSV is missing columns: {missing}")
    df = df.sort_values("height").reset_index(drop=True)
    df["time_utc"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
    df["hour_utc"] = df["time_utc"].dt.hour
    return df


def fee_rows(df):
    """Rows with a positive fee. The log of zero is not defined."""
    return df[(df["avg_fee"] > 0) & (df["tx_count"] > 0)].copy()


def slot_of_hour(hour):
    """Return the time-slot name for an hour (0-23)."""
    for name, hours in SLOTS.items():
        if hour in hours:
            return name
    raise ValueError(f"hour out of range: {hour}")


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)
    return Path(path)


def sample_sd(values):
    """Sample standard deviation (divide by n - 1), written by hand."""
    x = np.asarray(values, dtype=float)
    return float(np.sqrt(np.sum((x - x.mean()) ** 2) / (len(x) - 1)))
