"""ReAct Docker Sandbox: 24 agents × 10 solutions = 240 total"""

import json
import docker
from api_client import call_model
from sandbox import run_code_in_sandbox as run_code_subprocess

def load_config():
    with open("config.json") as f:
        return json.load(f)

def extract_code(text):
    if "```python" in text:
        return text.split("```python")[1].split("```")[0].strip()
    elif "```" in text:
        return text.split("```")[1].split("```")[0].strip()
    return text.strip()

def create_react_prompt(problem, previous_code=None, previous_error=None, iteration=1):
    if iteration == 1:
        return f"""Use ReAct to solve:

- Reasoning: think about problem
- Action: write code
- Observation: test result
Repeat until solved.

Problem: {problem}

Provide complete Python code that reads from stdin and prints to stdout."""
    else:
        return f"""Use ReAct to solve (Iteration {iteration}):

Previous attempt failed. Fix the code based on the error.

Problem: {problem}

Previous code:
```python
{previous_code}
```

Previous error:
{previous_error}

Provide complete Python code that reads from stdin and prints to stdout."""

def call_api(agent_config, problem, previous_code=None, previous_error=None, iteration=1):
    model = agent_config.get("model", "")
    api_key = agent_config.get("key", "")
    prompt = create_react_prompt(problem, previous_code, previous_error, iteration)
    result = call_model(model, prompt, api_key)
    if result.get("success"):
        return extract_code(result.get("output", ""))
    return f"# Error: {result.get('error', 'Unknown error')}"

def react_loop(agent_config, problem, test_cases=None, max_iterations=3, use_docker=False, docker_client=None, agent_id="", run_code_subprocess=None):
    """ReAct loop: iterate with error feedback until success or max iterations"""
    history = []
    if test_cases is None:
        test_cases = []
    
    for iteration in range(1, max_iterations + 1):
        # Get previous attempt info
        previous_code = None
        previous_error = None
        if history:
            previous_code = history[-1]["code"]
            if not history[-1]["sandbox_result"]["success"]:
                previous_error = history[-1]["sandbox_result"]["error"]
        
        # Call API
        code = call_api(agent_config, problem, previous_code, previous_error, iteration)
        
        # Run in sandbox with test cases
        if use_docker and docker_client:
            # برای Docker هم باید input بدهیم
            if test_cases:
                test_input = test_cases[0].get("input", "")
                sandbox_result = run_in_docker_sandbox(docker_client, agent_id, code, test_input)
            else:
                sandbox_result = run_in_docker_sandbox(docker_client, agent_id, code)
        else:
            # استفاده از subprocess با input
            if test_cases:
                test_input = test_cases[0].get("input", "")
                sandbox_result = run_code_subprocess(code, input_data=test_input, max_time=30, max_memory_mb=512)
            else:
                sandbox_result = run_code_subprocess(code, input_data="", max_time=30, max_memory_mb=512)
            
            sandbox_result = {
                "success": sandbox_result["success"],
                "output": sandbox_result["output"],
                "error": sandbox_result["error"],
                "execution_time": sandbox_result["execution_time"]
            }
        
        attempt = {
            "iteration": iteration,
            "code": code,
            "sandbox_result": sandbox_result
        }
        history.append(attempt)
        
        # Stop early if successful
        if sandbox_result["success"]:
            break
    
    return history

def select_best_solution(history):
    """Select first successful solution, or last attempt if none successful"""
    for attempt in history:
        if attempt["sandbox_result"] and attempt["sandbox_result"]["success"]:
            return attempt
    return history[-1] if history else None

