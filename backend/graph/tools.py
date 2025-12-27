from typing import List
from langchain_core.tools import tool

# --- File System Tools (Explorer) ---
@tool
def list_files(path: str = ".") -> str:
    """List files in the given directory."""
    import os
    try:
        return str(os.listdir(path))
    except Exception as e:
        return f"Error: {e}"

@tool
def read_file(path: str) -> str:
    """Read contents of a file."""
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error: {e}"

@tool
def list_docker_containers() -> str:
    """List active docker containers."""
    import subprocess
    try:
        result = subprocess.run(["docker", "ps", "--format", "{{.ID}} {{.Image}} {{.Names}}"], capture_output=True, text=True)
        return result.stdout if result.stdout else "No active containers."
    except Exception as e:
        return f"Error listing containers: {e}"

# --- Security Tools (Auditor) ---
@tool
def run_security_scan(file_path: str) -> str:
    """Run a security scan on the specified file."""
    # Mocking a bandit scan
    import random
    if random.choice([True, False]):
        return "PASS: No security issues found."
    else:
        return f"FAIL: Potential SQL Injection found in {file_path}. Severity: High."

# --- Execution Tools (Executor) ---
@tool
def run_tests(test_file: str) -> str:
    """Run unit tests."""
    # Mocking E2B execution for now
    return "Running tests... \nTests Passed: 5/5"
