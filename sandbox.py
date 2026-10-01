"""
Corrected subprocess sandbox used by the research benchmark.

The key protocol rule is: stdin is supplied while the process is running,
not after waiting for the process to exit.
"""

import subprocess
import tempfile
import shutil
import time


def run_code_in_sandbox(code, input_data="", max_time=8, max_memory_mb=256):
    temp_dir = tempfile.mkdtemp(prefix="sandbox_")
    try:
        code_file = f"{temp_dir}/solution.py"
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(code)

        started = time.perf_counter()
        try:
            proc = subprocess.Popen(
                ["python3", code_file],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=temp_dir,
            )
            stdout, stderr = proc.communicate(
                input=input_data or "",
                timeout=max_time,
            )
            timed_out = False
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            timed_out = True

        return {
            "success": proc.returncode == 0 and not timed_out,
            "output": stdout,
            "error": stderr,
            "execution_time": round(time.perf_counter() - started, 4),
            "timed_out": timed_out,
            "exit_code": proc.returncode,
            "memory_limit_mb": max_memory_mb,
            "memory_limit_enforced": False,
        }
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def run_tests(code, test_cases, max_time=8, max_memory_mb=256):
    results = []
    for i, test_case in enumerate(test_cases):
        result = run_code_in_sandbox(
            code,
            input_data=test_case.get("input", ""),
            max_time=max_time,
            max_memory_mb=max_memory_mb,
        )
        actual = result["output"].strip()
        expected = str(test_case.get("expected_output", "")).strip()
        passed = (
            result["success"]
            and not result["timed_out"]
            and actual == expected
        )
        results.append(
            {
                "test_number": i + 1,
                "input": test_case.get("input", ""),
                "expected": expected,
                "actual": actual,
                "passed": passed,
                "stderr": result["error"],
                "execution_time": result["execution_time"],
                "timed_out": result["timed_out"],
            }
        )

    passed_count = sum(r["passed"] for r in results)
    return {
        "passed": passed_count == len(results),
        "passed_count": passed_count,
        "total_count": len(results),
        "test_results": results,
    }
