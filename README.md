# VMAR-PS

## Verified Multi-Agent ReAct for Iterative Program Synthesis

### Portfolio status

**REGISTERED — HISTORICAL RESEARCH CASE STUDY**

VMAR-PS is a research framework for studying executable program-synthesis reliability through:

- multi-agent generation
- ReAct-style iteration
- execution feedback
- iterative refinement
- candidate selection
- inference-time compute

The repository is presented as a research case study: empirical claims come from preserved execution artifacts, while the hardened framework provides the instrument for future controlled experiments.

## Research Question

> Does combining multiple independently configured agents, ReAct-style iteration, execution feedback, and iterative refinement improve executable program-synthesis reliability under the tested conditions?

The current framework expresses this question more formally relative to single-agent and non-iterative baselines. The historical evidence is described separately because the original experiment did not contain valid controls.

## What VMAR-PS Does

The core pipeline is:

~~~text
Problem
  ↓
Agent Pool
  ↓
Independent Generation
  ↓
Execution / Verification
  ↓
Observation / Error Feedback
  ↓
ReAct Refinement
  ↓
Repeated Verification
  ↓
Candidate Selection
  ↓
Final Program
~~~

Each attempt can be retained as structured evidence so that generation, execution, refinement, selection, runtime, model calls, and failure modes can be analyzed without reconstructing hidden state.

---

# Pre-Execution Hypothesis — VMAR-PS

> ⚠️ **HYPOTHESIS / PRIOR ONLY — NOT AN EMPIRICAL RESULT**
>
> The hardened VMAR-PS experiments have not produced a committed controlled result set. The historical H-001 run is preserved separately and its correctness measurement is invalidated.
>
> This section records the expected behavior **before a valid controlled experiment is executed**. The probabilities below are subjective priors, not calibrated posterior probabilities or measured effects.

## Executive hypothesis

VMAR-PS asks whether combining:

- independent multi-agent generation,
- ReAct-style iteration,
- execution feedback,
- iterative refinement,
- and candidate selection

can improve **executable program-synthesis reliability** under a controlled inference-time budget.

The central expectation is:

> **Execution feedback should provide a clearer source of improvement than simply increasing the number of agents, while the marginal benefit of additional agents and refinement rounds should diminish under fixed compute.**

The strongest expected gains are therefore associated with **verification-backed refinement**, while the largest uncertainty concerns whether multi-agent diversity adds enough complementary information to justify its additional inference cost.

---

## Expected behavior

### A. Execution feedback should help

**Prior probability: ~85%**

The strongest expected effect is that seeing concrete execution outcomes provides information that pure textual reasoning cannot reliably reproduce.

Expected mechanism:

```text
Candidate
   ↓
Objective execution
   ↓
Concrete failure signal
   ↓
Targeted repair
   ↓
Re-execution
```

The first repair iteration is expected to provide most of the useful correction signal.

### B. More agents should show diminishing returns

**Prior probability: ~80%**

Increasing the agent pool should initially increase the probability of finding a usable solution, but the marginal value of additional agents should fall as outputs become more correlated.

Expected qualitative pattern:

```text
1 → 2 → 4 agents     meaningful gains
4 → 8 agents         smaller gains
8 → 16 agents        diminishing gains
16 → 24 agents       likely small or negligible gains
```

This is a hypothesis about reliability under increasing inference expenditure, not an assumption that 24 agents are inherently superior.

### C. Fixed-budget advantage over single-agent ReAct may be small

**Prior probability: ~55–60%**

When total inference calls or compute are held fixed, a large multi-agent pool may lose much of its apparent advantage because the same budget could instead be spent on repeated attempts or refinement by fewer agents.

This is one of the most informative possible outcomes for the project:

> **A positive result under unconstrained scaling would not by itself establish an advantage under matched inference cost.**

### D. Later refinement rounds should add less

**Prior probability: ~75%**

The largest improvement is expected in the first repair cycle.

After that, the expected benefits decrease while regression risk increases:

```text
Round 0 → Round 1    largest expected gain
Round 1 → Round 2    smaller gain
Round 2 → Round 3    smaller / uncertain gain
Round 3 → Round 4    likely saturation or regression
```

A later model can repair a defect, but it can also introduce a new defect into an already-correct candidate.

### E. Visible-test selection should not be treated as hidden correctness

**Prior probability: ~70%**

When candidates are selected using visible execution tests, hidden correctness is expected to remain lower than visible-test success on at least some tasks because the visible tests do not exhaustively characterize the program specification.

This makes the separation between:

```text
Visible tests → selection / repair feedback
Hidden tests  → final evaluation
```

scientifically important.

### F. Diversity may matter more than raw agent count

**Prior probability: ~60%**

Twenty-four agents generated by one model with one prompt can produce highly correlated errors.

The expected hypothesis is therefore:

```text
Model / prompt diversity
        ↓
Less-correlated failure modes
        ↓
More complementary candidates
        ↓
Higher useful-candidate probability
```

