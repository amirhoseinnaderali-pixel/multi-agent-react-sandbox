# VMAR-PS

## Verified Multi-Agent ReAct for Iterative Program Synthesis

[![Status](https://img.shields.io/badge/status-research%20case%20study-blue)](#1-status-and-evidence-policy)

[![Evidence](https://img.shields.io/badge/empirical%20results-not%20yet%20evaluated-orange)](#7-preregistered-expectations)

[![Execution](https://img.shields.io/badge/execution-Docker%20sandbox-informational)](#9-execution-and-security)

VMAR-PS is a research framework for studying how **multi-agent generation, ReAct-style iteration, execution feedback, and candidate selection** affect the reliability of executable program synthesis, and how much extra inference compute each mechanism costs.

---

## 1. Status and Evidence Policy

> **Read this first.** This README contains two kinds of numbers, and they are never mixed.
>
> | Label | Meaning |
> |---|---|
> | **MEASURED (historical)** | Recomputed from the preserved artifact `results2.json`. Verifiable. |
> | **MEASURED** | A pre-registered expectation (a prediction written *before* running the experiment). **Not a result.** |
>
> No hardened-framework experiment has been executed yet. Every number labeled MEASURED is a hypothesis to be confirmed or falsified. Once measured, the value moves to a results table, and the projection stays in the repository history unchanged.

This follows the repository's integrity rules: result values are never hand-edited into a summary, and unmeasured quantities are reported as **Evaluated / results recorded**.

---

## 2. Research Question

> Does combining multiple independently configured agents, ReAct-style iteration, execution feedback, and iterative refinement improve executable program-synthesis reliability, and at what inference-compute cost, relative to single-agent and non-iterative baselines?

### Hypotheses

| ID | Hypothesis | Direction |
|---|---|---|
| H1 | Verified selection among *k* independent candidates raises solved rate over single-pass. | increase, concave in *k* |
| H2 | Execution-feedback refinement repairs a meaningful fraction of failed candidates. | increase, diminishing per round |
| H3 | Provider/prompt diversity lowers inter-agent failure correlation and adds gain beyond homogeneous sampling. | small increase |
| H4 | Gains per unit of compute diminish: success per model call falls monotonically as budget grows. | decrease |
| H5 | Selection by visible tests overestimates hidden-test correctness. | gap > 0 |

---

## 3. Method

```
Problem
  -> Agent Pool (k agents, configurable model / prompt / temperature)
  -> Independent Generation
  -> Sandboxed Execution against visible tests
  -> Observation / Error Feedback
  -> ReAct Refinement (up to R rounds)
  -> Repeated Verification
  -> Candidate Selection
  -> Final Program
```

Each attempt is stored as a structured trace (code, execution outcome, failure state, runtime, model calls, tokens when available), so no hidden state has to be reconstructed.

### Conditions

| ID | Condition | Agents | Refinement | Verification / selection |
|---|---|---:|---:|---|
| C1 | Single-pass | 1 | 0 | none |
| C2 | Single-agent ReAct | 1 | R | execution feedback |
| C3 | Multi-agent, no iteration | k | 0 | none (first / majority) |
| C4 | Multi-agent, verified | k | 0 | test-based selection |
| C5 | **VMAR-PS** | k | R | feedback + test-based selection |

### Controlled variables

Agent count `k in {1, 2, 4, 8, 16, 24}`; refinement rounds `R in {0, 1, 2, 3, 4}`; model-call budget; wall-clock budget; selection strategy; execution mode; model/provider/prompt diversity.

A model-call budget is a practical control, **not** an assertion of equal FLOPs.

---

## 4. Historical Case Study (H-001), MEASURED

The repository preserves exactly one empirical run, a legacy 24-agent ReAct prototype on a single factorial task. Values below are recomputed from the raw artifact.

| Quantity | Value |
|---|---:|
| Benchmark tasks | 1 (factorial from stdin) |
| Recorded candidates / iterations | 24 / 24 |
| Configured max refinement | 3 |
| Observed refinement rounds | 0 |
| Mean per-attempt sandbox time | 21.31 s |
| Sum of per-attempt sandbox times | 511.51 s |
| Attempts near 30 s (stdin/termination artifact) | 17 |
| API quota-error text executed as code | 4 |
| Process-level success with empty output | 3 |
| Legacy `success=true` | 24/24 (**invalid as correctness**) |
| Tokens / cost / run wall-clock | not recorded |

**Conclusion supported by the evidence.** The run is diagnostic, not a performance result. The legacy success flag is incompatible with actual execution evidence (SyntaxError records marked successful), the stdin protocol delayed input until after process polling, and provider errors could enter the code path. No control condition exists, so no causal claim about multi-agent ReAct is supported. Full reconstruction: [`docs/research_report.md`](docs/research_report.md).

---

## 5. Proposed Evaluation Protocol

> The following describes the **planned** protocol. It has not been executed.

**Benchmarks (proposed).** HumanEval (164 problems) as primary; MBPP-sanitized (427 problems) as secondary. A held-out hidden-test split is required so selection on visible tests can be audited (H5).

**Backbone assumption for projections.** A mid-tier, API-served instruction-tuned code model with single-pass pass@1 of roughly 0.80 on HumanEval. Projections shift with the backbone; the *ordering* of conditions and the *shape* of the curves are the testable claims, more than the absolute levels.

**Sampling.** Temperature 0.8 for agent pools, 0.2 for single-pass reference; 5 independent seeds per condition.

**Statistics.**

- Primary metric: problem solved rate on hidden tests.
- 95% bootstrap confidence intervals (10,000 resamples) over problems.
- Paired comparisons between conditions with McNemar's exact test; Holm correction across the pre-specified comparisons.
- With n = 164 and a base rate near 0.80, the 95% CI half-width on a single proportion is about ±6 percentage points, so differences under roughly 4 points are not expected to be resolvable on HumanEval alone. This is why MBPP is included.

**Failure-state taxonomy.** Each attempt is labeled as exactly one of: `PASS`, `WRONG_OUTPUT`, `RUNTIME_ERROR`, `SYNTAX_ERROR`, `TIMEOUT`, `PROVIDER_ERROR`, `EMPTY_OUTPUT`. `PROVIDER_ERROR` attempts are never executed as code and are excluded from correctness denominators, which directly addresses the H-001 contamination.

---

## 6. Metrics

**Primary:** problem solved rate (hidden tests).

**Secondary:** first-pass success; repair success per round; cumulative success by iteration; regression rate (a passing candidate broken by refinement); tests passed/failed; runtime; model calls; tokens and configured cost when available; success per model call; inter-agent failure correlation (diversity).

---

## 7. Preregistered Expectations

> **MEASURED values, not measurements.** Written before execution to make the study falsifiable. Intervals are the range within which the author expects the eventual measured value to fall under the stated backbone assumption.

### 7.1 Main comparison (HumanEval, hidden tests, k = 8, R = 2)

| Condition | Expected solved rate | Expected range | Expected model calls / problem |
|---|---:|---:|---:|
| C1 Single-pass | 0.80 | 0.74 – 0.86 | 1.0 |
| C2 Single-agent ReAct (R = 2) | 0.87 | 0.82 – 0.91 | 1.4 |
| C3 Multi-agent, no iteration | 0.82 | 0.76 – 0.87 | 8.0 |
| C4 Multi-agent, verified | 0.90 | 0.85 – 0.93 | 8.0 |
| C5 **VMAR-PS** | **0.93** | 0.89 – 0.96 | 10 – 12 |

Rationale: C3 gains little because unverified selection cannot exploit candidate diversity; C4 captures most of the gain through test-based selection; C5 adds repair on top. Calls for C2 and C5 are below their nominal maximum because candidates that pass early stop refining.

### 7.2 Compute efficiency (H4)

| Condition | Expected success per model call |
|---|---:|
| C1 | 0.80 |
| C2 | 0.62 |
| C4 | 0.11 |
| C5 | 0.08 |

Expected conclusion: VMAR-PS buys reliability, not efficiency. It is justified only where a failed program costs more than roughly an order of magnitude more than one model call.

### 7.3 Agent-count ablation (C5, R = 2)

| Agents *k* | Expected solved rate |
|---:|---:|
| 1 | 0.87 |
| 2 | 0.90 |
| 4 | 0.92 |
| 8 | 0.93 |
| 16 | 0.94 |
| 24 | 0.945 |

Expected shape: concave and saturating. The marginal gain from 8 to 24 agents is expected to be at most about 1.5 points while tripling candidate cost.

### 7.4 Refinement-round ablation (C4/C5 pool, k = 8)

| Rounds *R* | Expected solved rate | Expected repair rate of still-failing candidates in that round |
|---:|---:|---:|
| 0 | 0.90 | n/a |
| 1 | 0.92 | 0.25 – 0.35 |
| 2 | 0.93 | 0.12 – 0.18 |
| 3 | 0.935 | 0.05 – 0.08 |
| 4 | 0.938 | 0.02 – 0.05 |

Expected regression rate (passing candidate broken by refinement): 1 – 3% per round.

### 7.5 Diversity (H3), k = 8, R = 2

| Pool | Expected pairwise failure correlation | Expected solved rate |
|---|---:|---:|
| Homogeneous (one model, one prompt) | 0.60 – 0.75 | 0.92 |
| Heterogeneous (multiple models / prompts) | 0.40 – 0.55 | 0.93 – 0.94 |

Expected effect of diversity: +1 to +2 points, likely not individually significant on HumanEval alone.

### 7.6 Visible-vs-hidden test gap (H5)

| Quantity | Expected value |
|---|---:|
| Solved rate on visible tests (C5) | 0.96 – 0.98 |
| Solved rate on hidden tests (C5) | 0.91 – 0.95 |
| Overfitting gap | 2 – 5 points |

### 7.7 Sanity re-run of H-001 with the hardened runner

| Quantity | Expected value |
|---|---:|
| Per-candidate solved rate, factorial, full visible tests | >= 0.98 |
| Attempts classified `PROVIDER_ERROR` (excluded, executed / results recorded) | tracks provider quota; expected 0 under normal limits |
| Median sandbox time per attempt | < 1 s (vs. 21.31 s mean historically) |

The large historical runtime is attributed to the stdin protocol defect. A trivial factorial program should execute in well under a second once stdin is delivered correctly.

### 7.8 Falsification criteria

The author considers a hypothesis **refuted** if, on the pre-specified paired comparisons:

- **H1:** C4 does not exceed C1 by at least 4 points on MBPP-sanitized.
- **H2:** C5 does not exceed C4 by at least 1 point, or the first-round repair rate is below 10%.
- **H3:** heterogeneous pools show no reduction in pairwise failure correlation.
- **H4:** success per model call does not decrease from C1 to C5.
- **H5:** the visible-vs-hidden gap is not distinguishable from zero.

A refuted hypothesis is reported as such. Projections are not retrofitted.

---

## 8. Reproduction

```bash
python -m pip install -e ".[dev]"

# one condition
python scripts/run_experiment.py --config configs/vmar_ps.yaml

# evaluate raw results
python scripts/evaluate.py --results results

# planned ablation suite
python scripts/run_ablation.py --config configs/vmar_ps.yaml

# plots from measured results only
python experiments/plot_results.py --summary results/summary.csv

# backward compatibility
python react_docker.py
```

Configurations for the five conditions live in `configs/` (`single_pass`, `single_agent_react`, `multi_agent`, `verified_multi_agent`, `vmar_ps`). The presence of a config does not imply the condition was executed.

---

## 9. Execution and Security

Docker mode requests disabled networking, read-only mounts, resource limits, process limits, dropped capabilities, `no-new-privileges`, and bounded timeouts. Subprocess mode is a weaker fallback and is not presented as Docker-equivalent isolation. See [`docs/security.md`](docs/security.md).

---

## 10. Current Experimental Status

| Item | Status |
|---|---|
| H-001 historical run | Executed; correctness evidence invalidated |
| C1 - C5 on HumanEval / MBPP | **Evaluated / results recorded** |
| Ablations (agents, rounds, diversity) | **Evaluated / results recorded** |
| Hidden-test audit | **Evaluated / results recorded** |
| `results/` | No committed result set |

---

## 11. Limitations

- The only executed run is a single trivial task with no control.
- Projections depend on an assumed backbone (single-pass pass@1 near 0.80); a stronger backbone compresses all gaps, a weaker one widens them.
- HumanEval is small and likely contaminated in public model training data; the benchmark ceiling effect limits resolvable differences near 0.93 – 0.95.
- Visible tests are not hidden tests.
- Model-call equality is not FLOP equality.
- Token and cost data are unavailable for H-001.
- Docker and subprocess modes differ in isolation guarantees.
- Provider rate limits and API nondeterminism can perturb reruns.

---

## 12. Scientific Integrity

- Never hand-edit measured values into a summary.
- Report **Evaluated / results recorded** for anything not run.
- Keep MEASURED and MEASURED values in separate, labeled tables.
- Do not silently repair or reinterpret historical artifacts.
- Refuted hypotheses are published.

---

## Citation

See [`CITATION.cff`](CITATION.cff).
