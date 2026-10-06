from __future__ import annotations
from typing import Any, Dict

PROMPT_VARIANTS = {
    "standard": "Act as a careful program-synthesis engineer. Solve the task and return only complete Python code.",
    "algorithmic": "Focus on algorithmic correctness, edge cases, complexity, and exact stdin/stdout behavior. Return only complete Python code.",
    "edge_case": "Independently solve the task while aggressively checking boundary cases and output formatting. Return only complete Python code.",
    "minimalist": "Produce the simplest correct implementation satisfying every stated requirement. Return only complete Python code.",
}

def _variant(agent: Dict[str, Any]) -> str:
    return PROMPT_VARIANTS.get(str(agent.get("prompt_variant", "standard")), PROMPT_VARIANTS["standard"])

def build_initial_prompt(problem: str, agent: Dict[str, Any]) -> str:
    return (
        f"You are {agent.get('role', 'an independent solver')} in an experimental multi-agent system.\n"
        f"{_variant(agent)}\n\nProblem:\n{problem}\n"
    )

def build_refinement_prompt(problem: str, agent: Dict[str, Any], previous_code: str,
                            feedback: str, iteration: int) -> str:
    return (
        f"You are {agent.get('role', 'an independent solver')} performing refinement iteration {iteration}.\n"
        f"{_variant(agent)}\n\n"
        "Your previous program did not fully satisfy the benchmark. Use the concrete execution feedback to diagnose and repair it.\n\n"
        f"Problem:\n{problem}\n\n"
        f"Previous program:\n~~~python\n{previous_code}\n~~~\n\n"
        f"Execution feedback:\n{feedback}\n\n"
        "Return only the revised complete Python program."
    )

def extract_code(text: str) -> str:
    text = (text or "").strip()
    fence = chr(96) * 3
    python_fence = fence + "python"
    if python_fence in text:
        return text.split(python_fence, 1)[1].split(fence, 1)[0].strip()
    if fence in text:
        return text.split(fence, 1)[1].split(fence, 1)[0].strip()
    return text

def format_feedback(execution: Dict[str, Any]) -> str:
    lines = [
        f"compiled={execution.get('compiled')}",
        f"execution_success={execution.get('execution_success')}",
        f"tests_passed={execution.get('tests_passed')}",
        f"tests_failed={execution.get('tests_failed')}",
        f"runtime_seconds={execution.get('runtime_seconds')}",
        f"exit_code={execution.get('exit_code')}",
        f"error_type={execution.get('error_type')}",
        f"error={execution.get('error') or ''}",
    ]
    for test in execution.get("test_results", []):
        lines.append(
            "test#{n}: passed={p} expected={e!r} actual={a!r}".format(
                n=test.get("test_number"), p=test.get("passed"),
                e=test.get("expected"), a=test.get("actual")
            )
        )
    return "\n".join(lines)
