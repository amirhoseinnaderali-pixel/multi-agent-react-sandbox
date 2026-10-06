# Selection Strategy

## Separation of stages

### Generation
Which programs were produced?

### Verification
Which generated programs passed visible tests?

### Selection
Which verified candidate was selected as the final answer?

## Strategies

### first_verified
Select the first candidate whose final attempt passes all visible tests.

### max_tests_passed
Rank candidates by final verification success, number of visible tests passed, and fewer refinement iterations.

### first_candidate
Select the first candidate without using verification result as a ranking criterion. This is a control for selection effects.

## Traceability

The selected candidate ID and selected attempt ID are retained in raw results.

## Research implication

Selection is an experimental variable. Changing it changes the experiment configuration and deterministic experiment identity.
