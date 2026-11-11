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

- `x` = number of transactions in a block (`tx_count`). `y` = average fee per transaction (`avg_fee`).
- A busy block means many people want space. We expect a higher fee.
- Fees have huge spikes. So we fit **two models**: raw fee, and the **log of the fee**. The log model is the main one.
- All formulas are written by hand. We check the slope against `scipy.stats.linregress`.
- Reading the log model: one extra transaction multiplies the fee by `e^b`. For 1,000 extra transactions, the factor is `e^(1000 × b)`.

**Our result (fill after the real run; keys under `3_regression (Unit 4)` → `log_fee`):**

| Item | Value |
|---|---|
| Number of blocks | `n` = ____ |
| Slope `b` | `slope_b` = ____ |
| Intercept `a` | `intercept_a` = ____ |
| Correlation `r` | `correlation_r` = ____ |
| `R²` | `r_squared` = ____ |
| Standard error of estimate | `std_error_of_estimate` = ____ (in log units) |
| Slope p-value (scipy check) | `slope_p_value` = ____ |

Chart: `output/regression.png`.

## 6. Limits (say them in the viva)

- **Correlation is not cause.** Block fullness is a rough sign of demand. The real driver is how many users compete for space.
- A low `R²` is a valid result. It means `tx_count` explains only a part of the fee. Do not hide it.
- Fees of nearby blocks are linked. The least-squares error formulas assume independent errors.
- The line is for the range of our data. Do not predict far outside it.
- With the log model, `e^ŷ` predicts the typical (median-like) fee, not the arithmetic mean.

## 7. Viva questions and short answers

1. **Why least squares?** It makes the sum of the squared errors as small as possible. It has a simple closed formula.
2. **What does `R² = 0.24` mean?** The line explains 24% of the variation in the log fee. 76% comes from other causes.
3. **Why `n − 2` in the standard error?** We estimated two numbers (`a` and `b`) from the data. This costs two degrees of freedom.
4. **Why the log of the fee?** The fee is skewed with big spikes. The log makes the spread more even and the line fit better.
5. **Correlation versus regression?** Correlation says how strong the link is. Regression gives the line to predict.
6. **Can we predict the next block's fee?** Only roughly. The standard error shows the typical miss. We report it.
