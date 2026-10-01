# Methodology

## Pipeline

~~~text
Problem
  ↓
Agent Pool
  ↓
Independent Program Generation
  ↓
Execution / Verification
  ↓
Observation + Error Feedback
  ↓
ReAct Refinement
  ↓
Repeated Verification
  ↓
Candidate Selection
  ↓
Final Program
~~~

## Stage definitions

| Stage | Input | Output | Model/computation | Decision rule | Failure conditions |
|---|---|---|---|---|---|
| Problem loading | Benchmark file | Problem prompt + tests | Local file I/O | Valid JSON/JSONL schema | Missing/invalid benchmark |
| Agent pool | YAML config | Ordered agent profiles | Configuration resolution | num_agents and optional pool cycling | Empty pool or disallowed expansion |
| Generation | Prompt + problem | Program text | Configured LLM | One model call per attempt | API/model failure |
| Code extraction | Model text | Python source | Deterministic string parsing | Fenced code extraction or raw text | Empty/invalid source |
| Verification | Source + tests | Structured execution result | Docker or subprocess | Every configured visible test | Syntax, runtime, timeout, memory, wrong output, sandbox failure |
| Feedback | Execution result | Text observation | Deterministic formatter | Include all test outcomes and error fields | Missing result fields |
| Refinement | Problem + prior code + feedback | Revised program | Configured LLM | Up to maximum refinement rounds | API failure, repeated failure, budget exhaustion |
| Selection | Candidate set | Selected candidate | Deterministic selector | Named strategy in config | No candidate, no verified candidate |
| Aggregation | Raw results | Summary tables | Local computation | Group by method | Empty result set |

## Methods

1. single_pass: one agent, one generation, no refinement.
2. single_agent_react: one agent with execution feedback and iterative refinement.
3. multi_agent: multiple independent agents, one generation each, no refinement; first verified candidate selection.
4. verified_multi_agent: multiple independent agents, one generation each, no refinement; max-tests-passed selection.
5. vmar_ps: multiple agents with execution-guided iterative refinement and explicit selection.

All methods share the same benchmark and sandbox interfaces.

## Attempt logging

Every generation attempt is retained. An attempt records:

- attempt ID
- iteration
- agent ID
- provider
- model
- prompt variant
- generated code
- execution result
- feedback
- whether the attempt was a revision
- previous success state
- model-call index
- token usage when returned
- estimated cost when configured

Previous attempts are never replaced.

## Verification semantics

A candidate is final_success only when every visible benchmark test passes.

The framework separates:

- compiled
- execution_success
- tests_passed
- tests_failed
- runtime_seconds
- exit_code
- timed_out
- error_type

A subprocess exit code of zero alone is not sufficient to call a candidate correct.

## Selection semantics

Generation, verification, and selection are independent stages. The selected program is traceable to its candidate and final attempt.
