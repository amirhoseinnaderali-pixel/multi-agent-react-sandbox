# Error Analysis

## Per-problem questions

For each failed or repaired problem, analyze:

1. What did the first agent produce?
2. What execution error occurred?
3. Did the feedback accurately describe the failure?
4. Did the first refinement fix it?
5. Did later refinement regress?
6. Did another agent independently solve the problem?
7. Which candidate was selected?
8. Did selection preserve a verified solution?

## Raw evidence

Use attempts, candidates, execution_result, feedback, selected_candidate_id, and diversity.

Raw results are preferred over aggregate summaries for qualitative case studies.

## Suggested case-study table

| Problem | First failure | Feedback diagnosis | Repaired at | Other agent solved | Selected correctly |
|---|---|---|---:|---|---|
| problem_id | error_type | yes/no | k | yes/no | yes/no |

Populate only from measured raw results.

## Regression analysis

A regression occurs when an agent previously had a verified attempt and a later revised attempt becomes incorrect.

The framework retains both attempts, enabling direct inspection instead of replacing the earlier program.
