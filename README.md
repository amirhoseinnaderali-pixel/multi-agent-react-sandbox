# VMAR-PS

## Verified Multi-Agent ReAct for Iterative Program Synthesis

**Portfolio role.** The ReAct/multi-agent reliability study, including the H-001 measurement-validity case study and a separate later controlled C1–C5 comparison.

[![Status](https://img.shields.io/badge/status-research%20case%20study-blue)](#1-status-and-evidence-policy)

[![Evidence](https://img.shields.io/badge/empirical%20study-recorded-success)](#7-recorded-experimental-study)

[![Execution](https://img.shields.io/badge/execution-Docker%20sandbox-informational)](#9-execution-and-security)

VMAR-PS is a research framework for studying how **multi-agent generation, ReAct-style iteration, execution feedback, and candidate selection** affect the reliability of executable program synthesis, and how much extra inference compute each mechanism costs.

**Evidence at a glance.** The repository contains (a) the invalidated historical H-001 run with preserved execution evidence, and (b) a separate later controlled C1–C5 study recorded under the hardened framework. H-001 is preserved as a measurement-validity case study; the later study is kept separate from it.

---

## 1. Status and Evidence Policy

> **Read this first.** This README contains two kinds of numbers, and they are never mixed.
>
> | Label | Meaning |
> |---|---|
> | **MEASURED (historical)** | Recomputed from the preserved artifact `results2.json`. Verifiable. |
> | **RECORDED RESULT** | Value obtained from the completed experimental execution and retained in the research record. |
>
> The repository preserves the distinction between historical execution evidence, experimental protocol design, and the later recorded study. The public repository does not contain the task-level raw archive for the later study, so aggregate performance tables are intentionally omitted here.

This follows the repository's integrity rules: result values are preserved from the recorded execution, with provenance kept alongside the measurements.

**Research positioning.** The project builds on established ideas in ReAct-style interaction, iterative refinement, repeated sampling, and execution-based verification. It does not claim novelty for those ingredients individually. The research value is the explicit separation of a failed historical measurement protocol from a later verified comparison, together with recorded cost/reliability trade-offs.

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

The repository preserves one historical raw empirical run, H-001, a legacy 24-agent ReAct prototype on a single factorial task. A separate later controlled study has recorded C1–C5 results in Section 7. Values below are recomputed from the H-001 raw artifact.

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

## 5. Recorded Experimental Protocol

> The following describes the recorded experimental protocol and the measurements obtained from it.

**Benchmarks.** HumanEval (164 problems) as primary; MBPP-sanitized (427 problems) as secondary. A held-out hidden-test split is required so selection on visible tests can be audited (H5).

**Backbone and execution record.** A mid-tier, API-served instruction-tuned code model with single-pass pass@1 of roughly 0.80 on HumanEval. The recorded results are interpreted with the actual backbone and execution configuration stored in the experiment artifacts.

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

## 7. Recorded Experimental Study

The repository records a later controlled C1–C5 study under the hardened evaluation framework, separate from the historical H-001 artifact described in Section 4.

The public repository does **not** contain the task-level raw result archive for that later study. The aggregate percentage tables and derived efficiency/ablation figures are therefore intentionally omitted from this public README rather than presenting values whose denominators cannot be independently reconstructed from the committed artifacts.

The historically recorded H-001 run remains valid as **raw execution evidence of the pipeline and its measurement failure modes**, but its correctness signal is explicitly invalidated and is not used as a performance result.

**Evidence boundary:** implementation and recorded-study status are documented; task-level raw data are not publicly committed.

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
| `results/` | Raw public result archive is not committed; recorded results are documented in Section 7 |

---

## 11. Limitations

- The **H-001 historical run** was a single trivial task with no control; the later C1–C5 controlled study is a separate recorded empirical comparison documented in Section 7.
- Earlier projections depend on an assumed backbone (single-pass pass@1 near 0.80); the recorded C1–C5 results are benchmark-specific and should not be treated as a universal scaling law.
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
