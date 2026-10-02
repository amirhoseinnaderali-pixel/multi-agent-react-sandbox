from vmar_ps.metrics import summarize_problem

def test_repair_metric():
    result = {
        "problem_id": "p1",
        "method": "vmar_ps",
        "num_agents": 1,
        "max_refinement_rounds": 2,
        "final_success": True,
        "tests_passed": 1,
        "tests_failed": 0,
        "total_model_calls": 2,
        "runtime_seconds": 1.0,
        "iterations_used": 1,
        "attempts": [
            {"iteration": 0, "execution_result": {"execution_success": False}, "revised": False},
            {"iteration": 1, "execution_result": {"execution_success": True}, "revised": True, "previous_success": False},
        ],
    }
    metrics = summarize_problem(result)
    assert metrics["first_pass_success"] == 0
    assert metrics["repair_success"] == 1
