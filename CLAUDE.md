# Project: BTC Fee Predictor
Course project for MM0501 Probability and Statistics (VIT Pune). It uses about 2,000 real Bitcoin blocks.
It tests block waiting time, blocks per hour, fee regression, fee by time of day, and the mean fee.
User: one student. Viva defence is required. Stack: Python 3, pip, pandas, numpy, scipy, matplotlib.
Runs on Windows (PowerShell) in VS Code. Code must be simple and explainable.

## Commands
- Install: `pip install -r requirements.txt`
- Collect data: `python -m src.collect --count 2000` (needs internet; run on the PC)
- Fake data for practice: `python -m src.synth` (never use it in the report)
- Run all analysis: `python -m src.analyze` (or `--csv <file> --out <dir>`)
- Test one file: `python -m pytest tests/test_<name>.py -q`
- Test all: `python -m pytest tests -q`
- Lint + format check before every commit: `python -m ruff check . ; python -m ruff format --check .`

## The 5 syllabus topics (each is one module in `src/`; `src/describe.py` is the Unit 1 step)
Viva sheets for each topic: `docs/explanations/`. Team split: `docs/explanations/00_team_split.md`.
1. Exponential: gaps between block timestamps (`src/exp_gaps.py`)
2. Poisson: blocks per hour (`src/poisson_counts.py`)
3. Regression + standard error of estimate: `avg_fee` vs `tx_count` (`src/regression.py`)
4. One-way ANOVA: fee by UTC time slot, plus Kruskal-Wallis check (`src/anova_slots.py`)
5. 95% confidence interval for the mean fee (`src/conf_interval.py`)

## Conventions
- Write each statistics formula in plain code. Use `scipy` only to check the result.
- One function = one idea. Add a docstring with an analogy in one line.
- Data lives in `data/raw/blocks.csv`. Columns: `height, timestamp, tx_count, size, total_fee, avg_fee`.
- All time values are UTC. Name the time zone in every plot title.
- Charts and tables go to `output/`. Never write results into `src/`.
- IMPORTANT: never edit files in `data/raw/`. Re-run `python -m src.collect` to regenerate.
- Use `numpy.random.default_rng(42)` for any random step.

## Workflow
- Plan first for any change that touches more than 2 files. Save it in `docs/plans/<name>.md`.
- Write a test before you fix a bug.
- Conventional commits. One logical change per commit.
- Report every result, even a poor fit. Do not hide a low R squared.

## Gotchas
- Public block APIs have rate limits. Use a pause between requests and cache to CSV.
- Fee data is skewed. Use the log fee for regression and ANOVA. Run Kruskal-Wallis as a second check.
- Nearby blocks are not fully independent. Write this limit in the report.
- `git push` always needs the user to confirm. Say "this pushes to GitHub" before the command.
- Do not use "transactions per block" as a Poisson example. Block size is capped.

## More context
- Architecture: @docs/architecture.md
