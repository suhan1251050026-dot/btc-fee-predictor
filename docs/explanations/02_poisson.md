# Topic 2: Poisson distribution (Unit 2)

Code: `src/poisson_counts.py`. Owner: Member A.

## 1. The idea (analogy)

Count the raindrops that hit your hand in exactly one hour.
Some hours have 4 drops. Some have 9. The average stays near a fixed number.
The Poisson distribution gives the chance of each count.
Waiting time between drops is exponential. The **count** of drops is Poisson. Same rain, two views.

## 2. The formulas

- `P(X = k) = e^(−λ) × λ^k / k!` for `k = 0, 1, 2, ...`
- Mean = `λ`. Variance = `λ`. So **variance / mean ≈ 1** is a quick check.
- `P(X ≥ k) = 1 − P(X ≤ k − 1)`.
- If the rate is `r` per unit time, the count in time `t` is Poisson with `λ = r × t`.

**Three conditions:** events are independent, the average rate is constant, and two events do not happen at the same instant.

## 3. Worked example (small numbers)

A call centre gets 6 calls per hour on average (`λ = 6`).
- `P(exactly 10 calls) = e^(−6) × 6^10 / 10! = 0.0413` (4.1%).
- `P(10 or more calls) = 0.0839` (8.4%). Staff must plan for this.

## 4. Real-world use cases (not Bitcoin)

1. **Call centres:** the number of calls in one hour. This sets the number of agents.
2. **Quality control:** the number of defects in 1 metre of cable.
3. **Road safety:** the number of accidents at a junction each day.
4. **Hospitals:** the number of patients who arrive at the emergency room each hour.

## 5. How our project uses it

- Data: the number of blocks found in each full clock hour (`hourly_counts`). The first and last hours are partial, so we drop them.
- We estimate `λ` = the mean count (about 6 blocks per hour for Bitcoin).
- We compute `P(10 or more blocks)` by hand and compare with the real share.
- **Chi-square goodness of fit:** we compare the observed and expected counts for each value.
  - Rule: each expected count must be 5 or more. We merge small bins (`merge_bins`).
  - Degrees of freedom = bins − 1 − 1. We lose one more degree because we estimated `λ` from the data.

**Our result (real data: 2,010 blocks, 27 Oct to 11 Nov 2026):**

| Item | Value |
|---|---|
| Number of full hours | 355 |
| Lambda (mean blocks per hour) | **5.64** |
| Variance | 5.45 |
| Variance / mean | **0.97** (near 1 supports the model) |
| P(10 or more blocks), model | **0.062** (6.1%) |
| P(10 or more blocks), real | **0.048** (4.8%) |
| Chi-square | 11.28, with **df = 9** (11 bins after merging) |
| Chi-square p-value | **0.257** |

**What we say:**
- The variance (5.45) is almost equal to the mean (5.64). This is the "fingerprint" of the Poisson distribution.
- The chi-square p-value is 0.257, above 0.05. We have no evidence against the Poisson model.
- The model says about 6% of hours have 10 or more blocks. The real share is about 5%. The model slightly over-predicts busy hours.
- The theoretical rate is 6 blocks per hour (one every 10 minutes). Our 5.64 is a little lower, because blocks came slightly slower in this period.
- **Cross-check with the exponential:** the mean gap is 637 s, and 3600 / 637 = 5.65. The two topics agree.

Chart: `output/poisson_counts.png`. The real bars and the Poisson bars have almost the same shape.

## 6. Limits (say them in the viva)

- If the hash rate changes during the day, the rate is not constant. The variance can be larger than the mean (overdispersion).
- We need enough hours of data. Two weeks gives about 336 hours. A short run gives few bins.
- The number of **transactions per block** is NOT a good Poisson example. The block size is capped, so the counts are not random enough. We do not use it.

## 7. Viva questions and short answers

1. **When do we use Poisson?** For the count of rare, independent events in a fixed time or space, with a constant average rate.
2. **What is special about the mean and variance?** They are equal. Both are `λ`.
3. **Why do we merge bins?** The chi-square test needs an expected count of 5 or more in each bin.
4. **Why is df = bins − 2?** One degree is lost for the total count. One more is lost because we estimated `λ`.
5. **How are Poisson and exponential linked?** Exponential gaps give Poisson counts. Both come from the same random process.
6. **What if the variance is much larger than the mean?** The events are clustered or the rate changes. Poisson is a poor fit. Our ratio is 0.97, so this did not happen.
7. **Why 11 bins and df = 9?** We merged the rare high counts so that each expected count is 5 or more. Then df = 11 − 1 − 1 = 9.
