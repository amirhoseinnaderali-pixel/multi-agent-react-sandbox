from pathlib import Path

from vmar_ps.llm import GenerationResponse
import vmar_ps.pipeline as pipeline


class FakeClient:
    def __init__(self):
        self.calls = 0

    def generate(self, **kwargs):
        self.calls += 1
        if self.calls == 1:
            code = "print('wrong')"
        else:
            code = "import sys\nn=int(sys.stdin.read().strip())\nprint(n*n)\n"
        return GenerationResponse(True, code, "fake-model", "fake")


class FakeSandbox:
    mode = "fake"

    def verify(self, code, tests):
        if "wrong" in code:
            return {
                "compiled": True, "execution_success": True,
                "tests_passed": 0, "tests_failed": len(tests),
                "runtime_seconds": 0.01, "memory_mb": None,
                "memory_limit_mb": 256, "network_disabled": False,
                "exit_code": 0, "timed_out": False,
                "error": "Output mismatch", "error_type": "wrong_output",
                "test_results": [],
            }
        return {
            "compiled": True, "execution_success": True,
            "tests_passed": len(tests), "tests_failed": 0,
            "runtime_seconds": 0.01, "memory_mb": None,
            "memory_limit_mb": 256, "network_disabled": False,
            "exit_code": 0, "timed_out": False,
            "error": None, "error_type": None,
            "test_results": [],
        }


def test_react_iteration_preserves_attempt_history(tmp_path: Path, monkeypatch):
    benchmark = tmp_path / "benchmark.json"
    benchmark.write_text(
        '{"problems":[{"id":"p1","prompt":"square n","tests":[{"input":"3\\n","expected_output":"9"}]}]}',
        encoding="utf-8",
    )
    clients = []

    def fake_build_client(agent):
        client = FakeClient()
        clients.append(client)
        return client

    monkeypatch.setattr(pipeline, "build_client", fake_build_client)
    monkeypatch.setattr(pipeline, "build_sandbox", lambda config: FakeSandbox())

    config = {
        "method": "single_agent_react",
        "benchmark": str(benchmark),
        "seed": 1,
        "num_agents": 1,
        "max_refinement_rounds": 1,
        "selection_strategy": "first_verified",
        "agents": [{"agent_id": "a1", "model": "fake", "provider": "fake"}],
        "budget": {"model_calls": 2, "wall_clock_seconds": None},
    }
    result = pipeline.ExperimentRunner(config).run()[0]
    assert result["final_success"] is True
    assert len(result["attempts"]) == 2
    assert result["attempts"][0]["revised"] is False
    assert result["attempts"][1]["revised"] is True
