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

- Data: gaps between block timestamps, in seconds (`block_gaps`). We sort the timestamps first (see Limits).
- We compute `λ = 1 / mean gap` and `P(gap > 20 min)` by hand.
- We compare with the real share of long gaps.
- We run the Kolmogorov-Smirnov test (`scipy.stats.kstest`) as a formal check.

**Our result (real data: 2,010 blocks, 27 Oct to 11 Nov 2026):**

| Item | Value |
|---|---|
| Number of gaps | 2,009 |
| Mean gap | **637 s** (10.6 min) |
| SD of gaps | 650 s |
| SD / mean | **1.02** (near 1 supports the model) |
| Rate `λ` | 0.00157 per second (5.65 per hour) |
| P(wait > 20 min), model | **0.152** (15.2%) |
| P(wait > 20 min), real | **0.148** (14.8%) |
| KS test p-value | **0.449** |

**What we say:**
- The SD is almost equal to the mean. This is the "fingerprint" of the exponential distribution.
- The model predicts 15.2% of waits longer than 20 minutes. The real share is 14.8%. They are very close.
- The KS p-value is 0.449, far above 0.05. We have no evidence against the exponential model.
- The mean gap is 637 s, slightly above the 600 s target. The difficulty adjusts only every 2,016 blocks, so the real mean can drift a little from the target.
- **Cross-check with Poisson:** 3600 / 637 = 5.65 blocks per hour. The Poisson step found λ = 5.64. The two topics agree.

Chart: `output/exp_gaps.png`. The red exponential curve follows the bars closely.

## 6. Limits (say them in the viva)

- Miners set the timestamps. In our data, 61 blocks have a time earlier than the block before them.
  Our first version dropped these negative gaps. This kept their too-long neighbours and gave a wrong mean of 661 s.
  We found the error because the Poisson step gave 5.64 blocks per hour (3600 / 5.64 = 638 s).
  The fix: sort the timestamps first. Now the mean gap is 637 s, and both topics agree. This is a good viva story.
- The network hash rate changes. So the true rate `λ` is not exactly constant.
- The difficulty adjusts every 2,016 blocks. This can change the mean gap between periods.
- The KS test is not exact when we estimate the mean from the same data. Treat the p-value as a guide.

## 7. Viva questions and short answers

1. **What does memoryless mean?** The past wait does not change the chance of the next wait. A drop is never "due".
2. **Why is the SD equal to the mean?** For the exponential, both are `1/λ`. We use SD / mean ≈ 1 as a quick check.
3. **Why is block time exponential?** Mining is a lottery with no memory. Each try has the same tiny chance.
4. **Why not Ethereum?** Ethereum has a fixed 12-second slot. The gaps are almost constant, not random.
5. **Link to Poisson?** The gaps are exponential. The count of blocks in one hour is Poisson. Same process, two views.
6. **What does a small KS p-value say?** The data does not follow the exponential model well. Our p-value is 0.449, so the fit is good.
7. **Why did you sort the timestamps?** Some miner clocks are wrong. Dropping negative gaps biased the mean up to 661 s. Sorting gives the correct mean of 637 s. It agrees with the Poisson result.
