from sandbox import run_code_in_sandbox, run_tests


def test_stdin_is_sent_before_timeout():
    result = run_code_in_sandbox(
        "n = int(input())\nprint(n * 2)\n",
        input_data="21\n",
        max_time=2,
    )
    assert result["success"]
    assert result["output"].strip() == "42"


def test_all_declared_tests_are_checked():
    result = run_tests(
        "print(input().strip().upper())\n",
        [
            {"input": "a\n", "expected_output": "A"},
            {"input": "b\n", "expected_output": "B"},
        ],
        max_time=2,
    )
    assert result["passed"]
    assert result["passed_count"] == 2
    assert result["total_count"] == 2
