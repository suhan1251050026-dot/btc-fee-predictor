---
name: plan-feature
description: Plan one feature or analysis module and save the plan to docs/plans. Use when starting any change that touches more than 2 files, or when the user says "plan".
---

# Plan a feature

1. Ask the user up to 3 questions about edge cases. Skip what the code already answers.
2. Read the files that the change will touch. Do not change anything.
3. Write the plan to `docs/plans/<feature>.md` with these headings:
   - Goal (one sentence)
   - Syllabus topic and formula
   - Files to create or change
   - Test cases with known answers
   - Risks and limits to state in the report
4. Stop. Ask the user to approve the plan before any code.
