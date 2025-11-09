"""
sandbox.py - توابع ساده برای اجرای کد در sandbox
"""

import os
import subprocess
import tempfile
import shutil
import time
import psutil


def run_code_in_sandbox(code, input_data="", max_time=30, max_memory_mb=256):
    """اجرای کد در sandbox با input"""
    
    # ساخت دایرکتوری موقت
    temp_dir = tempfile.mkdtemp(prefix="sandbox_")
    
    try:
        # نوشتن کد در فایل
        code_file = os.path.join(temp_dir, "solution.py")
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(code)
        
        # اجرای کد
        cmd = ["python3", code_file]
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        
        start_time = time.time()
        
        try:
            # تبدیل input به bytes اگر string باشه
            input_bytes = input_data.encode("utf-8") if isinstance(input_data, str) else input_data
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                cwd=temp_dir,
                env=env
            )
            
            # مانیتورینگ
            output = ""
            error = ""
            memory_used_mb = 0.0
            timed_out = False
            
            while process.poll() is None:
                elapsed = time.time() - start_time
                
                # چک کردن timeout
                if elapsed > max_time:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except:
                        process.kill()
                    timed_out = True
                    break
                
                # چک کردن memory
                try:
                    proc_info = psutil.Process(process.pid)
                    mem_info = proc_info.memory_info()
                    current_memory = mem_info.rss / (1024 * 1024)
                    memory_used_mb = max(memory_used_mb, current_memory)
                    
                    if current_memory > max_memory_mb:
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                        except:
                            process.kill()
                        break
                except:
                    break
                
                time.sleep(0.1)
            
            # فرستادن input و خواندن خروجی
            try:
                stdout, stderr = process.communicate(input=input_bytes, timeout=max_time + 1)
                output = stdout.decode("utf-8", errors="replace") if stdout else ""
                error = stderr.decode("utf-8", errors="replace") if stderr else ""
            except subprocess.TimeoutExpired:
                process.kill()
                output = ""
                error = "Execution timeout"
            except Exception as e:
                output = ""
                error = f"Error reading output: {str(e)}"
            
            execution_time = time.time() - start_time
            
            return {
                "success": process.returncode == 0 and not timed_out,
                "output": output,
                "error": error,
                "execution_time": round(execution_time, 2),
                "memory_used_mb": round(memory_used_mb, 2),
                "timed_out": timed_out
            }
            
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "execution_time": 0.0,
                "memory_used_mb": 0.0,
                "timed_out": False
            }
    
    finally:
        # پاک کردن دایرکتوری موقت
        try:
            shutil.rmtree(temp_dir)
        except:
            pass


def run_tests(code, test_cases, max_time=30, max_memory_mb=256):
    """اجرای تست‌ها روی کد"""
    
    results = []
    passed = 0
    
    for i, test_case in enumerate(test_cases):
        test_input = test_case.get("input", "")
        expected = str(test_case.get("expected_output", "")).strip()
        
        # اجرای کد با input
        result = run_code_in_sandbox(code, test_input, max_time, max_memory_mb)
        
        actual = result["output"].strip()
        test_passed = actual == expected
        
        if test_passed:
            passed += 1
        
        results.append({
            "test_number": i + 1,
            "input": test_input,
            "expected": expected,
            "actual": actual,
            "passed": test_passed
        })
    
    return {
        "passed": passed == len(test_cases),
        "passed_count": passed,
        "total_count": len(test_cases),
        "test_results": results
    }
