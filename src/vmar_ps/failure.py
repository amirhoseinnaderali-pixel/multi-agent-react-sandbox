from __future__ import annotations
from typing import Any, Dict

def classify_failure(execution: Dict[str, Any]) -> str | None:
    if execution.get("execution_success") and execution.get("tests_failed", 0) == 0:
        return None
    if execution.get("model_error"):
        return "model_api_failure"
    if not execution.get("compiled", True):
        return "syntax_error"
    error = str(execution.get("error") or "").lower()
    if execution.get("timed_out") or "timeout" in error:
        return "timeout"
    if "memory" in error or "out of memory" in error:
        return "memory_failure"
    if execution.get("exit_code") not in (0, None):
        return "runtime_error"
    if execution.get("execution_success") and execution.get("tests_failed", 0) > 0:
        return "wrong_output"
    return "execution_failure"

def classify_generation_error(error: str) -> str:
    text = error.lower()
    if any(token in text for token in ("quota", "rate limit", "resource_exhausted")):
        return "model_api_failure"
    return "generation_failure"
