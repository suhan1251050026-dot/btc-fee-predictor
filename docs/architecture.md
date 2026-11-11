# Architecture

```
collect.py ──► data/raw/blocks.csv ──► analyze.py ──► output/ (charts + tables)
                                          │
        ┌───────────────┬─────────────────┼─────────────────┬──────────────────┐
        ▼               ▼                 ▼                 ▼                  ▼
  exp_gaps.py   poisson_counts.py   regression.py    anova_slots.py   conf_interval.py
  (Unit 2)      (Unit 2)            (Unit 4)         (Unit 4)         (Unit 4)
```

- `src/collect.py`: downloads consecutive Bitcoin blocks and writes one CSV.
- `src/analyze.py`: loads the CSV, runs each module, and writes a summary.
- Each module has `run(df, out_dir)` and returns a dict of results.

## Project plan

| Step | Task | Done when |
|---|---|---|
| 1 | Collect 2,000+ blocks | CSV has no height gaps |
| 2 | Descriptive statistics, histogram, box plot | Charts in `output/` |
| 3 | Exponential model of block gaps | KS test result saved |
| 4 | Poisson model of blocks per hour | Chi-square result saved |
| 5 | Regression of fee on `tx_count` | R squared and standard error saved |
| 6 | ANOVA by UTC slot | F, p, and Kruskal-Wallis saved |
| 7 | 95% confidence interval | Interval saved |
| 8 | Report and pitch | Limits section written |

## Known limits (for the report)
- Fees in nearby blocks are linked. The tests assume independence.
- Fee data is skewed. Use the log fee and a second test.
- The period is short. Name the dates.
- Bitcoin uses UTC. India is UTC+5:30.
