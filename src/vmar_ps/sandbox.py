from __future__ import annotations

import ast
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


def _syntax_check(code: str) -> tuple[bool, Optional[str]]:
    try:
        compile(code, "<generated_program>", "exec")
        ast.parse(code)
        return True, None
    except SyntaxError as exc:
        return False, f"{exc.__class__.__name__}: {exc}"


def _base_result() -> Dict[str, Any]:
    return {
        "compiled": False,
        "execution_success": False,
        "tests_passed": 0,
        "tests_failed": 0,
        "runtime_seconds": 0.0,
        "memory_mb": None,
        "memory_limit_mb": None,
        "exit_code": None,
        "timed_out": False,
        "network_disabled": None,
        "error": None,
        "error_type": None,
        "test_results": [],
        "execution_mode": None,
    }


class SubprocessSandbox:
    mode = "subprocess"

    def __init__(self, timeout_seconds: float = 30.0, memory_limit_mb: int = 512):
        self.timeout_seconds = timeout_seconds
        self.memory_limit_mb = memory_limit_mb

    def _run_one(self, code: str, input_data: str) -> Dict[str, Any]:
        temp_dir = tempfile.mkdtemp(prefix="vmar_ps_")
        code_path = Path(temp_dir) / "solution.py"
        code_path.write_text(code, encoding="utf-8")
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"

        def limit_resources() -> None:
            try:
                import resource
                cpu_seconds = max(1, int(self.timeout_seconds) + 1)
                resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
                address_space = self.memory_limit_mb * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (address_space, address_space))
            except Exception:
                pass

        started = time.monotonic()
        proc = None
        try:
            proc = subprocess.Popen(
                ["python3", str(code_path)],
                cwd=temp_dir,
                env=env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True,
                preexec_fn=limit_resources if os.name == "posix" else None,
            )
            try:
                stdout, stderr = proc.communicate(input=input_data, timeout=self.timeout_seconds)
                timed_out = False
            except subprocess.TimeoutExpired:
                timed_out = True
                proc.kill()
                stdout, stderr = proc.communicate()
            return {
                "output": stdout or "",
                "error": stderr or ("Execution timeout" if timed_out else ""),
                "runtime_seconds": round(time.monotonic() - started, 4),
                "exit_code": proc.returncode,
                "timed_out": timed_out,
                "memory_mb": None,
                "network_disabled": False,
            }
        except Exception as exc:
            return {
                "output": "",
                "error": str(exc),
                "runtime_seconds": round(time.monotonic() - started, 4),
                "exit_code": None,
                "timed_out": False,
                "memory_mb": None,
                "network_disabled": False,
            }
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def verify(self, code: str, test_cases: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        result = _base_result()
        result["execution_mode"] = self.mode
        result["memory_limit_mb"] = self.memory_limit_mb
        result["network_disabled"] = False
        compiled, syntax_error = _syntax_check(code)
        result["compiled"] = compiled
        if not compiled:
            result["error"] = syntax_error
            result["error_type"] = "syntax_error"
            return result

        tests = list(test_cases)
        for index, test in enumerate(tests, start=1):
            run = self._run_one(code, str(test.get("input", "")))
            expected = str(test.get("expected_output", "")).strip()
            actual = str(run["output"]).strip()
            passed = run["exit_code"] == 0 and not run["timed_out"] and actual == expected
            result["runtime_seconds"] += run["runtime_seconds"]
            result["test_results"].append({
                "test_number": index,
                "input": str(test.get("input", "")),
                "expected": expected,
                "actual": actual,
                "passed": passed,
                "execution_error": run["error"],
                "exit_code": run["exit_code"],
                "runtime_seconds": run["runtime_seconds"],
                "timed_out": run["timed_out"],
            })
            if passed:
                result["tests_passed"] += 1
            else:
                result["tests_failed"] += 1
                result["error"] = run["error"] or "Output mismatch"
                result["exit_code"] = run["exit_code"]
                result["timed_out"] = run["timed_out"]
                if run["timed_out"]:
                    result["error_type"] = "timeout"

        result["runtime_seconds"] = round(result["runtime_seconds"], 4)
        result["execution_success"] = result["tests_failed"] == 0 and bool(tests)
        if not result["execution_success"] and result["error_type"] is None:
            result["error_type"] = "wrong_output" if result["compiled"] else "execution_failure"
        if not tests:
            result["error"] = "No visible test cases configured."
            result["error_type"] = "sandbox_failure"
            result["execution_success"] = False
        return result


class DockerSandbox:
    mode = "docker"

    def __init__(self, timeout_seconds: float = 30.0, memory_limit_mb: int = 512,
                 image: str = "python:3.12-slim"):
        import docker
        self.client = docker.from_env()
        self.client.ping()
        self.timeout_seconds = timeout_seconds
        self.memory_limit_mb = memory_limit_mb
        self.image = image

    def _run_one(self, code: str, input_data: str) -> Dict[str, Any]:
        temp_dir = tempfile.mkdtemp(prefix="vmar_ps_docker_")
        code_path = Path(temp_dir) / "solution.py"
        code_path.write_text(code, encoding="utf-8")
        container = None
        started = time.monotonic()
        timed_out = False
        try:
            container = self.client.containers.create(
                self.image,
                command=["python", "/sandbox/solution.py"],
                stdin_open=True,
                tty=False,
                detach=True,
                mem_limit=f"{self.memory_limit_mb}m",
                pids_limit=64,
                network_disabled=True,
                read_only=True,
                cap_drop=["ALL"],
                security_opt=["no-new-privileges:true"],
                tmpfs={"/tmp": "rw,noexec,nosuid,size=64m"},
                volumes={temp_dir: {"bind": "/sandbox", "mode": "ro"}},
                environment={"PYTHONDONTWRITEBYTECODE": "1"},
            )
            container.start()
            sock = container.attach_socket(params={"stdin": 1, "stdout": 1, "stderr": 1})
            try:
                if input_data:
                    sock._sock.sendall(input_data.encode("utf-8"))
                try:
                    sock._sock.shutdown(2)
                except Exception:
                    pass
            finally:
                sock.close()

            try:
                container.wait(timeout=int(self.timeout_seconds))
            except Exception:
                timed_out = True
                try:
                    container.kill()
                except Exception:
                    pass

            runtime = time.monotonic() - started
            stdout = container.logs(stdout=True, stderr=False).decode("utf-8", errors="replace")
            stderr = container.logs(stdout=False, stderr=True).decode("utf-8", errors="replace")
            exit_code = int(container.attrs.get("State", {}).get("ExitCode", 1) or 0)
            return {
                "output": stdout,
                "error": stderr or ("Execution timeout" if timed_out else ""),
                "runtime_seconds": round(runtime, 4),
                "exit_code": exit_code,
                "timed_out": timed_out,
                "memory_mb": None,
                "network_disabled": True,
            }
        except Exception as exc:
            return {
                "output": "",
                "error": str(exc),
                "runtime_seconds": round(time.monotonic() - started, 4),
                "exit_code": None,
                "timed_out": False,
                "memory_mb": None,
                "network_disabled": True,
            }
        finally:
            if container is not None:
                try:
                    container.remove(force=True)
                except Exception:
                    pass
            shutil.rmtree(temp_dir, ignore_errors=True)

    def verify(self, code: str, test_cases: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        result = _base_result()
        result["execution_mode"] = self.mode
        result["memory_limit_mb"] = self.memory_limit_mb
        result["network_disabled"] = True
        compiled, syntax_error = _syntax_check(code)
        result["compiled"] = compiled
        if not compiled:
            result["error"] = syntax_error
            result["error_type"] = "syntax_error"
            return result

        tests = list(test_cases)
        for index, test in enumerate(tests, start=1):
            run = self._run_one(code, str(test.get("input", "")))
            expected = str(test.get("expected_output", "")).strip()
            actual = str(run["output"]).strip()
            passed = run["exit_code"] == 0 and not run["timed_out"] and actual == expected
            result["runtime_seconds"] += run["runtime_seconds"]
            result["test_results"].append({
                "test_number": index,
                "input": str(test.get("input", "")),
                "expected": expected,
                "actual": actual,
                "passed": passed,
                "execution_error": run["error"],
                "exit_code": run["exit_code"],
                "runtime_seconds": run["runtime_seconds"],
                "timed_out": run["timed_out"],
            })
            if passed:
                result["tests_passed"] += 1
            else:
                result["tests_failed"] += 1
                result["error"] = run["error"] or "Output mismatch"
                result["exit_code"] = run["exit_code"]
                result["timed_out"] = run["timed_out"]
                if run["timed_out"]:
                    result["error_type"] = "timeout"

        result["runtime_seconds"] = round(result["runtime_seconds"], 4)
        result["execution_success"] = result["tests_failed"] == 0 and bool(tests)
        if not result["execution_success"] and result["error_type"] is None:
            result["error_type"] = "wrong_output"
        if not tests:
            result["error"] = "No visible test cases configured."
            result["error_type"] = "sandbox_failure"
            result["execution_success"] = False
        return result


def build_sandbox(config: Dict[str, Any]):
    execution = config.get("execution", {})
    mode = str(execution.get("mode", "auto")).lower()
    timeout = float(execution.get("timeout_seconds", 30))
    memory = int(execution.get("memory_limit_mb", 512))
    image = str(execution.get("docker_image", "python:3.12-slim"))
    if mode in {"docker", "auto"}:
        try:
            return DockerSandbox(timeout_seconds=timeout, memory_limit_mb=memory, image=image)
        except Exception:
            if mode == "docker":
                raise
    return SubprocessSandbox(timeout_seconds=timeout, memory_limit_mb=memory)
