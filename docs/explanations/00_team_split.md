# Team split (4 members, 5 topics)

Project: Bitcoin Fee Predictor. Course: MM0501 Probability and Statistics.

| Member | Topic(s) | Syllabus unit | Code file | Sheet |
|---|---|---|---|---|
| A | Exponential distribution + Poisson distribution | Unit 2 | `src/exp_gaps.py`, `src/poisson_counts.py` | `01_exponential.md`, `02_poisson.md` |
| B | Regression and standard error of estimate | Unit 4 | `src/regression.py` | `03_regression.md` |
| C | One-way ANOVA | Unit 4 | `src/anova_slots.py` | `04_anova.md` |
| D | Confidence interval + descriptive statistics (data and charts) | Unit 4 + Unit 1 | `src/conf_interval.py`, `src/describe.py`, `src/collect.py` | `05_confidence_interval.md` |

Why Member A has two topics: Exponential and Poisson describe the same random process.
Gaps between events are exponential. Counts of events in a fixed time are Poisson. One story, two views.
Member D has the lighter statistics topic. Member D also owns data collection and the descriptive charts.

**Ask your teacher:** "Is the 20-mark explanation for each topic, or for each student?"
If the marks are for each student, Member A can pick one of the two topics and Member D can take the other.

## Every member must be able to say

1. The idea in one analogy.
2. The formula, and what each symbol means.
3. Two real-world use cases that are NOT Bitcoin.
4. How our project uses it, and our result.
5. One limit of the method.

## Suggested 20-mark plan for each topic (check your rubric)

| Part | Marks |
|---|---|
| Concept, assumptions, and formula | 6 |
| Analogy and real-world use cases | 5 |
| Our project: method, chart, and result | 6 |
| Limits and viva answers | 3 |

## Project workflow (all members)

1. Member D runs `python -m src.collect --count 2000` on a PC. This sends requests to a public API.
2. Anyone runs `python -m src.analyze`. The result goes to `output/`.
3. Each member fills the "Our result" box in the own sheet from `output/summary.json`.
4. The team writes one report. Each member writes the own section.

## Practice before the real data

`python -m src.synth` makes FAKE data with a known truth. `python -m src.analyze --csv data/raw/blocks_synthetic.csv --out output/synthetic` runs on it.
Use it to practise. **Never put synthetic results in the report.**
