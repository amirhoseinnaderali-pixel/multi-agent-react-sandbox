# Ablation Plan

## Core matrix

| Variant | Multi-Agent | ReAct | Execution Feedback | Iterative Refinement |
|---|---:|---:|---:|---:|
| Single-pass | No | No | No | No |
| Single-agent ReAct | No | Yes | Yes | Yes |
| Multi-agent | Yes | No | Verification only | No |
| Multi-agent + verification | Yes | No | Yes | No |
| VMAR-PS | Yes | Yes | Yes | Yes |

## Agent-count sweep

Run:

1, 2, 4, 8, 16, 24

while keeping benchmark, model pool, prompt variants, execution limits, and refinement rounds fixed.

## Refinement sweep

Run:

0, 1, 2, 3, 4

while holding the agent count fixed.

Interpret rounds=0 as a single-pass condition and higher values as increasing refinement opportunities.

## Diversity ablations

At minimum compare:

1. Same model + same prompt across all agents.
2. Same model + diverse prompts.
3. Heterogeneous models + same prompt.
4. Heterogeneous models + diverse prompts.

Record:

- unique models
- unique providers
- unique prompt variants
- first-code agreement rate
- pairwise code Jaccard similarity

## Feedback ablations

Remove execution feedback while keeping the generation and iteration structure otherwise comparable.

The resulting condition must distinguish extra generation attempts from feedback-conditioned generation.

## Selection ablations

Compare:

- first_verified
- max_tests_passed
- first_candidate

Selection must remain explicit in the configuration and results.

## Sandbox ablation

Compare Docker and subprocess modes only when the host can reproduce both. The project must not describe them as equivalent security environments.

## Controlled protocol

For every ablation:

- same benchmark revision
- same visible tests
- same seed
- same model configuration
- same timeout and memory limit
- same budget policy
- same result schema
- preserved raw attempts

No measured cell may be filled by hand.
