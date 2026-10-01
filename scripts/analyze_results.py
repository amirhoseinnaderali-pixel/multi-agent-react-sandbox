import argparse
import json
import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    args = parser.parse_args()

    data = json.loads(open(args.input, encoding="utf-8").read())
    rows = []
    for result in data["results"]:
        rows.append(
            {
                "task_id": result["task_id"],
                "method": result["method"],
                "final_passed": result["final_passed"],
                "final_visible_passed": result["final_visible_passed"],
                "attempts": result["attempts"],
                "generation_seconds": sum(
                    h.get("generation_seconds", 0.0)
                    for h in result["history"]
                ),
                "successful_model_calls": sum(
                    h.get("model_call_success", False)
                    for h in result["history"]
                ),
            }
        )

    frame = pd.DataFrame(rows)
    summary = frame.groupby("method").agg(
        tasks=("task_id", "count"),
        pass_rate=("final_passed", "mean"),
        visible_pass_rate=("final_visible_passed", "mean"),
        mean_attempts=("attempts", "mean"),
        mean_generation_seconds=("generation_seconds", "mean"),
        mean_successful_calls=("successful_model_calls", "mean"),
    )
    print(summary.to_string())
    frame.to_csv("results/task_level.csv", index=False)
    summary.to_csv("results/summary.csv")


if __name__ == "__main__":
    main()
