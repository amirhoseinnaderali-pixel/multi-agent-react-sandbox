# VMAR-PS

## Verified Multi-Agent ReAct for Iterative Program Synthesis

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
