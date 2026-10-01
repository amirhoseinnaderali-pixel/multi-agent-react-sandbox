# Result Schema

Each problem result is one JSON object in raw_results.jsonl.

## Top-level fields

~~~json
{
  "schema_version": "1.0",
  "experiment_id": "deterministic-hash",
  "experiment_seed": 7,
  "problem_id": "factorial_basic",
  "method": "vmar_ps",
  "num_agents": 24,
  "configured_num_agents": 24,
  "max_refinement_rounds": 3,
  "selection_strategy": "max_tests_passed",
  "execution_mode": "docker",
  "first_pass_success": false,
  "repair_success": true,
  "final_success": true,
  "tests_passed": 3,
  "tests_failed": 0,
  "runtime_seconds": 3.21,
  "total_model_calls": 8,
  "input_tokens": 1000,
  "output_tokens": 500,
  "total_tokens": 1500,
  "cost_usd": null,
  "iterations_used": 2,
  "error_type": null
}
~~~

## Attempt schema

Every attempt records:

~~~json
{
  "attempt_id": "problem:agent:iteration",
  "iteration": 1,
  "agent_id": "agent_01",
  "model": "model-name",
  "provider": "google",
  "prompt_variant": "standard",
  "generated_code": "...",
  "execution_result": {},
  "feedback": "...",
  "revised": true,
  "previous_success": false,
  "model_call_index": 4,
  "input_tokens": null,
  "output_tokens": null,
  "total_tokens": null,
  "cost_usd": null
}
~~~

## Execution result

The object contains compiled, execution_success, tests_passed, tests_failed, runtime_seconds, memory_mb, memory_limit_mb, network_disabled, exit_code, timed_out, error, error_type, test_results, and execution_mode.

## Missing data policy

The framework uses null rather than inventing a value.

If a provider does not expose token usage, token fields remain null.

If pricing is not configured, cost_usd remains null.

If an experiment has not been run, downstream reports should state Not yet evaluated.
