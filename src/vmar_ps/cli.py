from __future__ import annotations
import argparse
import json
from pathlib import Path
from .config import load_config
from .pipeline import ExperimentRunner, write_results

def main(default_config: str = "configs/vmar_ps.yaml") -> None:
    parser = argparse.ArgumentParser(description="Run a VMAR-PS experiment.")
    parser.add_argument("--config", default=default_config)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--budget-model-calls", type=int, default=None)
    parser.add_argument("--max-refinement-rounds", type=int, default=None)
    args = parser.parse_args()
    config = load_config(args.config)
    if args.budget_model_calls is not None:
        config.setdefault("budget", {})["model_calls"] = args.budget_model_calls
    if args.max_refinement_rounds is not None:
        config["max_refinement_rounds"] = args.max_refinement_rounds
    if args.output_dir:
        config["output_dir"] = args.output_dir
    runner = ExperimentRunner(config)
    results = runner.run()
    output_root = Path(config.get("output_dir", "results")) / runner.experiment_id
    raw_path = output_root / "raw_results.jsonl"
    write_results(results, raw_path)
    (output_root / "config_resolved.json").write_text(
        json.dumps({k: v for k, v in config.items() if k != "_config_path"}, indent=2),
        encoding="utf-8",
    )
    print(f"experiment_id={runner.experiment_id}")
    print(f"results={raw_path}")
    print(f"problems={len(results)}")
