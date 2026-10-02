# VMAR-PS Paper Draft

## 1. Abstract

[EXPERIMENT REQUIRED]

This work introduces VMAR-PS, a configurable framework for studying execution-guided multi-agent reasoning for iterative program synthesis. The system exposes agent count, refinement rounds, execution feedback, selection strategy, and inference budgets as explicit experimental variables. It records complete generation and verification traces so that reliability and compute efficiency can be analyzed without reconstructing hidden state.

## 2. Introduction

Large language models can generate executable programs, but correctness failures remain difficult to diagnose from text generation alone. Execution provides an observable signal: a program can be run against a benchmark and the resulting evidence can be fed into a subsequent generation step.

VMAR-PS studies whether combining this feedback with multiple independent agents changes program-synthesis reliability.

[EXPERIMENT REQUIRED: quantitative motivation]

## 3. Problem Definition

Given a programming problem and a visible test suite, the system must generate a Python program that passes all configured tests.

Let A be the number of agents, R the maximum refinement rounds, B the model-call budget, V the verification procedure, and S the selection strategy.

## 4. Related Work

[EXPERIMENT REQUIRED: literature review and citations]

Relevant conceptual areas include ReAct, multi-agent collaboration, self-refinement, execution-guided code generation, and program synthesis.

## 5. Multi-Agent ReAct Method

Each agent independently receives the problem. After an initial program is executed, failed tests and execution errors are returned as structured feedback. An agent may then revise its program up to the configured refinement limit.

The complete attempt trace is retained.

## 6. Execution-Based Verification

Verification records compilation status, test outcomes, runtime, timeout state, resource limits, exit code, and error classification.

Docker execution disables networking and applies resource restrictions. Subprocess execution is a weaker fallback.

## 7. Experimental Setup

[EXPERIMENT REQUIRED]

The benchmark, models, temperatures, prompt variants, agent counts, refinement rounds, and compute budgets must be listed from resolved configuration files.

## 8. Baselines

The framework defines:

- single-pass
- single-agent ReAct
- multi-agent no-iteration
- multi-agent with explicit verification and selection
- VMAR-PS

## 9. Ablations

[EXPERIMENT REQUIRED]

Planned ablations independently vary agent count, refinement rounds, model diversity, prompt diversity, feedback, selection, and execution mode.

## 10. Results

[EXPERIMENT REQUIRED]

No result should be inserted without a raw experiment record.

## 11. Error Analysis

[EXPERIMENT REQUIRED]

Use attempt-level traces to examine syntax, runtime, timeout, memory, wrong-output, and API failure classes.

## 12. Compute Efficiency

[EXPERIMENT REQUIRED]

Report model calls, runtime, token counts where available, and cost where configured.

## 13. Limitations

Visible tests can underestimate hidden failures. Model-provider changes and rate limits can influence results. Model-call equality is not equal to FLOP equality. The initial diversity metric is lexical rather than semantic.

## 14. Future Work

- larger standardized programming benchmarks
- hidden-test evaluation
- multilingual code generation
- semantic diversity metrics
- statistical uncertainty analysis
- provider-independent model adapters
- resumable distributed experiments

## 15. Conclusion

[EXPERIMENT REQUIRED]

The framework is designed so that central claims are determined by measurements rather than implementation assumptions.
