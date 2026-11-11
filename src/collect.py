"""Download consecutive Bitcoin blocks from the public mempool.space API. Save one CSV.

Run on your own PC (not in a sandbox with a blocked network):
    python -m src.collect --count 2000

Columns: height, timestamp, tx_count, size, total_fee, avg_fee
- total_fee is in satoshi. avg_fee = total_fee / tx_count.
- The API returns 10 blocks per request. A pause between requests keeps us under the rate limit.
"""

import argparse
import sys
import time
from pathlib import Path

import pandas as pd
import requests

BASE = "https://mempool.space/api"
HEADERS = {"User-Agent": "mm0501-course-project (student statistics study)"}


def get_json(url, tries=3, pause=2.0):
    """GET a URL and return JSON. Retry up to 3 times."""
    last = None
    for attempt in range(1, tries + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError) as exc:
            last = exc
            print(f"  retry {attempt}/{tries} after error: {exc}")
            time.sleep(pause * attempt)
    raise RuntimeError(f"Request failed after {tries} tries: {url}") from last


def parse_block(b):
    """Turn one API block object into one CSV row. Return None if the block has no fee data."""
    extras = b.get("extras") or {}
    total_fee = extras.get("totalFees")
    tx_count = b.get("tx_count")
    if total_fee is None or not tx_count:
        return None
    return {
        "height": b["height"],
        "timestamp": b["timestamp"],
        "tx_count": tx_count,
        "size": b.get("size"),
        "total_fee": total_fee,
        "avg_fee": total_fee / tx_count,
    }


def collect(count, pause):
    tip = int(get_json(f"{BASE}/blocks/tip/height"))
    print(f"Chain tip: block {tip}")
    rows, start = {}, tip
    while len(rows) < count and start > 0:
        batch = get_json(f"{BASE}/v1/blocks/{start}")
        if not batch:
            break
        for b in batch:
            row = parse_block(b)
            if row:
                rows[row["height"]] = row
        start = min(b["height"] for b in batch) - 1
        print(f"  {len(rows)}/{count} blocks")
        time.sleep(pause)
    return pd.DataFrame(sorted(rows.values(), key=lambda r: r["height"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=2000)
    ap.add_argument("--pause", type=float, default=1.0, help="seconds between requests")
    ap.add_argument("--out", default="data/raw/blocks.csv")
    args = ap.parse_args()

    df = collect(args.count, args.pause)
    if df.empty:
        sys.exit("No blocks collected.")
    gaps = int((df["height"].diff().dropna() != 1).sum())
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    first = pd.to_datetime(df["timestamp"].iloc[0], unit="s", utc=True)
    last = pd.to_datetime(df["timestamp"].iloc[-1], unit="s", utc=True)
    print(f"Saved {len(df)} blocks to {args.out}")
    print(f"Period (UTC): {first} to {last}")
    print(f"Height gaps (must be 0): {gaps}")
    print("Write the period and the source in docs/data_notes.md for your report.")


if __name__ == "__main__":
    main()
