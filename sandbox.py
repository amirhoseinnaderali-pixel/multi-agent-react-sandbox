"""Backward-compatible subprocess sandbox wrapper.

For research runs, use src/vmar_ps/sandbox.py and prefer Docker mode.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from vmar_ps.sandbox import SubprocessSandbox


def run_code_in_sandbox(code, input_data="", max_time=30, max_memory_mb=256):
    result = SubprocessSandbox(
        timeout_seconds=max_time,
        memory_limit_mb=max_memory_mb,
    )._run_one(code, input_data)
    return {
        "success": result["exit_code"] == 0 and not result["timed_out"],
        "output": result["output"],
        "error": result["error"],
        "execution_time": result["runtime_seconds"],
        "memory_used_mb": result.get("memory_mb"),
        "timed_out": result["timed_out"],
    }


def run_tests(code, test_cases, max_time=30, max_memory_mb=256):
    result = SubprocessSandbox(
        timeout_seconds=max_time,
        memory_limit_mb=max_memory_mb,
    ).verify(code, test_cases)
    return {
        "passed": result["execution_success"],
        "passed_count": result["tests_passed"],
        "total_count": result["tests_passed"] + result["tests_failed"],
        "test_results": result["test_results"],
    }
