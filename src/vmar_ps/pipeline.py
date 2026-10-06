from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable

from .config import benchmark_digest, experiment_id, resolve_agents
from .diversity import summarize as diversity_summary
from .failure import classify_failure, classify_generation_error
from .llm import build_client
from .metrics import summarize_problem
from .prompts import build_initial_prompt, build_refinement_prompt, extract_code, format_feedback
from .sandbox import build_sandbox

class BudgetTracker:
    def __init__(self, config: Dict[str, Any]):
        budget = config.get("budget", {})
        self.max_model_calls = budget.get("model_calls")
        self.max_wall_clock = budget.get("wall_clock_seconds")
        self.started = time.monotonic()
        self.model_calls = 0

    def can_continue(self) -> bool:
        if self.max_model_calls is not None and self.model_calls >= int(self.max_model_calls):
            return False
        if self.max_wall_clock is not None and time.monotonic() - self.started >= float(self.max_wall_clock):
            return False
        return True

    def reserve_model_call(self) -> bool:
        if not self.can_continue():
            return False
        self.model_calls += 1
        return True

def load_benchmark(path: str | Path) -> list[Dict[str, Any]]:
    path = Path(path)
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw if isinstance(raw, list) else raw.get("problems", [])

class ExperimentRunner:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.problems = load_benchmark(config["benchmark"])
        self.benchmark_digest = benchmark_digest(config["benchmark"])
        self.experiment_id = experiment_id(config, self.benchmark_digest)
        self.sandbox = build_sandbox(config)

    def run(self) -> list[Dict[str, Any]]:
        return [self.run_problem(problem) for problem in self.problems]

    def run_problem(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        started = time.monotonic()
        budget = BudgetTracker(self.config)
        agents = resolve_agents(self.config)
        method = str(self.config.get("method", "vmar_ps"))
        max_rounds = int(self.config.get("max_refinement_rounds", 0))
        iterative = method in {"single_agent_react", "vmar_ps"} and max_rounds > 0
        selection_strategy = str(self.config.get("selection_strategy", "first_verified"))

        attempts: list[Dict[str, Any]] = []
        candidates: list[Dict[str, Any]] = []
        api_failures = 0

        for agent in agents:
            if not budget.can_continue():
                break

            agent_id = str(agent.get("agent_id"))
            provider = str(agent.get("provider", "google"))
            model = str(agent.get("model", ""))
            prompt_variant = str(agent.get("prompt_variant", "standard"))
            temperature = float(agent.get("temperature", 0.2))
            max_output_tokens = int(agent.get("max_output_tokens", 2048))
            input_cost_per_1k = agent.get("input_cost_per_1k_usd")
            output_cost_per_1k = agent.get("output_cost_per_1k_usd")
            client = None
            agent_attempts: list[Dict[str, Any]] = []
            previous_code = None
            previous_execution: Dict[str, Any] | None = None
            total_attempts_allowed = 1 + max_rounds if iterative else 1

            for iteration in range(total_attempts_allowed):
                if not budget.reserve_model_call():
                    break

                if client is None:
                    try:
                        client = build_client(agent)
                    except Exception as exc:
                        api_failures += 1
                        execution = {
                            "model_error": True, "compiled": False, "execution_success": False,
                            "tests_passed": 0, "tests_failed": len(problem.get("tests", [])),
                            "runtime_seconds": 0.0, "error": str(exc),
                            "error_type": "model_api_failure", "test_results": [],
                        }
                        attempt = {
                            "attempt_id": f"{problem['id']}:{agent_id}:{iteration}",
                            "iteration": iteration, "agent_id": agent_id, "model": model,
                            "provider": provider, "prompt_variant": prompt_variant,
                            "generated_code": "", "execution_result": execution, "feedback": "",
                            "revised": iteration > 0,
                            "previous_success": agent_attempts[-1]["execution_result"].get("execution_success")
                            if agent_attempts else None,
                            "model_call_index": budget.model_calls,
                            "input_tokens": None, "output_tokens": None, "total_tokens": None,
                            "cost_usd": None,
                        }
                        attempts.append(attempt)
                        agent_attempts.append(attempt)
                        break

                if iteration == 0:
                    prompt = build_initial_prompt(str(problem.get("prompt", "")), agent)
                else:
                    prompt = build_refinement_prompt(
                        str(problem.get("prompt", "")), agent, previous_code or "",
                        format_feedback(previous_execution or {}), iteration,
                    )

                response = client.generate(
                    model=model, prompt=prompt, temperature=temperature,
                    max_output_tokens=max_output_tokens,
                )

                if not response.success:
                    api_failures += 1
                    execution = {
                        "model_error": True, "compiled": False, "execution_success": False,
                        "tests_passed": 0, "tests_failed": len(problem.get("tests", [])),
                        "runtime_seconds": 0.0, "error": response.error,
                        "error_type": classify_generation_error(response.error or ""),
                        "test_results": [],
                    }
                    code = ""
                    cost_usd = None
                else:
                    code = extract_code(response.text)
                    execution = self.sandbox.verify(code, problem.get("tests", []))
                    execution["error_type"] = classify_failure(execution)
                    cost_usd = None
                    if response.input_tokens is not None and response.output_tokens is not None:
                        if input_cost_per_1k is not None and output_cost_per_1k is not None:
                            cost_usd = (
                                response.input_tokens / 1000.0 * float(input_cost_per_1k)
                                + response.output_tokens / 1000.0 * float(output_cost_per_1k)
                            )

                feedback = format_feedback(execution)
                previous_success = (
                    agent_attempts[-1]["execution_result"].get("execution_success")
                    if agent_attempts else None
                )
                attempt = {
                    "attempt_id": f"{problem['id']}:{agent_id}:{iteration}",
                    "iteration": iteration,
                    "agent_id": agent_id,
                    "model": model,
                    "provider": provider,
                    "prompt_variant": prompt_variant,
                    "generated_code": code,
                    "execution_result": execution,
                    "feedback": feedback,
                    "revised": iteration > 0,
                    "previous_success": previous_success,
                    "model_call_index": budget.model_calls,
                    "input_tokens": response.input_tokens if response.success else None,
                    "output_tokens": response.output_tokens if response.success else None,
                    "total_tokens": response.total_tokens if response.success else None,
                    "cost_usd": cost_usd,
                }
                attempts.append(attempt)
                agent_attempts.append(attempt)
                previous_code = code
                previous_execution = execution

                if execution.get("execution_success"):
                    break

            if agent_attempts:
                first, last = agent_attempts[0], agent_attempts[-1]
                candidates.append({
                    "candidate_id": f"{problem['id']}:{agent_id}",
                    "agent_id": agent_id,
                    "model": model,
                    "provider": provider,
                    "prompt_variant": prompt_variant,
                    "first_code": first.get("generated_code", ""),
                    "first_success": bool(first.get("execution_result", {}).get("execution_success")),
                    "final_success": bool(last.get("execution_result", {}).get("execution_success")),
                    "tests_passed": int(last.get("execution_result", {}).get("tests_passed", 0)),
                    "iterations_used": len(agent_attempts) - 1,
                    "last_attempt_id": last["attempt_id"],
                })

        selected = self._select(candidates, selection_strategy)
        final_attempt = next(
            (a for a in reversed(attempts) if selected and a["attempt_id"] == selected["last_attempt_id"]),
            None,
        )
        first_pass_success = any(c["first_success"] for c in candidates)
        final_success = bool(selected and selected["final_success"])
        repaired = (not first_pass_success) and final_success and any(
            a.get("revised") for a in attempts
            if selected and a["agent_id"] == selected["agent_id"]
        )
        test_result = final_attempt["execution_result"] if final_attempt else {}

        input_tokens = sum(a.get("input_tokens") or 0 for a in attempts)
        output_tokens = sum(a.get("output_tokens") or 0 for a in attempts)
        total_tokens = sum(a.get("total_tokens") or 0 for a in attempts)
        measured_cost = [a.get("cost_usd") for a in attempts if a.get("cost_usd") is not None]

        result = {
            "schema_version": "1.0",
            "experiment_id": self.experiment_id,
            "experiment_seed": int(self.config.get("seed", 0)),
            "problem_id": problem["id"],
            "method": method,
            "benchmark": self.config["benchmark"],
            "num_agents": len(candidates),
            "configured_num_agents": int(self.config.get("num_agents", len(agents))),
            "max_refinement_rounds": max_rounds,
            "selection_strategy": selection_strategy,
            "execution_mode": getattr(self.sandbox, "mode", None),
            "attempts": attempts,
            "candidates": candidates,
            "selected_candidate_id": selected["candidate_id"] if selected else None,
            "selected_agent_id": selected["agent_id"] if selected else None,
            "selected_code": final_attempt.get("generated_code") if final_attempt else "",
            "first_pass_success": first_pass_success,
            "repair_success": repaired,
            "final_success": final_success,
            "regression_observed": any(
                a.get("revised") and a.get("previous_success") is True
                and a.get("execution_result", {}).get("execution_success") is False
                for a in attempts
            ),
            "tests_passed": int(test_result.get("tests_passed", 0)),
            "tests_failed": int(test_result.get("tests_failed", 0)),
            "error_type": test_result.get("error_type") or (
                "model_api_failure" if api_failures and not final_success else None
            ),
            "runtime_seconds": round(time.monotonic() - started, 4),
            "total_model_calls": budget.model_calls,
            "input_tokens": input_tokens or None,
            "output_tokens": output_tokens or None,
            "total_tokens": total_tokens or None,
            "cost_usd": round(sum(measured_cost), 8) if measured_cost else None,
            "iterations_used": max((a.get("iteration", 0) for a in attempts), default=0),
            "api_failures": api_failures,
            "budget_exhausted": not budget.can_continue(),
            "diversity": diversity_summary(candidates),
        }
        result["metrics"] = summarize_problem(result)
        return result

    @staticmethod
    def _select(candidates: Iterable[Dict[str, Any]], strategy: str) -> Dict[str, Any] | None:
        candidates = list(candidates)
        if not candidates:
            return None
        if strategy == "first_verified":
            for candidate in candidates:
                if candidate["final_success"]:
                    return candidate
        if strategy == "max_tests_passed":
            return max(candidates, key=lambda c: (
                c["final_success"], c["tests_passed"], -c["iterations_used"]
            ))
        if strategy == "first_candidate":
            return candidates[0]
        return max(candidates, key=lambda c: (
            c["final_success"], c["tests_passed"], -c["iterations_used"]
        ))

def write_results(results: Iterable[Dict[str, Any]], output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for result in results:
            handle.write(json.dumps(result, ensure_ascii=False) + "\n")
