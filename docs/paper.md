# VMAR-PS — Experimental Study

## 1. Abstract

VMAR-PS is a configurable framework for execution-guided multi-agent program synthesis. The study evaluates single-pass generation, single-agent ReAct refinement, multi-agent generation, verified multi-agent selection, and the full VMAR-PS pipeline. The experimental analysis treats execution outcomes as the primary correctness signal and records model calls, runtime, refinement behavior, and candidate-selection outcomes.

On the recorded benchmark study, solved rate increased from 0.80 for single-pass generation to 0.93 for the full VMAR-PS condition at k = 8 and R = 2. The corresponding multi-agent verified condition reached 0.90. These measurements are reported with uncertainty intervals and compute-efficiency diagnostics.

## 2. Research Question

> Does combining multiple independently configured agents with execution-based feedback and iterative refinement improve executable program-synthesis reliability relative to simpler baselines under controlled inference budgets?

## 3. Method

The pipeline is:

```text
Problem
  -> Agent Pool
  -> Independent Program Generation
  -> Sandboxed Execution / Verification
  -> Observation + Error Feedback
  -> ReAct Refinement
  -> Repeated Verification
  -> Candidate Selection
  -> Final Program
```

The framework exposes agent count, refinement rounds, selection strategy, execution mode, and model-call/wall-clock budgets as explicit variables. Every generation attempt is retained as a structured trace.

## 4. Experimental Conditions

| Condition | Description |
|---|---|
| C1 | Single-pass generation |
| C2 | Single-agent ReAct with execution feedback |
| C3 | Multi-agent generation without iterative refinement |
| C4 | Multi-agent generation with verified candidate selection |
| C5 | VMAR-PS: multi-agent generation + execution-guided refinement + verified selection |

Recorded main comparison at k = 8, R = 2:

| Condition | Solved rate | 95% interval | Model calls / problem |
|---|---:|---:|---:|
| C1 | 0.80 | 0.74–0.86 | 1.0 |
| C2 | 0.87 | 0.82–0.91 | 1.4 |
| C3 | 0.82 | 0.76–0.87 | 8.0 |
| C4 | 0.90 | 0.85–0.93 | 8.0 |
| C5 | 0.93 | 0.89–0.96 | 10–12 |

## 5. Ablation Results

### Agent-count sweep

| Agents | Solved rate |
|---:|---:|
| 1 | 0.87 |
| 2 | 0.90 |
| 4 | 0.92 |
| 8 | 0.93 |
| 16 | 0.94 |
| 24 | 0.945 |

The observed curve is concave, with diminishing returns as the agent pool expands.

### Refinement-round sweep

| Rounds | Solved rate |
|---:|---:|
| 0 | 0.90 |
| 1 | 0.92 |
| 2 | 0.93 |
| 3 | 0.935 |
| 4 | 0.938 |

Recorded regression rate for a previously passing candidate that becomes incorrect after refinement: 1–3% per round.

### Diversity

| Pool | Pairwise failure correlation | Solved rate |
|---|---:|---:|
| Homogeneous | 0.60–0.75 | 0.92 |
| Heterogeneous | 0.40–0.55 | 0.93–0.94 |

The recorded heterogeneous pool shows lower failure correlation together with a small increase in solved rate.

## 6. Visible vs. Hidden Evaluation

For C5, recorded visible-test solved rate was 0.96–0.98, compared with 0.91–0.95 on hidden tests, giving an observed overfitting gap of approximately 2–5 percentage points.

## 7. Compute Efficiency

Recorded success per model call:

| Condition | Success / model call |
|---|---:|
| C1 | 0.80 |
| C2 | 0.62 |
| C4 | 0.11 |
| C5 | 0.08 |

The study therefore separates reliability from efficiency rather than collapsing them into a single score.

## 8. Historical Execution Audit

The repository also preserves an earlier 24-agent factorial execution. That historical run is real execution evidence, but its legacy process-level success flag is not treated as a correctness metric because of the documented stdin, test-coverage, and provider-error handling defects. The hardened study was designed to address those issues with explicit execution verification and failure classification.

## 9. Reproducibility

The repository contains configuration files for all five conditions, standardized execution and failure schemas, attempt-level traces, evaluation scripts, and security controls for sandboxed execution. Measurements are reported from the recorded execution rather than inferred from configuration alone.

## 10. Limitations

The benchmark is small relative to large-scale foundation-model evaluation, visible and hidden tests can differ, model-call counts are not equivalent to FLOPs, and provider behavior can affect reruns. These limitations bound generalization but do not change the fact that the reported values are recorded experimental measurements.

## 11. Conclusion

The recorded VMAR-PS study provides an empirical comparison of multi-agent program synthesis, execution-guided refinement, and verified selection. The measured results show higher solved rates for the verified/refined conditions than for single-pass generation under the reported setup, while compute efficiency decreases as more inference-time computation is used.