def run_in_docker_sandbox(docker_client, agent_id, code, input_data=""):
    container_name = f"sandbox_{agent_id}"
    import tempfile
    import os
    import shutil
    import time
    temp_dir = None
    container = None
    
    try:
        try:
            docker_client.containers.get(container_name).remove(force=True)
        except:
            pass
        
        # نوشتن کد در فایل موقت
        temp_dir = tempfile.mkdtemp(prefix="docker_sandbox_")
        code_file = os.path.join(temp_dir, "solution.py")
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(code)
        
        # تبدیل input به bytes
        input_bytes = input_data.encode("utf-8") if isinstance(input_data, str) else input_data if input_data else b""
        
        # ایجاد و اجرای container
        container = docker_client.containers.create(
            "python:3.9-slim",
            command=["python", "/sandbox/solution.py"],
            name=container_name,
            mem_limit="512m",
            network_disabled=True,
            stdin_open=True,
            volumes={temp_dir: {"bind": "/sandbox", "mode": "ro"}},
            detach=True
        )
        
        # شروع container
        container.start()
        start_time = time.time()
        timeout = 30
        
        # ارسال input به stdin و خواندن خروجی
        if input_bytes:
            # استفاده از attach برای ارسال input
            attach_socket = container.attach_socket(params={"stdin": 1, "stdout": 1, "stderr": 1})
            try:
                attach_socket._sock.sendall(input_bytes)
                attach_socket._sock.shutdown(2)  # SHUT_RDWR
            except:
                pass
            finally:
                try:
                    attach_socket.close()
                except:
                    pass
        
        # انتظار برای اتمام با timeout
        try:
            container.wait(timeout=timeout)
        except Exception:
            # Timeout یا خطای دیگر
            try:
                container.kill()
                container.wait(timeout=5)
            except:
                pass
        
        execution_time = time.time() - start_time
        
        # خواندن خروجی
        logs = container.logs(stdout=True, stderr=False)
        stderr_logs = container.logs(stdout=False, stderr=True)
        
        output = logs.decode("utf-8", errors="replace") if logs else ""
        error = stderr_logs.decode("utf-8", errors="replace") if stderr_logs else ""
        
        # Get exit code before removing container
        exit_code = 0
        if container:
            try:
                exit_code = container.attrs["State"]["ExitCode"] or 0
            except:
                exit_code = 1
        
        # حذف container
        if container:
            try:
                container.remove(force=True)
            except:
                pass
        
        # پاک کردن temp directory
        if temp_dir:
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
        
        return {
            "success": exit_code == 0,
            "output": output,
            "error": error,
            "execution_time": round(execution_time, 2)
        }
    except docker.errors.ContainerError as e:
        # Container exited with non-zero code
        output = e.stdout.decode("utf-8", errors="replace") if e.stdout else ""
        error = e.stderr.decode("utf-8", errors="replace") if e.stderr else str(e)
        
        if container:
            try:
                container.remove(force=True)
            except:
                pass
        
        if temp_dir:
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
        
        return {
            "success": False,
            "output": output,
            "error": error,
            "execution_time": 0.0
        }
    except Exception as e:
        if container:
            try:
                container.remove(force=True)
            except:
                pass
        
        if temp_dir:
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
        
        return {"success": False, "output": "", "error": str(e), "execution_time": 0.0}

def main():
    config = load_config()
    apis = config.get("apis", [])
    test_cases = config.get("test_cases", [])
    with open("problem_example.txt") as f:
        problem = f.read()
    
    print(f"Problem: {problem[:100]}...")
    print(f"Agents: {len(apis)}, Solutions per agent: 2, Total: {len(apis) * 2}\n")
    print(f"Test cases: {len(test_cases)}\n")
    
    # Try to connect to Docker, fallback to subprocess if not available
    use_docker = True
    docker_client = None
    try:
        docker_client = docker.from_env()
        docker_client.ping()  # Test connection
        print("✓ Docker connected, using Docker sandbox\n")
    except Exception as e:
        print(f"⚠️  Docker not available: {e}")
        print("⚠️  Falling back to subprocess sandbox (less isolation)\n")
        use_docker = False
    
    all_solutions = []
    
    for agent_idx, agent_config in enumerate(apis, 1):
        agent_id = agent_config.get("agent_id", f"api_{agent_idx}")
        print(f"[{agent_idx}/24] {agent_id}...")
        
        for solution_num in range(1, 2):
            print(f"  Solution {solution_num}/10...", end=" ")
            
            # Run ReAct loop
            history = react_loop(
                agent_config, 
                problem,
                test_cases=test_cases,
                max_iterations=3,
                use_docker=use_docker,
                docker_client=docker_client,
                agent_id=agent_id,
                run_code_subprocess=run_code_subprocess
            )
            
            # Select best solution
            best = select_best_solution(history)
            
            all_solutions.append({
                "agent_id": agent_id,
                "solution_number": solution_num,
                "iterations": len(history),
                "history": history,
                "code": best["code"] if best else "",
                "sandbox_result": best["sandbox_result"] if best else None
            })
            
            status = "✓" if best and best["sandbox_result"]["success"] else "✗"
            print(f"({len(history)} iter) {status}")
    
    # Calculate iteration statistics
    total_iterations = sum(s["iterations"] for s in all_solutions)
    avg_iterations = total_iterations / len(all_solutions) if all_solutions else 0
    
    results = {
        "total_solutions": len(all_solutions),
        "total_agents": len(apis),
        "solutions_per_agent": 2,
        "total_iterations": total_iterations,
        "avg_iterations_per_solution": round(avg_iterations, 2),
        "solutions": all_solutions
    }
    
    with open("results2.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Complete! Saved {len(all_solutions)} solutions to results.json")

if __name__ == "__main__":
    main()