This is a testable mechanism, not an assumption that heterogeneous models must win.

---

# Projected Conditions and What They Test

The hardened framework exposes several controls:

| Condition family | Main variable | Expected interpretation |
|:--|:--|:--|
| **Single-pass** | 1 agent, no refinement | Reference baseline |
| **Single-agent ReAct** | Refinement depth | Value of iterative execution feedback |
| **Multi-agent** | Agent count | Candidate diversity / redundancy |
| **Verified multi-agent** | Multi-agent + explicit verification | Value of external correctness feedback |
| **VMAR-PS** | Multi-agent + ReAct + verification + selection | Combined mechanism |

These are **experimental interfaces**, not historical measurements.

The framework also exposes agent counts from **1 to 24** and refinement rounds from **0 to 4**, allowing the project to test whether the apparent benefit of scale comes from:

- more independent candidates;
- more refinement;
- verification;
- diversity;
- or interactions between them.

---

# Expected Cost–Reliability Trade-off

The expected relationship is not simply:

```text
more agents = better
```

Instead:

```text
Inference compute
      ↓
More candidate / repair opportunities
      ↓
Higher reliability
      ↓
Diminishing returns
      ↓
Eventually, additional compute mostly buys redundancy
```

The key efficiency metrics should therefore include:

- solved rate;
- first-pass success;
- repair success;
- regression rate;
- cumulative success by iteration;
- success per model call;
- tokens when available;
- configured / measured cost when available;
- runtime;
- diversity measures.

A strategy with a higher raw solved rate is not automatically more efficient if it consumes substantially more model calls.

---

# Expected Error Patterns

The pre-execution hypothesis expects several recurring failure modes:

```text
Generation error
      ↓
Execution failure
      ↓
Repair attempt
      ↓
 ┌───────────────┐
 │ correct repair│
 │ or regression │
 └───────────────┘
```

The most informative quantities are therefore expected to be:

| Measure | Expected behavior |
|:--|:--|
| **Repair success** | Positive, especially in the first iteration |
| **Regression rate** | Increases or remains nontrivial at later rounds |
| **Success per call** | Peaks at low-to-moderate agent counts |
| **Cumulative success** | Improves with more attempts, but sub-linearly |
| **Diversity benefit** | Strongest when candidate errors are complementary |

These are expected patterns, not observed measurements.

---

# Historical H-001 vs. Future Controlled Evidence

The historical H-001 run must remain separate from these priors.

H-001:

- used one trivial factorial task;
- preserved 24 candidate/agent traces;
- recorded 24 first-iteration attempts;
- lacked a valid baseline control;
- used a legacy process-level success flag;
- suffered from stdin / termination and API-error contamination;
- did not provide a trustworthy correctness rate.

Therefore the historical run **cannot validate or invalidate** the hypotheses above.

The first valid evidence for these hypotheses must come from a controlled execution of the hardened framework with explicit baseline conditions, objective correctness tests, and preserved raw attempt-level records.

---

# What Would Falsify the Hypotheses?

The pre-execution projection would be materially weakened by outcomes such as:

- execution feedback failing to improve reliability over a matched non-feedback baseline;
- 16–24 agents providing clear gains with little or no diminishing return;
- later refinement rounds consistently outperforming the first repair round;
- matched-budget multi-agent systems substantially outperforming simpler single-agent strategies without requiring more compute;
- diversity measures showing no relationship to complementary candidate errors;
- visible-test improvements translating almost perfectly into hidden-test correctness, indicating little selection gap.

A negative or surprising result would still be scientifically useful because these hypotheses are explicitly intended to be falsifiable.

---

# Pre-Execution Scorecard

Freeze before the first valid controlled run:

- [ ] Execution feedback improves over the corresponding non-feedback control
- [ ] The largest refinement gain occurs in the first repair iteration
- [ ] Additional agents show diminishing returns
- [ ] 16–24 agents add little relative to lower agent counts
- [ ] Matched-budget multi-agent advantage is substantially smaller than unconstrained scaling would suggest
- [ ] Diversity explains some of the gain beyond raw agent count
- [ ] Hidden-test performance is lower than visible-test performance on at least some tasks

This scorecard records the prior and should not be edited retrospectively after seeing results.

---

# Scientific Guardrails for the Future Run

The future controlled study should preserve the following distinctions:

- **Historical H-001** remains raw historical evidence with invalid correctness measurement.
- **Validation / smoke runs** are not empirical benchmark results.
- **Hardened experiment outputs** become scientific evidence only after objective evaluation and provenance checks pass.
- Model-call equality is not automatically FLOP equality.
- Docker and subprocess execution should not be treated as equivalent isolation environments.
- Visible tests must remain separate from hidden final evaluation when used for selection or repair.
- Every attempt should retain enough structured metadata to reconstruct generation, execution, repair, selection, and failure state.

