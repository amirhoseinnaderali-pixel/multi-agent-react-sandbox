# VMAR-PS

## Verified Multi-Agent ReAct for Iterative Program Synthesis

VMAR-PS is a research framework for controlled experiments on program-synthesis reliability. It studies the interaction between:

- multi-agent generation
- ReAct-style iteration
- execution feedback
- iterative refinement
- candidate selection
- inference compute

The target research identity is VMAR-PS. The intended repository name is verified-multi-agent-react-program-synthesis.

## Abstract

The original repository was a multi-agent coding sandbox with a ReAct-like loop and Docker/subprocess execution. The refactored project makes experimental variables explicit, records attempt-level evidence, adds named baselines, separates agent diversity from iteration, introduces compute budgets, and produces machine-readable evaluation outputs.

No performance claim is made by the framework itself.

## Research Question

Does combining multiple independently configured LLM agents with execution-based feedback and iterative refinement improve executable program-synthesis reliability relative to single-agent and non-iterative baselines under controlled inference budgets?

See docs/research_question.md.

## Hypotheses

- H1: execution-guided multi-agent ReAct may improve verified solution probability under comparable budgets.
- H2: execution feedback may contribute independently of agent count.
- H3: measurable diversity may reduce correlated failure.
- H4: refinement gains may saturate.

These remain hypotheses until measured.

## Method

The core pipeline is:

~~~text
Problem
  ↓
Agent Pool
  ↓
Independent Generation
  ↓
Execution / Verification
  ↓
Observation / Error Feedback
  ↓
ReAct Refinement
  ↓
Repeated Verification
  ↓
Candidate Selection
  ↓
Final Program
~~~

Every attempt remains in the raw result trace.

## Baselines

1. Single-pass
2. Single-agent ReAct
3. Multi-agent without iteration
4. Multi-agent with explicit verification and selection
5. VMAR-PS

The interfaces are implemented in the shared experiment runner.

## Experimental Controls

Agent count can be varied independently from refinement rounds.

Supported agent counts for the planned sweep:

1, 2, 4, 8, 16, 24

Supported refinement settings:

0, 1, 2, 3, 4

Compute controls:

- fixed model-call budget
- fixed wall-clock budget
- fixed refinement budget
- unrestricted natural budget

## Metrics

Primary:

- problem solved rate

Secondary:

- first-pass success
- repair success rate
- cumulative success by iteration
- regression rate
- tests passed
- runtime
- model calls
- tokens when available
- configured cost when available
- success per model call
- diversity measures

## Diversity

Each agent profile records:

- agent ID
- model
- provider
- prompt variant
- temperature
- generation limits
- role

The framework also measures:

- unique models
- unique providers
- unique prompt variants
- first-code agreement
- pairwise lexical Jaccard similarity

The initial similarity metric is deliberately simple and should not be treated as a semantic diversity score.

## Execution and Security

Docker mode requests:

- disabled networking
- read-only root filesystem
- read-only source mount
- resource limits
- process limits
- dropped capabilities
- no-new-privileges
- bounded timeout

Subprocess mode is a weaker fallback. It does not provide container-equivalent isolation and does not disable networking.

See docs/security.md.

## Configuration

Researchers change experiment definitions in configs rather than editing Python.

Files:

~~~text
configs/
  single_pass.yaml
  single_agent_react.yaml
  multi_agent.yaml
  verified_multi_agent.yaml
  vmar_ps.yaml
~~~

API credentials are read from environment variables. Copy .env.example to your local environment and set GEMINI_API_KEY.

The current Google GenAI adapter uses the google-genai Python package and the models.generate_content interface.

## Reproduction

Install:

~~~bash
python -m pip install -e ".[dev]"
~~~

Run one condition:

~~~bash
python scripts/run_experiment.py --config configs/vmar_ps.yaml
~~~

Evaluate raw results:

~~~bash
python scripts/evaluate.py --results results
~~~

Run the planned ablation suite:

~~~bash
python scripts/run_ablation.py --config configs/vmar_ps.yaml
~~~

Generate plots from measured results:

~~~bash
python experiments/plot_results.py --summary results/summary.csv
~~~

Backward compatibility:

~~~bash
python react_docker.py
~~~

The compatibility command now routes to the research runner rather than the legacy hard-coded loop.

## Results

Current repository status:

- Framework implementation: implemented in the refactor branch.
- New experiments: Not yet evaluated.
- Historical results: preserved in results2.json.
- Historical results are not used as evidence for the new study because the legacy success flag is not a reliable correctness criterion.

A historical audit found 24 recorded solutions and 24 total iterations. Four historical entries contain SyntaxError text even though their legacy sandbox success field is true. This is precisely the type of measurement issue the new execution schema is designed to avoid.

## Reproducibility

The framework provides:

- deterministic experiment IDs
- resolved config snapshots
- raw JSONL results
- explicit seed
- structured attempts
- configuration-driven benchmarks
- automated tests
- GitHub Actions test workflow

## Limitations

The first benchmark is intentionally small and is only an executable wiring benchmark. It does not support a scientific conclusion about program synthesis.

Visible tests are not hidden tests. Model-call budgets are not equal to FLOPs. Provider API failures can affect experiments. Docker availability can differ between hosts.

## Paper

See docs/paper.md for the manuscript scaffold.

## Research Positioning

See docs/research_positioning.md. The project does not claim novelty simply because it integrates known components.

## License

The repository's previous license state is preserved unless changed explicitly by the maintainer.

## Citation

See CITATION.cff.

## Scientific Integrity

Never hand-edit result values into a summary.

Use Not yet evaluated when a measurement has not been run.

Use [EXPERIMENT REQUIRED] in the paper draft when evidence is missing.
