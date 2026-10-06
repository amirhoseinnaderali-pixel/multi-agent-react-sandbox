#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def read_raw(results_root: Path) -> pd.DataFrame:
    rows = []
    for path in sorted(results_root.rglob("raw_results.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    if not rows:
        raise SystemExit("No raw experiment results found.")
    return pd.json_normalize(rows)


def save_plot(path: Path, title: str, xlabel: str, ylabel: str, plotter) -> None:
    plt.figure()
    plotter()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True, alpha=0.2)
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Generate VMAR-PS plots from raw JSONL results.")
    parser.add_argument("--results", default="results")
    parser.add_argument("--summary", default=None, help="Compatibility alias; raw results are still read.")
    parser.add_argument("--output-dir", default="results/plots")
    args = parser.parse_args()

    results_root = Path(args.results)
    if args.summary and args.results == "results":
        results_root = Path(args.summary).resolve().parent

    frame = read_raw(results_root)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    agent_group = frame.groupby("num_agents", as_index=False)["final_success"].mean()
    save_plot(
        out / "success_vs_agents.png",
        "Success rate vs number of agents",
        "Number of agents",
        "Success rate",
        lambda: plt.plot(agent_group["num_agents"], agent_group["final_success"], marker="o"),
    )

    round_group = frame.groupby("max_refinement_rounds", as_index=False)["final_success"].mean()
    save_plot(
        out / "success_vs_rounds.png",
        "Success rate vs refinement rounds",
        "Maximum refinement rounds",
        "Success rate",
        lambda: plt.plot(round_group["max_refinement_rounds"], round_group["final_success"], marker="o"),
    )

    save_plot(
        out / "success_vs_model_calls.png",
        "Success rate vs model-call budget",
        "Model calls",
        "Final success (0/1)",
        lambda: plt.scatter(frame["total_model_calls"], frame["final_success"]),
    )

    pass_group = frame.groupby("method", as_index=False)[["first_pass_success", "final_success"]].mean()
    def first_final():
        x = range(len(pass_group))
        plt.plot(list(x), pass_group["first_pass_success"], marker="o", label="First-pass")
        plt.plot(list(x), pass_group["final_success"], marker="s", label="Final")
        plt.xticks(list(x), pass_group["method"], rotation=25, ha="right")
        plt.legend()
    save_plot(
        out / "first_pass_vs_final.png",
        "First-pass vs final success",
        "Method",
        "Success rate",
        first_final,
    )

    if "error_type" in frame.columns:
        error_group = frame.dropna(subset=["error_type"])
        if not error_group.empty:
            error_group = error_group.groupby("error_type", as_index=False)["repair_success"].mean()
            def repair_by_error():
                x = range(len(error_group))
                plt.bar(list(x), error_group["repair_success"])
                plt.xticks(list(x), error_group["error_type"], rotation=30, ha="right")
            save_plot(
                out / "repair_success_by_error.png",
                "Repair success by error type",
                "Error type",
                "Repair success rate",
                repair_by_error,
            )

    priced = frame.dropna(subset=["cost_usd"]) if "cost_usd" in frame.columns else pd.DataFrame()
    if not priced.empty:
        save_plot(
            out / "cost_vs_success.png",
            "Compute cost vs success rate",
            "Estimated cost (USD)",
            "Final success",
            lambda: plt.scatter(priced["cost_usd"], priced["final_success"]),
        )

    diversity_col = "diversity.pairwise_code_jaccard_mean"
    if diversity_col in frame.columns:
        diverse = frame.dropna(subset=[diversity_col])
        if not diverse.empty:
            save_plot(
                out / "diversity_vs_performance.png",
                "Output similarity vs performance",
                "Mean pairwise code Jaccard similarity",
                "Final success",
                lambda: plt.scatter(diverse[diversity_col], diverse["final_success"]),
            )

    print(f"plots={out}")


if __name__ == "__main__":
    main()
