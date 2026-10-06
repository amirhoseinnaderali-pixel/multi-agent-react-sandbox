# Failure Taxonomy

The framework classifies failures into operational categories.

| Failure | Definition |
|---|---|
| generation_failure | Model returned unusable generation content |
| syntax_error | Generated source does not compile or parse as Python |
| compilation_error | Reserved for future multi-language backends |
| runtime_error | Program exited with an error |
| timeout | Execution exceeded the configured time limit |
| memory_failure | Process or container exceeded the configured memory boundary |
| wrong_output | Program ran but output did not match expected output |
| incomplete_solution | Source is empty or missing required executable content |
| test_case_overfitting | Requires explicit hidden-test configuration; not inferred automatically |
| refinement_failure | Revisions failed to recover correctness |
| sandbox_failure | Test could not be executed reliably |
| model_api_failure | Provider/API error such as quota exhaustion |

## Classification rule

Classification is attached to each execution attempt.

The framework does not convert an API error into a code failure and does not convert a zero exit code into correctness.

## Research questions enabled

For each error class, ask how often the first attempt fails this way, how often one feedback cycle repairs it, how often agent diversity recovers it, and which failures persist across more agents and more iterations.

## Limitations

Some environments expose incomplete error information. Failure categories are operational labels, not perfect causal diagnoses.
