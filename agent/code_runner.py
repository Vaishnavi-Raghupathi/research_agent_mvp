import subprocess
import tempfile
import os
import time # Added for wait/retry logic (optional but good practice)

# BUG FIX: Ensure both generate_code and fix_code are imported
# They are required by the functions defined here.
from agent.codegen import generate_code, fix_code


def execute_code_in_sandbox(code_string: str):
    """Runs Python code in a temp file and returns (success, output)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        tmp.write(code_string)
        path = tmp.name

    try:
        result = subprocess.run(
            [os.sys.executable, path],
            capture_output=True,
            text=True,
            timeout=15, # Increased timeout slightly for large models
            check=False # CRITICAL: Prevents Python from raising exception on return code != 0
        )

        success = (result.returncode == 0)
        output = result.stdout if success else result.stderr

    except subprocess.TimeoutExpired:
        success = False
        output = "TimeoutExpired: Code execution exceeded the 15-second limit."

    finally:
        os.remove(path)

    return success, output


def run_code_agent_loop(summary, equations, max_iters=5):
    print("--- 1/3: Generating Initial Code ---")
    current = generate_code(summary, equations)

    for i in range(1, max_iters + 1):
        print(f"\n--- Iteration {i}/{max_iters}: Executing Code ---")
        
        # Add a small delay between iterations to prevent rate-limiting in high-volume tests
        if i > 1:
            time.sleep(1) 
            
        success, output = execute_code_in_sandbox(current)

        if success:
            print("\n--- SUCCESS: Code Executed Cleanly! ---")
            return current

        # BUG FIX: Added code to show the last 5 lines of the error for visibility
        error_lines = output.strip().splitlines()
        print("\n--- ERROR FOUND (Last 5 lines) ---")
        print("\n".join(error_lines[-5:]))

        if i == max_iters:
            print("\n--- FAILED AFTER MAX ITERATIONS 💀 ---")
            return None
            
        print("\n--- FIXING CODE USING LLM ---")
        current = fix_code(current, output)

    return None # Should not be reached