import subprocess
from pathlib import Path
from src.tools.sandbox_guard import is_path_allowed

def run_pytest(test_dir: str) -> dict:
    """Exécute les tests avec Pytest et retourne les résultats"""
    if not is_path_allowed(test_dir):
        raise PermissionError("Forbidden path")
    path = Path(test_dir)
    if not path.exists():
        return {"success": False, "error": "Test folder not found", "passed": 0, "failed": 0}

    try:
        result = subprocess.run(
            ["pytest", str(path), "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=60
        )

        passed = 0
        failed = 0
        output_lines = result.stdout.split("\n")
        
        for line in output_lines:
            if " passed" in line:
                try:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed":
                            passed = int(parts[i-1])
                except: 
                    pass
            if " failed" in line:
                try:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "failed":
                            failed = int(parts[i-1])
                except: 
                    pass

        success = result.returncode == 0 and failed == 0
        return {
            "success": success,
            "passed": passed,
            "failed": failed,
            "output": result.stdout,
            "errors": result.stderr,
            "returncode": result.returncode
        }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout", "passed": 0, "failed": 0}
    except Exception as e:
        return {"success": False, "error": str(e), "passed": 0, "failed": 0}