The goal is to make the experiment capable of separating:

```text
Agent count
      ×
Iteration depth
      ×
Execution feedback
      ×
Candidate diversity
      ×
Inference cost
```

rather than attributing all improvements to a single "multi-agent" effect.

---

## Historical Experiments Actually Performed

The repository contains one preserved empirical run:

**Legacy H-001 — 24-agent ReAct factorial prototype**

- 1 factorial programming task
- 24 recorded candidate/agent traces
- 24 recorded iterations
- up to 3 refinement iterations configured, but every recorded candidate stopped after its first iteration
- execution feedback was present, but only the first declared test case was used
- the historical artifact records no trustworthy correctness rate
- 4 entries contain API quota-error text that was converted into Python source and then produced SyntaxError
- 17 attempts have approximately 30-second execution times consistent with the later-identified stdin/termination problem
- 3 attempts report legacy process-level success with empty output
- no single-pass or other baseline was executed in the preserved artifact

The original success field is **not** used as a correctness metric.

See the full reconstruction in [docs/research_report.md](docs/research_report.md).

## Main Observed Findings

The strongest historical finding is diagnostic rather than a performance result:

1. The original pipeline did produce and preserve 24 multi-agent generation/execution traces.
2. The raw artifact exposes a concrete mismatch between the legacy success flag and actual execution evidence, including SyntaxError records marked as successful.
3. The original stdin protocol and API-error handling could contaminate execution measurements.
4. Because there was no valid control condition and no trustworthy correctness signal, the historical run cannot establish that multi-agent generation, ReAct, execution feedback, refinement, or diversity improved program-synthesis reliability.

This is why the later hardened framework uses objective test outcomes, explicit failure states, attempt-level traces, and explicit compute controls.

## Baselines and Controls in the Hardened Framework

The current runner implements interfaces for:

1. Single-pass
2. Single-agent ReAct
3. Multi-agent without iteration
4. Multi-agent with explicit verification and selection
5. VMAR-PS

Supported experimental controls include:

- agent count: 1, 2, 4, 8, 16, 24
- refinement rounds: 0, 1, 2, 3, 4
- fixed model-call budgets
- fixed wall-clock budgets
- selection strategy
- execution mode
- model/provider/prompt diversity

These are **experimental capabilities**, not historical benchmark results.

## Metrics

Primary:

- problem solved rate

Secondary:

- first-pass success
- repair success
- cumulative success by iteration
- regression rate
- tests passed/failed
- runtime
- model calls
- tokens when available
- configured cost when available
- success per model call
- diversity measures

A model-call budget is a practical control variable, not an assertion of equal FLOPs.

## Reproduction

Install:

~~~bash
python -m pip install -e ".[dev]"
~~~

Run one condition:

~~~bash
python scripts/run_experiment.py --config configs/vmar_ps.yaml
~~~

Evaluate raw results:

~~~bash
python scripts/evaluate.py --results results
~~~

Run the planned ablation suite:

~~~bash
python scripts/run_ablation.py --config configs/vmar_ps.yaml
~~~

Generate plots from measured results:

~~~bash
python experiments/plot_results.py --summary results/summary.csv
~~~

Backward compatibility:

~~~bash
python react_docker.py
~~~

## Execution and Security

Docker mode requests disabled networking, read-only mounts, resource limits, process limits, dropped capabilities, no-new-privileges, and bounded timeouts.

Subprocess mode is a weaker fallback and is not presented as Docker-equivalent isolation.

See [docs/security.md](docs/security.md).

## Current Experimental Status

- **Historical H-001:** executed, but correctness evidence is invalidated by the legacy measurement protocol.
- **Hardened baseline/VMAR-PS experiments:** no committed execution results found.
- **New experiments:** not yet evaluated.
- results2.json remains the historical raw artifact.
- results/ currently contains no new committed result set.

The research report explicitly distinguishes RAW EXECUTION EVIDENCE from DERIVED, HISTORICAL, and DOCUMENTATION-ONLY evidence.

## Limitations

- The historical benchmark contains only one trivial factorial task.
- No historical one-shot control was run.
- Visible tests are not hidden tests.
- The original stdin protocol could cause false timeouts.
- The original success flag was not a correctness criterion.
- API quota failures could enter the code-execution path.
- Historical model/provider/profile metadata is incomplete.
- Token and cost data are unavailable for H-001.
- Model-call equality is not FLOP equality.
- Docker and subprocess modes have different isolation properties.
- A single historical run cannot support broad or causal claims.

## Research Report

For the complete historical reconstruction, result tables, evidence-quality classification, failure analysis, and conclusion:

[docs/research_report.md](docs/research_report.md)

## Scientific Integrity

Never hand-edit result values into a summary.

Use **Not yet evaluated** when a measurement has not been run.

Use **[EXPERIMENT REQUIRED]** in the paper draft when evidence is missing.

Historical artifacts are not silently repaired or converted into new empirical results.
