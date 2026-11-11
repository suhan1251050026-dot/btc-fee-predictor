# Topic 1: Exponential distribution (Unit 2)

Code: `src/exp_gaps.py`. Owner: Member A.

## 1. The idea (analogy)

You hold out your hand and wait for the first raindrop. The rain has **no memory**.
If you already waited 5 minutes, the next drop is not "due". The wait starts fresh every moment.
The exponential distribution models this kind of waiting time.

## 2. The formulas

- Rate: `λ` (events per unit time). Mean waiting time = `1/λ`.
- Probability of waiting longer than `t`: `P(X > t) = e^(−λt)`.
- Probability of waiting at most `t`: `P(X ≤ t) = 1 − e^(−λt)`.
- Mean = `1/λ`. Standard deviation = `1/λ`. So **SD / mean ≈ 1** is a quick check.
- Memoryless: `P(X > s + t | X > s) = P(X > t)`.

## 3. Worked example (small numbers)

A bus arrives on average every 10 minutes. Then `λ = 0.1` per minute.
- `P(wait > 20 min) = e^(−0.1 × 20) = e^(−2) = 0.1353` (13.5%).
- `P(wait ≤ 5 min) = 1 − e^(−0.5) = 0.3935` (39.4%).

## 4. Real-world use cases (not Bitcoin)

1. **Reliability engineering:** the time until a machine part fails. This sets the maintenance plan.
2. **Customer service:** the time between two customers who arrive at a bank counter. This sets the staff plan.
3. **Networks:** the time between two data packets that arrive at a router.
4. **Physics:** the time until a radioactive atom decays.

## 5. How our project uses it

Bitcoin miners run a lottery. Each try has a tiny, equal chance to win. The lottery has no memory.
So the time between two blocks is close to exponential. The network keeps the mean near 10 minutes (600 s).

- Data: gaps between block timestamps, in seconds (`block_gaps`).
- We compute `λ = 1 / mean gap` and `P(gap > 20 min)` by hand.
- We compare with the real share of long gaps.
- We run the Kolmogorov-Smirnov test (`scipy.stats.kstest`) as a formal check.

**Our result (fill after the real run; keys in `output/summary.json` under `1_exponential (Unit 2)`):**

| Item | Value |
|---|---|
| Number of gaps | `n_gaps` = ____ |
| Mean gap (s) | `mean_gap_s` = ____ |
| SD / mean | `sd_over_mean` = ____ (near 1 supports the model) |
| P(wait > 20 min), model | `p_wait_over_20min_model` = ____ |
| P(wait > 20 min), real | `p_wait_over_20min_real` = ____ |
| KS test p-value | `ks_p_value` = ____ (below 0.05 means a poor fit) |

Chart: `output/exp_gaps.png`. Read the result honestly. A poor fit is a valid finding.

## 6. Limits (say them in the viva)

- Miners set the timestamps. They can be a little wrong or out of order. We drop gaps of 0 or less and report how many.
- The network hash rate changes. So the true rate `λ` is not exactly constant.
- The difficulty adjusts every 2,016 blocks. This can change the mean gap between periods.
- The KS test is not exact when we estimate the mean from the same data. Treat the p-value as a guide.

## 7. Viva questions and short answers

1. **What does memoryless mean?** The past wait does not change the chance of the next wait. A drop is never "due".
2. **Why is the SD equal to the mean?** For the exponential, both are `1/λ`. We use SD / mean ≈ 1 as a quick check.
3. **Why is block time exponential?** Mining is a lottery with no memory. Each try has the same tiny chance.
4. **Why not Ethereum?** Ethereum has a fixed 12-second slot. The gaps are almost constant, not random.
5. **Link to Poisson?** The gaps are exponential. The count of blocks in one hour is Poisson. Same process, two views.
6. **What does a small KS p-value say?** The data does not follow the exponential model well. We report it and explain why.
