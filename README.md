# VMAR-PS

**Verified Multi-Agent ReAct for Iterative Program Synthesis**

VMAR-PS explores whether generating several code candidates, running them against tests, and refining failures with execution feedback improves program-synthesis reliability—and what extra inference cost it adds.

## How it works

```text
Problem → independent agents generate code
        → run candidates in a sandbox
        → use test failures as feedback
        → refine candidates (up to R rounds)
        → select a candidate using test results
```

The framework records candidates, execution outcomes, errors, runtime, and model-call information when available.

## Conditions compared

| Condition | Setup |
|---|---|
| **C1 — Single-pass** | One agent, one attempt |
| **C2 — Single-agent ReAct** | One agent refines code using execution feedback |
| **C3 — Multi-agent** | Several independent candidates, no refinement |
| **C4 — Verified multi-agent** | Several candidates; select using tests |
| **C5 — VMAR-PS** | Multi-agent generation, feedback, refinement, and test-based selection |

## What happened?

### 1. Historical run H-001: useful failure analysis, not a performance result

The preserved legacy run attempted one simple factorial problem with 24 candidates. It exposed important measurement bugs:

- **No refinement actually occurred**, despite a configured limit of three rounds.
- **Four API quota-error messages were treated as code.**
- Some processes were marked successful despite empty output; the old success flag therefore did not establish correctness.
- Stdin handling and process termination produced misleading timeouts.

The recorded 24/24 legacy “successes” are **invalid as a correctness score**. H-001 is kept as a case study in how evaluation can go wrong—not as evidence that the method works better.

### 2. Later C1–C5 study: results reported, raw archive missing

The README records a separate controlled comparison on **HumanEval (164 problems)** and **MBPP-sanitized (427 problems)**, with five seeds per condition. However, the task-level result archive is not committed publicly. The aggregate accuracy figures are therefore omitted here: readers cannot independently reconstruct them from the public files.

**Evidence boundary:** the later study is recorded as completed, but its quantitative conclusions are not independently verifiable from the public repository alone.

## Reproduce a run

```bash
python -m pip install -e ".[dev]"
python scripts/run_experiment.py --config configs/vmar_ps.yaml
python scripts/evaluate.py --results results
```

The configs for C1–C5 live in `configs/`. Running them starts a new experiment; it does **not** recover the missing task-level archive from the later study.

## Execution safety

Docker mode requests restrictions such as disabled networking, read-only mounts, resource limits, dropped capabilities, and timeouts. The subprocess fallback provides weaker isolation and should not be treated as equivalent to Docker. See [docs/security.md](docs/security.md).

## Limitations

- Visible-test selection can overestimate performance on hidden tests.
- Equal model-call budgets do not mean equal FLOPs or cost.
- H-001 has no valid correctness score and no recorded token/cost data.
- The later study's raw task-level results are not publicly committed.

See [docs/research_report.md](docs/research_report.md) for the H-001 analysis and [CITATION.cff](CITATION.cff) for citation information.
