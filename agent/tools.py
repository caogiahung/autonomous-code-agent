import subprocess
import re


SECURITY_PATTERNS = [
    (r'password\s*=\s*["\'].+["\']', "Hardcoded password detected"),
    (r'api_key\s*=\s*["\'].+["\']', "Hardcoded API key detected"),
    (r'secret\s*=\s*["\'].+["\']', "Hardcoded secret detected"),
    (r'eval\(', "Use of eval() — potential code injection risk"),
    (r'os\.system\(', "Use of os.system() — prefer subprocess with args list"),
]


def run_code_sandbox(code: str, timeout: int = 10) -> dict:
    """
    Execute Python code in a sandboxed subprocess.
    Returns stdout, stderr, and exit code.
    """
    try:
        result = subprocess.run(
            ["python3", "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode,
            "success": result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Execution timed out", "exit_code": -1, "success": False}
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "exit_code": -1, "success": False}


def security_scan(code: str) -> list:
    """
    Scan code for common security anti-patterns.
    Returns list of warnings.
    """
    warnings = []
    for pattern, message in SECURITY_PATTERNS:
        if re.search(pattern, code, re.IGNORECASE):
            warnings.append(message)
    return warnings


def summarize_issue(issue: dict) -> str:
    """Format an issue dict into a readable string for the agent."""
    return (
        f"Issue #{issue['number']}: {issue['title']}\n"
        f"Labels: {', '.join(issue['labels']) or 'none'}\n"
        f"Description:\n{issue['body'][:1000]}"
    )

def format_patch(filepath: str, code: str) -> str:
    """Format a patch summary for PR description."""
    return f"**File changed:** `{filepath}`\n\n```python\n{code[:500]}\n```"
