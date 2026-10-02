from __future__ import annotations
from typing import Any, Dict, Iterable

def summarize_problem(result: Dict[str, Any]) -> Dict[str, Any]:
    attempts = result.get("attempts", [])
    first_success = any(
        a.get("iteration") == 0 and a.get("execution_result", {}).get("execution_success")
        for a in attempts
    )
    final_success = bool(result.get("final_success"))
    repaired = (not first_success) and final_success and any(a.get("iteration", 0) > 0 for a in attempts)
    regression = any(
        a.get("revised") and a.get("previous_success") is True
        and a.get("execution_result", {}).get("execution_success") is False
        for a in attempts
    )
    return {
        "experiment_id": result.get("experiment_id"),
        "problem_id": result.get("problem_id"),
        "method": result.get("method"),
        "num_agents": result.get("num_agents"),
        "max_refinement_rounds": result.get("max_refinement_rounds"),
        "problems": 1,
        "solved": int(final_success),
        "first_pass_success": int(first_success),
        "repair_success": int(repaired),
        "regression": int(regression),
        "tests_passed": result.get("tests_passed", 0),
        "tests_failed": result.get("tests_failed", 0),
        "total_model_calls": result.get("total_model_calls", 0),
        "runtime_seconds": result.get("runtime_seconds", 0.0),
        "iterations_used": result.get("iterations_used", 0),
        "success_per_model_call": (
            1.0 / result["total_model_calls"]
            if final_success and result.get("total_model_calls", 0) > 0 else 0.0
        ),
        "error_type": result.get("error_type"),
    }

def aggregate(results: Iterable[Dict[str, Any]]) -> list[Dict[str, Any]]:
    rows = [summarize_problem(r) for r in results]
    grouped: dict[str, list[Dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["method"]), []).append(row)
    output = []
    for method, items in sorted(grouped.items()):
        n = len(items)
        repair_den = sum(1 for x in items if not x["first_pass_success"])
        calls = sum(x["total_model_calls"] for x in items)
        output.append({
            "method": method,
            "agents": items[0]["num_agents"],
            "iterations": items[0]["max_refinement_rounds"],
            "problems": n,
            "solved": sum(x["solved"] for x in items),
            "success_rate": sum(x["solved"] for x in items) / n if n else 0.0,
            "first_pass_success": sum(x["first_pass_success"] for x in items),
            "repair_success_rate": (
                sum(x["repair_success"] for x in items) / repair_den if repair_den else None
            ),
            "regression_rate": sum(x["regression"] for x in items) / n if n else 0.0,
            "model_calls": calls,
            "runtime_seconds": round(sum(x["runtime_seconds"] for x in items), 4),
            "avg_runtime_seconds": round(sum(x["runtime_seconds"] for x in items) / n, 4) if n else 0.0,
            "avg_iterations_used": round(sum(x["iterations_used"] for x in items) / n, 4) if n else 0.0,
            "success_per_model_call": sum(x["solved"] for x in items) / calls if calls else 0.0,
        })
    return output
