---
name: commit
description: Run checks and write a conventional commit from the diff. Use when the user asks to commit.
disable-model-invocation: true
---

# Commit

1. Run `python -m ruff check .` and `python -m pytest tests -q`. Stop if either fails.
2. Run `git diff --stat` and `git status`.
3. Write one conventional commit message (`feat:`, `fix:`, `docs:`, `test:`, `chore:`). One logical change only.
4. Run `git add` for the changed files and `git commit`.
5. Do NOT run `git push`. Tell the user: "Push needs your confirmation. It sends code to GitHub."
