# Data notes

- Source: mempool.space public API (`/api/blocks/tip/height` and `/api/v1/blocks/<height>`)
- Collected on: 11 November 2026, about 17:40 IST (12:10 UTC)
- First block time: 27 October 2026, 16:31:42 UTC
- Last block time: 11 November 2026, 12:05:19 UTC
- Period: about 15 days
- Number of blocks saved: 2,010 (the API sends 10 blocks per request, so the count is a little over 2,000)
- Height gaps: 0 (the blocks are consecutive)
- Blocks without fee data or with 0 transactions in the fee steps: 5 (2,005 blocks remain for the fee topics)
- Timestamps out of order by height: 61. The exponential step sorts the timestamps (see `docs/explanations/01_exponential.md`).
- Gaps of exactly 0 seconds after sorting: 2
- Fee unit: satoshi (1 BTC = 100,000,000 satoshi). `avg_fee` = total fee of the block / number of transactions.
- Special events in this period: None known
- Collection machine and connection: Windows Laptop, Home Wi-fi,Pune 