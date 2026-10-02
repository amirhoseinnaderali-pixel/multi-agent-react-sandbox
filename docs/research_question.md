# Research Question

## Research Question

Does combining multiple independently configured LLM agents with execution-based feedback and iterative refinement improve executable program-synthesis reliability relative to single-agent and non-iterative baselines under controlled inference budgets?

## Motivation

The original repository already contained a 24-agent ReAct-style loop and sandbox execution, but the implementation did not expose enough experimental controls to isolate the effects of agent count, iteration, execution feedback, diversity, or compute.

VMAR-PS turns those mechanisms into independent configuration variables so that a researcher can test them without changing Python code.

## Hypotheses

H1. Multi-agent ReAct with execution feedback increases the probability that a benchmark problem reaches a fully verified solution compared with single-pass generation under a comparable compute budget.

H2. Execution feedback contributes independently to reliability beyond simply increasing the number of independent generations.

H3. Greater measurable agent/model/prompt diversity is associated with lower correlated failure and higher robustness.

H4. Additional refinement rounds improve cumulative correctness up to a saturation point rather than monotonically indefinitely.

These hypotheses were evaluated in the recorded study; the observed results are reported separately from the hypothesis statements.

## Variables

### Independent variables

- Agent count: 1, 2, 4, 8, 16, 24.
- Maximum refinement rounds: 0, 1, 2, 3, 4.
- ReAct enabled/disabled.
- Execution feedback enabled/disabled through the selected baseline/method.
- Agent diversity: unique models, providers, prompt variants, and measured output similarity.
- Selection strategy.
- Execution mode: Docker or subprocess.
- Compute budget: model calls and wall-clock limit.

### Dependent variables

- Problem solved rate.
- First-pass success.
- Repair success rate.
- Cumulative success by iteration.
- Regression rate.
- Tests passed and failed.
- Runtime.
- Model calls.
- Tokens when returned by the provider.
- Cost when pricing is configured.
- Success per model call.

### Controlled variables

- Benchmark problem set.
- Test cases.
- Python runtime/container image.
- Timeout.
- Memory limit.
- Seed/config identity.
- Agent generation parameters where the experiment is not explicitly varying them.

## Expected mechanism

The proposed mechanism is:

1. Independent agents create candidate programs.
2. Execution reveals concrete evidence about correctness.
3. Feedback gives an individual agent an actionable observation for refinement.
4. Repeated verification removes candidates that do not satisfy the benchmark.
5. Diversity may reduce correlated failures, while selection chooses among verified candidates.

The mechanism is an experimental explanation, not an established result.

## Threats to validity

- Visible tests are not equivalent to hidden benchmark tests.
- A small benchmark can overstate apparent reliability.
- Different models may have very different baseline capabilities.
- Agent count can increase inference compute unless budgets are explicitly matched.
- Prompt diversity can be confounded with model diversity.
- Docker and subprocess execution have different isolation properties.
- API quotas, transient failures, and provider-side changes can affect results.
- Token and cost metadata may be unavailable for some providers.
- Semantic output diversity is approximated with lexical Jaccard similarity in the initial implementation.
