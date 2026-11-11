# Topic 3: Regression and standard error of estimate (Unit 4)

Code: `src/regression.py`. Owner: Member B.

## 1. The idea (analogy)

A taxi fare grows with the distance. Plot distance on the x-axis and fare on the y-axis.
Draw the **best straight line** through the points. Use the line to predict the fare for a new distance.
The **standard error of estimate** is the typical miss of the prediction.
Think of darts: it is the average distance between the dart and the target.

## 2. The formulas (least squares)

For data `(x, y)` with `n` points:

- Slope: `b = Sxy / Sxx`, where `Sxy = Σ(x − x̄)(y − ȳ)` and `Sxx = Σ(x − x̄)²`.
- Intercept: `a = ȳ − b × x̄`. Line: `ŷ = a + b × x`.
- Correlation: `r = Sxy / √(Sxx × Syy)`. `R² = r²` is the share of the variation that the line explains.
- Standard error of estimate: `s_e = √( Σ(y − ŷ)² / (n − 2) )`.

## 3. Worked example (small numbers)

Data: `x = 1, 2, 3, 4, 5` and `y = 2, 4, 5, 4, 5`.
- `x̄ = 3`, `ȳ = 4`, `Sxx = 10`, `Sxy = 6`. So `b = 0.6` and `a = 4 − 0.6 × 3 = 2.2`.
- Line: `ŷ = 2.2 + 0.6x`. For `x = 6`, the prediction is `5.8`.
- Predictions: 2.8, 3.4, 4.0, 4.6, 5.2. Errors: −0.8, 0.6, 1.0, −0.6, −0.2.
- `SSE = 0.64 + 0.36 + 1.0 + 0.36 + 0.04 = 2.4`. So `s_e = √(2.4 / 3) = 0.894`.
- `r = 0.775` and `R² = 0.6`. The line explains 60% of the variation.

(Our test `test_regression_textbook_example` checks these exact numbers.)

## 4. Real-world use cases (not Bitcoin)

1. **Business:** predict monthly sales from the advertising budget.
2. **Real estate:** predict the house price from the area in square feet.
3. **Engineering:** calibrate a sensor. Predict the true temperature from the sensor voltage.
4. **Agriculture:** predict the crop yield from the amount of rain.

## 5. How our project uses it

- `x` = number of transactions in a block (`tx_count`). `y` = average fee per transaction (`avg_fee`, in satoshi).
- **Our first expectation:** a busy block means many people want space, so the fee goes UP.
- Fees have huge spikes. So we fit **two models**: raw fee, and the **log of the fee**. The log model is the main one.
- All formulas are written by hand. We check the slope against `scipy.stats.linregress`.
- Reading the log model: one extra transaction multiplies the fee by `e^b`. For 1,000 extra transactions, the factor is `e^(1000 × b)`.

**Our result (real data: 2,005 blocks with fee data, 27 Oct to 11 Nov 2026):**

| Item | Log-fee model (main) | Raw-fee model |
|---|---|---|
| Slope `b` | **−0.000501** | −0.194 satoshi per transaction |
| Intercept `a` | 8.048 | 1,488 satoshi |
| Correlation `r` | **−0.832** | −0.533 |
| `R²` | **0.692** | 0.284 |
| Standard error of estimate | **0.672** (log units) | 617 satoshi |
| Slope p-value | below 0.0001 | — |

**The surprise: the slope is NEGATIVE.** Blocks with more transactions have a LOWER fee per transaction.
For 1,000 extra transactions, the typical fee is multiplied by `e^(−0.501) = 0.61`. That is about 39% lower.
The log model explains 69% of the variation. The raw model explains only 28%, so the log was the right choice.

**Why is it negative? We tested two reasons with our data:**

1. **The ratio effect (built into the formula).**
   `avg_fee = total_fee / tx_count`. So `tx_count` is inside both `x` and `y`.
   In logs: `log(avg_fee) = log(total_fee) − log(tx_count)`.
   A log-log fit gives a slope of **−1.28**. Of this, **−1.00 comes only from the division**.
   The real link between the total fee and `tx_count` is only **−0.28** (r = −0.19).
   Analogy: share one pizza among more friends. Each slice gets smaller, even if the pizza is the same.

2. **Small transactions.** A block has a size limit. A block with many transactions holds many SMALL transactions.

| Blocks grouped by `tx_count` | Median bytes per transaction | Median fee per transaction |
|---|---|---|
| 30 to 2,708 | 829 | 871 satoshi |
| 2,709 to 3,605 | 521 | 876 satoshi |
| 3,606 to 5,743 | 392 | 409 satoshi |
| 5,744 to 11,360 | 238 | 82 satoshi |

   Small transactions pay small fees. So a high `tx_count` does NOT mean high demand. It means a mix of small, cheap transactions.

**Conclusion for the report:** `tx_count` is a poor measure of demand for block space.
The strong negative slope is mostly the ratio effect plus transaction size. It is not a law of "busy blocks are cheap".
This is a real finding. We report it openly. It shows that a high `R²` does not prove a cause.

Chart: `output/regression.png`. The log plot (right) shows a clear downward line.

## 6. Limits (say them in the viva)

- **Correlation is not cause.** Our `R²` is high (0.69), but most of the link comes from the ratio effect, not from demand.
- A better measure of price is the fee per byte (or per virtual byte). Our CSV has `size` in bytes, not virtual bytes. This is a possible extension.
- The 15 days of data show day-to-day changes. Some days have many cheap transactions. This adds to the negative link.
- Fees of nearby blocks are linked. The least-squares error formulas assume independent errors.
- The line is for the range of our data. Do not predict far outside it.
- With the log model, `e^ŷ` predicts the typical (median-like) fee, not the arithmetic mean.

## 7. Viva questions and short answers

1. **Why least squares?** It makes the sum of the squared errors as small as possible. It has a simple closed formula.
2. **What does `R² = 0.69` mean?** The line explains 69% of the variation in the log fee. 31% comes from other causes.
3. **Why `n − 2` in the standard error?** We estimated two numbers (`a` and `b`) from the data. This costs two degrees of freedom.
4. **Why the log of the fee?** The fee is skewed with big spikes. The log makes the spread more even and the line fit better.
5. **Correlation versus regression?** Correlation says how strong the link is. Regression gives the line to predict.
6. **Can we predict the next block's fee?** Only roughly. The standard error is 0.672 in log units. So a typical prediction is off by a factor of about e^0.672 = 2.
7. **You expected a positive slope. Why is it negative?** Mostly the ratio effect: `tx_count` divides the total fee. Also, many-transaction blocks hold small, cheap transactions.
8. **Is the regression wrong then?** No. The method is correct. The variable choice limits what it can tell us. Finding this is part of good statistics.
