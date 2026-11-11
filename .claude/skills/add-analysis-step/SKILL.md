---
name: add-analysis-step
description: Add one statistics module (exponential, Poisson, regression, ANOVA, or confidence interval) with its test. Use when the user asks to build or fix one of the 5 syllabus topics.
---

# Add an analysis step

1. Read `CLAUDE.md` and `.claude/rules/statistics.md`.
2. Write the test first in `tests/test_<module>.py`. Use a small array with a known answer.
3. Run the test. It must fail.
4. Write `src/<module>.py` with `run(df, out_dir)`. Write the formula by hand. Add a one-line analogy in the docstring.
5. Compare the result with `scipy`. They must agree within a small tolerance.
6. Save one chart and one CSV table in `output/`.
7. Run `python -m pytest tests -q` and `python -m ruff check .`.
8. Give the user a 3-line viva note: what the method does, the analogy, and one limit.
