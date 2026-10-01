# Research Audit — Multi-Agent ReAct Sandbox

## Research question

> Does execution feedback improve held-out code correctness compared with one-shot generation under a fixed inference budget?

The controlled comparison is:
- Direct: one generation call, no execution feedback.
- ReAct: generate, execute visible tests, feed the result back, then regenerate up to a fixed number of attempts.

## Problems in the original experiment

1. The subprocess runner waited for the generated program to finish before providing stdin, so ordinary programs using input() could time out.
2. The main ReAct loop used only the first test case rather than evaluating all declared tests.
3. Process exit code was treated as success; that is not equivalent to passing the specification.
4. The loop stopped at the first process-level success instead of demonstrated correctness.
5. API quota errors could be converted into source text and then reported as a successful process.
6. The historical task was a single trivial factorial problem.
7. There was no one-shot control condition.

## Redesign

This branch adds six programming tasks. Each task has visible feedback tests and held-out evaluation tests.

Methods:
- Direct: one model call.
- ReAct: up to three model calls, using visible execution feedback after failures.

Primary metric: held-out evaluation pass rate.

Secondary metrics:
- visible feedback pass rate
- attempts used
- generation latency
- execution failures

## Hypothesis

> Execution feedback will improve held-out coding correctness compared with one-shot generation, at the cost of additional inference-time compute.

This is falsifiable.

## Interpretation

Accuracy should be reported together with model calls and latency. The scientific question is whether extra inference computation is useful and how efficiently it converts into correctness.