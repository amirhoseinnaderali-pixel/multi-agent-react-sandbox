import json

from vmar_ps.evaluation import write_summary


def test_result_aggregation(tmp_path):
    run = tmp_path / "abcd"
    run.mkdir()
    payload = {
        "experiment_id": "abcd",
        "problem_id": "p1",
        "method": "single_pass",
        "num_agents": 1,
        "max_refinement_rounds": 0,
        "final_success": True,
        "tests_passed": 1,
        "tests_failed": 0,
        "total_model_calls": 1,
        "runtime_seconds": 0.1,
        "iterations_used": 0,
        "attempts": [],
    }
    (run / "raw_results.jsonl").write_text(json.dumps(payload) + "\n", encoding="utf-8")
    json_path, csv_path = write_summary(tmp_path)
    assert json_path.exists()
    assert csv_path.exists()
    assert "single_pass" in json_path.read_text(encoding="utf-8")
