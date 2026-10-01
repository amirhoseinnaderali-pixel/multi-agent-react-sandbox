import argparse
import hashlib
import json
import os
import time
from pathlib import Path

import yaml

from api_client import call_model
from sandbox import run_tests


FENCE = chr(96) * 3


def extract_code(text):
    text = (text or "").strip()
    python_fence = FENCE + "python"
    if python_fence in text:
        return text.split(python_fence, 1)[1].split(FENCE, 1)[0].strip()
    if FENCE in text:
        parts = text.split(FENCE)
        if len(parts) >= 3:
            return parts[1].strip()
    return text


def feedback_text(rows):
    return "\n".join(
        f"Test {i}: {'PASS' if row['passed'] else 'FAIL'}; "
        f"expected={row['expected']!r}; actual={row['actual']!r}; "
        f"stderr={row['stderr']!r}"
        for i, row in enumerate(rows, 1)
    )


def direct_prompt(problem):
    return (
        "Write a complete Python 3 program for the following programming problem. "
        "Return only code.\n\nProblem:\n" + problem
    )


def react_prompt(problem, previous_code, feedback):
    return (
        "Fix the Python 3 program using the execution feedback below. "
        "Return only the complete corrected program.\n\n"
        f"Problem:\n{problem}\n\n"
        f"Previous program:\n[CODE]\n{previous_code}\n[/CODE]\n\n"
        f"Execution feedback:\n{feedback}"
    )


def run_task(task, method, model, temperature, max_iterations):
    history = []
    previous_code = None
    visible = None

    for attempt in range(1, max_iterations + 1):
        prompt = direct_prompt(task["problem"])
        if method == "react" and previous_code is not None:
            prompt = react_prompt(
                task["problem"],
                previous_code,
                feedback_text(visible["test_results"]),
            )

        generation_started = time.perf_counter()
        response = call_model(
            model,
            prompt,
            os.environ["GOOGLE_API_KEY"],
            temperature=temperature,
        )
        generation_seconds = time.perf_counter() - generation_started

        if not response["success"]:
            history.append(
                {
                    "attempt": attempt,
                    "model_call_success": False,
                    "error": response["error"],
                    "generation_seconds": generation_seconds,
                }
            )
            break

        code = extract_code(response["output"])
        visible = run_tests(code, task["feedback_tests"])
        evaluation = run_tests(code, task["eval_tests"])

        history.append(
            {
                "attempt": attempt,
                "model_call_success": True,
                "code": code,
                "visible": visible,
                "evaluation": evaluation,
                "generation_seconds": generation_seconds,
            }
        )

        if method == "direct" or visible["passed"]:
            break

        previous_code = code

    final = history[-1]
    return {
        "task_id": task["id"],
        "method": method,
        "attempts": len(history),
        "final_passed": final.get("evaluation", {}).get("passed", False),
        "final_visible_passed": final.get("visible", {}).get("passed", False),
        "history": history,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/research.yaml")
    args = parser.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text())
    tasks = json.loads(Path(cfg["tasks_file"]).read_text())["tasks"]

    results = {
        "model": cfg["model"],
        "temperature": cfg["temperature"],
        "max_iterations": cfg["max_iterations"],
        "task_hash": hashlib.sha256(
            json.dumps(tasks, sort_keys=True).encode()
        ).hexdigest()[:16],
        "created_unix": time.time(),
        "results": [],
    }

    for method in cfg["methods"]:
        for task in tasks:
            print(f"{method}: {task['id']}")
            results["results"].append(
                run_task(
                    task,
                    method,
                    cfg["model"],
                    cfg["temperature"],
                    cfg["max_iterations"] if method == "react" else 1,
                )
            )

    Path("results").mkdir(exist_ok=True)
    Path("results/controlled.json").write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
