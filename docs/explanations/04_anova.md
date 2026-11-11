# Topic 4: One-way ANOVA (Unit 4)

Code: `src/anova_slots.py`. Owner: Member C.

## 1. The idea (analogy)

You check the price of tea at 4 stalls. The prices are never exactly equal.
ANOVA asks one question: **is the difference between the stalls real, or only random wobble?**
It compares two things:
- the difference BETWEEN the group averages,
- the noise INSIDE each group.

If the stalls differ much more than the usual noise, we call the difference real.

## 2. The formulas

For `k` groups and `n` values in total:

- Grand mean `x̄`. Group means `x̄ᵢ`. Group sizes `nᵢ`.
- Between groups: `SSB = Σ nᵢ (x̄ᵢ − x̄)²`. Degrees of freedom `k − 1`.
- Within groups: `SSW = Σ Σ (x − x̄ᵢ)²`. Degrees of freedom `n − k`.
- Mean squares: `MSB = SSB / (k − 1)` and `MSW = SSW / (n − k)`.
- **`F = MSB / MSW`.** A large F means a real difference. The p-value comes from the F distribution.
- Null hypothesis `H0`: all group means are equal. Alternative `H1`: at least one mean is different.

## 3. Worked example (small numbers)

Three machines. Output: A = 4, 5, 6. B = 6, 7, 8. C = 8, 9, 10.
- Means: 5, 7, 9. Grand mean = 7.
- `SSB = 3×(5−7)² + 3×(7−7)² + 3×(9−7)² = 12 + 0 + 12 = 24`.
- `SSW = 2 + 2 + 2 = 6`.
- `df = 2` and `6`. `MSB = 12`. `MSW = 1`. **`F = 12`**, and the p-value is **0.008**.
- Decision: p is below 0.05. We reject `H0`. The machines are not all equal.

(Our test `test_anova_textbook_example` checks these exact numbers.)

## 4. Real-world use cases (not Bitcoin)

1. **Manufacturing:** compare the output of 3 machines or 3 production methods.
2. **Education:** compare the exam marks of students from 3 teaching methods.
3. **Agriculture:** compare the crop yield of 3 fertilisers.
4. **Medicine:** compare the effect of 3 doses of a drug.

## 5. How our project uses it

- Question: **does the fee depend on the time of day?**
- Groups: 4 UTC time slots. Night (00-05), morning (06-11), afternoon (12-17), evening (18-23).
  India time is UTC + 5:30. We name UTC in every chart.
- Data: the log of the average fee, because the raw fee is skewed.
- We compute `F` by hand and check it with `scipy.stats.f_oneway`.
- **Second check:** the Kruskal-Wallis test. It does not assume a bell-shaped (normal) data.
- **Why not many t-tests?** 4 groups give 6 pairs. Six tests at the 0.05 level give about a 26% chance of at least one false alarm (`1 − 0.95⁶`). ANOVA tests all groups in one step.

**Our result (fill after the real run; keys under `4_anova (Unit 4)`):**

| Item | Value |
|---|---|
| Blocks in each slot | `slot_counts` = ____ |
| Mean log fee in each slot | `slot_means_log_fee` = ____ |
| F, df | `F` = ____, `df_between` = ____, `df_within` = ____ |
| p-value | `p_value` = ____ |
| Kruskal-Wallis p-value | `kruskal_p_value` = ____ |
| Decision at the 0.05 level | ____ |

Chart: `output/anova_slots.png`.

## 6. Limits (say them in the viva)

- ANOVA assumes **independent** values, **near-normal** data inside each group, and **similar spread** in each group.
- Nearby blocks are linked. Busy periods follow busy periods. The independence assumption is not fully true.
- ANOVA says "at least one slot is different". It does not say which. A follow-up test (for example Tukey) would show this. It is outside our scope.
- With many blocks, a tiny difference can give a small p-value. Look at the size of the difference in the box plot, not only the p-value.
- Two weeks of data may include a special event. Name the dates.

## 7. Viva questions and short answers

1. **What is the null hypothesis?** All time slots have the same mean fee.
2. **What does a big F mean?** The difference between the slots is large compared with the noise inside the slots.
3. **Why not use a t-test?** A t-test compares 2 groups. For 4 groups, many t-tests raise the false-alarm chance. ANOVA tests all in one step.
4. **Why the log fee?** The fee is skewed. The log makes the groups closer to normal and the spread more equal.
5. **What if the assumptions fail?** We run Kruskal-Wallis as a second test. If both agree, we trust the result more.
6. **Does a small p-value prove that time causes the fee?** No. It shows that the means differ. Time of day is linked with user demand. That is the likely reason.
