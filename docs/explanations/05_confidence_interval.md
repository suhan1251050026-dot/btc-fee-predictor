# Topic 5: Confidence interval for the mean (Unit 4)

Code: `src/conf_interval.py` (and `src/describe.py` for the Unit 1 step). Owner: Member D.

## 1. The idea (analogy)

You cannot see the true average fee. You only have a sample of blocks.
So you throw a **net** over the true value. The net is the confidence interval.
A 95% net catches the true value in 95 out of 100 repeated studies.
A wider net is safer but less exact. A narrower net is exact but can miss.

## 2. The formulas

- Sample mean `x̄` and sample standard deviation `s` (divide by `n − 1`).
- Standard error of the mean: `SE = s / √n`.
- 95% interval: `x̄ ± t × SE`. The value `t` comes from the t distribution with `n − 1` degrees of freedom.
- The margin is `t × SE`. For a large `n`, `t` is close to 1.96.
- To halve the width, you need four times as many data points.

## 3. Worked example (small numbers)

A sample of `n = 25` has mean 50 and standard deviation 10.
- `SE = 10 / √25 = 2`. The t value for 24 degrees of freedom is `2.064`.
- Margin = `2.064 × 2 = 4.128`.
- 95% interval = `(45.87, 54.13)`.
- Say: "We are 95% confident that the true mean is between 45.87 and 54.13."

(Our test `test_ci_known_example` checks these exact numbers.)

**Wrong sentence:** "There is a 95% chance that the true mean is in this interval." The true mean is fixed. The interval is the random part.

## 4. Real-world use cases (not Bitcoin)

1. **Opinion polls:** "42% ± 3%" is a confidence interval for the share of voters.
2. **Quality control:** a factory estimates the mean weight of a packet from 50 samples.
3. **Medicine:** a trial reports the mean drop in blood pressure with a 95% interval.
4. **Software testing:** estimate the mean response time of a server from sample requests.

## 5. How our project uses it

- Data: the `avg_fee` column for all blocks.
- We compute the interval by hand and check it against `scipy.stats.t.interval`.
- Fees are skewed. Two views:
  1. The 95% interval for the **mean fee** (raw).
  2. The interval for the **mean log fee**, then converted back with `e^x`. This gives the **geometric mean**. It is NOT the arithmetic mean. We label it clearly.
- **Link to the CLT (central limit theorem):** the sample mean is close to normal for a large sample, even if the data is skewed. With about 2,000 blocks, the interval is reliable.
- **Unit 1 step (`src/describe.py`):** mean, median, SD, and coefficient of variation (CV = SD / mean × 100), plus a histogram and a box plot. The mean is larger than the median for skewed data. This is why we use the log.

**Unit 1 result (descriptive statistics, real data, 2,005 blocks):**

| Variable | Mean | Median | SD | CV | Min | Max |
|---|---|---|---|---|---|---|
| Transactions per block | 4,101 | 3,605 | 2,008 | 49% | 30 | 11,360 |
| Block size (bytes) | 1,703,046 | 1,644,487 | 417,163 | 24% | 14,632 | 3,972,779 |
| Average fee (satoshi) | **694** | **584** | 729 | **105%** | 13 | 16,678 |

- The fee mean (694) is above the median (584). The maximum (16,678) is 24 times the mean. The fee is **right-skewed**.
- The CV of the fee is 105%. The SD is larger than the mean. The fee varies a lot.
- This is why the other topics use the log of the fee.

**Confidence interval result:**

| Item | Raw fee | Log fee (back to satoshi) |
|---|---|---|
| Sample size `n` | 2,005 | 2,005 |
| Mean | **694.1 satoshi** | 5.992 (geometric mean **400 satoshi**) |
| SD | 729.2 | 1.210 |
| Standard error `s / √n` | 16.29 | 0.0270 |
| t critical (df = 2,004) | 1.961 | 1.961 |
| Margin | 31.94 | 0.0530 |
| **95% interval** | **662.2 to 726.1 satoshi** | **380 to 422 satoshi** (geometric mean) |

**What we say:**
- "We are 95% confident that the true mean fee per transaction in this period is between 662 and 726 satoshi."
- The t value (1.961) is almost equal to z (1.96), because `n` is large.
- The geometric mean (400) is much lower than the arithmetic mean (694). A few very expensive blocks pull the arithmetic mean up.
- The interval is narrow (±32 satoshi, about ±4.6%) because the sample is large. By the CLT, the sample mean is close to normal, even though the fee data is skewed.

Charts: `output/confidence_interval.png`, `output/hist_fee.png`, `output/box_fee.png`. Table: `output/descriptive.csv`.

## 6. Limits (say them in the viva)

- The formula assumes independent values. Fees of nearby blocks are linked. So the true interval is **wider** than ours.
- The mean of skewed data is pulled by big spikes. The median or the geometric mean can describe a "typical" fee better.
- The interval covers the **period of our data** only. It does not cover fees next year.
- The interval is about the mean fee of blocks, not about the fee of one future transaction.

## 7. Viva questions and short answers

1. **What does 95% mean?** If we repeat the study many times, about 95 of 100 intervals contain the true mean.
2. **Why t and not z?** We estimate the standard deviation from the sample. The t distribution adds a small safety margin for this. For a large `n`, t and z are almost equal.
3. **What makes the interval narrower?** A larger sample, a smaller spread, or a lower confidence level.
4. **Why does the CLT matter?** It lets us use the interval for the mean even when the fee data is skewed, if the sample is large.
5. **Mean fee or geometric mean?** The mean is pulled by spikes. The geometric mean of the fee is closer to a typical block. We report both and label them.
6. **What is the CV?** SD divided by the mean, in percent. It compares spread across data with different units or sizes.
