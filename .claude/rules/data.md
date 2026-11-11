---
paths: ["src/collect.py", "data/**"]
---
# Data collection rules

- Use a public Bitcoin block API (mempool.space or Blockstream). Check the rate limit first.
- Send one request, then pause. Retry a failed request at most 3 times.
- Save consecutive blocks only. Check for gaps in `height`.
- Convert timestamps to UTC datetime. Keep the Unix time column too.
- `avg_fee = total_fee / tx_count`. Handle `tx_count == 0` (skip the row and log it).
- Never commit API keys. Read keys from environment variables.
- Target: 2,000 or more blocks. Record the first and last block date in `docs/data_notes.md`.
