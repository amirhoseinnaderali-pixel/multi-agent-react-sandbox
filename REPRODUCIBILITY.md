# Reproducibility

Set the API key outside the repository:

```bash
export GOOGLE_API_KEY=...
```

Run:

```bash
pip install -r requirements.txt
python scripts/run_controlled.py --config configs/research.yaml
python scripts/analyze_results.py --input results/controlled.json
```

Keep fixed:
- model identifier
- temperature
- prompt templates
- visible feedback tests
- held-out evaluation tests
- maximum attempts

Record the model, git SHA, task-set hash, and run timestamp for repeated experiments.