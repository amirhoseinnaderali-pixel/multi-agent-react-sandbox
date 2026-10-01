# Multi-Agent ReAct Sandbox

A controlled study of execution feedback as inference-time compute for code-generating language models.

## Research question

> Does execution feedback improve held-out code correctness compared with one-shot generation?

`Direct` uses one generation call.

`ReAct` uses generate → execute visible tests → feed execution feedback back → regenerate, up to three attempts.

## Why the original experiment was insufficient

The historical factorial experiment had a useful execution-feedback idea, but the protocol was not a valid correctness benchmark:

- stdin was supplied after waiting for process completion, so ordinary input()-based programs could time out;
- only the first test case was used inside the ReAct loop;
- process exit code was treated as correctness;
- the loop stopped on the first process-level success;
- API quota errors could become Python source text;
- the benchmark used a single trivial factorial task;
- no one-shot control condition existed.

This branch keeps the historical artifact and adds a corrected experiment.

## Controlled benchmark

`benchmarks/tasks.json` contains six programming tasks.

Each task has visible feedback tests and held-out evaluation tests.

| Method | Calls/task | Feedback |
|---|---:|---|
| Direct | 1 | No |
| ReAct | up to 3 | Yes |

Primary metric: held-out task pass rate.

Secondary metrics:
- visible-test pass rate
- attempts
- model-generation latency
- successful model calls

## Run

Set the API key outside the repository:

```bash
export GOOGLE_API_KEY=...
```

Then:

```bash
pip install -r requirements.txt
python scripts/run_controlled.py --config configs/research.yaml
python scripts/analyze_results.py --input results/controlled.json
```

## Hypothesis

> Execution feedback will improve held-out coding correctness compared with one-shot generation, at the cost of additional inference-time compute.

Accuracy must be interpreted together with attempts and latency.

## Current status

Implemented:
- corrected stdin protocol
- objective multi-test execution
- visible-feedback / held-out-evaluation split
- direct vs ReAct comparison
- result logging and analysis

Not yet executed:
- the controlled experiment itself

## Research trajectory

`iterative prompting → structured agents → executable feedback → efficient inference-time compute`

The central question is whether extra computation can be allocated selectively to improve correctness efficiently.