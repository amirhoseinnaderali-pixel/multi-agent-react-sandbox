# Research Positioning

## Existing ideas

The project builds on established ideas including:

- ReAct-style reasoning/action/observation loops
- multi-agent generation
- self-refinement
- execution-guided program synthesis
- sandboxed code execution
- candidate selection

These components should be treated as prior ideas rather than claimed as novel individually.

## Engineering contribution

The implementation integrates those mechanisms into a controlled framework with:

- explicit baseline interfaces
- independent agent-count and refinement variables
- fixed model-call and wall-clock budgets
- persistent attempt-level traces
- standardized execution results
- measurable agent diversity
- deterministic experiment identifiers
- structured evaluation and plotting
- configuration-driven experiment definitions
- automated tests

## Research hypothesis

The empirical contribution remains to be demonstrated. The repository does not claim that multi-agent ReAct improves program synthesis until controlled experiments establish the effect.

## Evidence standard

A convincing study should compare:

- same benchmark
- comparable model-call budgets
- explicit baseline conditions
- uncertainty estimates when sample size permits
- failure-mode distributions
- compute efficiency
- sensitivity to agent count and refinement rounds

The framework itself does not create scientific evidence; it makes evidence collection reproducible.
