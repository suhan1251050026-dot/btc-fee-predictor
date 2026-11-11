---
paths: ["src/**/*.py", "tests/**/*.py"]
---
# Statistics code rules

- Each topic module exposes one `run(df, out_dir)` function. It returns a dict of results.
- Compute the formula by hand first (mean, SD, Z, F, chi-square). Then compare with `scipy`.
- Exponential: rate = 1 / mean gap. Compare mean and SD. Run `scipy.stats.kstest`.
- Poisson: lambda = mean blocks per hour. Use chi-square goodness of fit. Merge bins with expected count below 5.
- Regression: report slope, intercept, correlation r, R squared, and standard error of estimate.
- ANOVA: 4 UTC slots (night 0-5, morning 6-11, afternoon 12-17, evening 18-23). Also run Kruskal-Wallis.
- Confidence interval: t-interval for the mean. Report the sample size.
- Every module saves one chart and one CSV table in `output/`.
- Tests use small fixed arrays with known answers. No network in tests.
