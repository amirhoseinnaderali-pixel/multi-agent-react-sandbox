# Compute Budget Controls

## Why budgets matter

A method that makes four times as many model calls can improve accuracy simply by sampling more programs. That effect must not be confused with the effect of ReAct or multi-agent reasoning.

VMAR-PS exposes explicit budget controls.

## Fixed model-call budget

Set:

~~~yaml
budget:
  model_calls: 24
~~~

Every method stops when it reaches that number of reserved calls for a problem.

## Fixed wall-clock budget

Set:

~~~yaml
budget:
  model_calls: null
  wall_clock_seconds: 120
~~~

The runner stops once the wall-clock limit is reached.

## Fixed refinement budget

Set:

~~~yaml
max_refinement_rounds: 3
~~~

The number of refinement rounds is independent of the agent count.

## Natural budget

Set both budget fields to null. The configured method is then allowed to consume its natural number of calls.

Natural-budget results should not be the only basis for causal claims about a component.

## Recommended comparison design

1. Choose a fixed total model-call budget.
2. Run all methods on the same benchmark.
3. Keep model pool and generation limits fixed.
4. Record actual calls, runtime, and tokens.
5. Report absolute success and success per unit compute.

## Budget accounting

A call is counted when the framework reserves a model-call slot before invoking the provider. Failed provider calls therefore consume budget.

## Efficiency metrics

The framework records:

- total model calls
- runtime
- token counts when available
- configured or estimated cost when pricing metadata is supplied
- success per model call

No monetary estimate is invented when provider pricing is not configured.

## Important limitation

A model-call budget is not identical to FLOPs. Different models can have different inference cost, latency, and hidden compute. Model calls are therefore a practical control variable, not a complete measure of computational equivalence.
