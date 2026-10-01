from vmar_ps.sandbox import SubprocessSandbox

def test_subprocess_runs_multiple_tests():
    sandbox = SubprocessSandbox(timeout_seconds=2, memory_limit_mb=256)
    code = "import sys\nn=int(sys.stdin.read().strip())\nprint(n*n)\n"
    result = sandbox.verify(
        code,
        [
            {"input": "2\n", "expected_output": "4"},
            {"input": "3\n", "expected_output": "9"},
        ],
    )
    assert result["compiled"] is True
    assert result["tests_passed"] == 2
    assert result["tests_failed"] == 0
    assert result["execution_success"] is True

def test_subprocess_timeout_does_not_raise():
    sandbox = SubprocessSandbox(timeout_seconds=0.2, memory_limit_mb=128)
    result = sandbox.verify(
        "while True:\n    pass\n",
        [{"input": "", "expected_output": ""}],
    )
    assert result["execution_success"] is False
    assert result["timed_out"] is True
