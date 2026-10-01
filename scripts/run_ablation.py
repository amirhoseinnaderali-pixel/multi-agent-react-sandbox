#!/usr/bin/env python3
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vmar_ps.config import load_config
from vmar_ps.pipeline import ExperimentRunner, write_results

def run_job(base_config, name, method, num_agents, rounds, output_dir, fixed_calls):
    config = copy.deepcopy(base_config)
    config["method"] = method
    config["num_agents"] = num_agents
    config["max_refinement_rounds"] = rounds
    config["output_dir"] = str(output_dir)
    if fixed_calls is not None:
        config.setdefault("budget", {})["model_calls"] = fixed_calls
    config["experiment_label"] = name
    runner = ExperimentRunner(config)
    results = runner.run()
    root = Path(output_dir) / "ablation" / runner.experiment_id
    write_results(results, root / "raw_results.jsonl")
    (root / "config_resolved.json").write_text(
        json.dumps({k: v for k, v in config.items() if k != "_config_path"}, indent=2),
        encoding="utf-8",
    )
    return runner.experiment_id

def main():
    parser = argparse.ArgumentParser(description="Run controlled VMAR-PS ablations.")
    parser.add_argument("--config", default="configs/vmar_ps.yaml")
    parser.add_argument("--output-dir", default="results")
    parser.add_argument("--agents", default="1,2,4,8,16,24")
    parser.add_argument("--rounds", default="0,1,2,3,4")
    parser.add_argument("--fixed-model-calls", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    base = load_config(args.config)
    agent_values = [int(x) for x in args.agents.split(",") if x.strip()]
    round_values = [int(x) for x in args.rounds.split(",") if x.strip()]
    jobs = []
    base_agents = max(agent_values)
    base_rounds = max(round_values)

    for n in agent_values:
        jobs.append((f"agents_{n}_rounds_{base_rounds}", "vmar_ps", n, base_rounds))
    for r in round_values:
        jobs.append((f"agents_{base_agents}_rounds_{r}", "vmar_ps", base_agents, r))
    jobs.extend([
        ("single_pass", "single_pass", 1, 0),
        ("single_agent_react", "single_agent_react", 1, base_rounds),
        ("multi_agent", "multi_agent", base_agents, 0),
        ("verified_multi_agent", "verified_multi_agent", base_agents, 0),
    ])

    for name, method, n, r in jobs:
        print(f"{name}: method={method} agents={n} rounds={r}")
        if not args.dry_run:
            run_job(base, name, method, n, r, args.output_dir, args.fixed_model_calls)

if __name__ == "__main__":
    main()
