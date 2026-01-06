import subprocess
from pathlib import Path
from src.tools.sandbox_guard import is_path_allowed
import json

def run_pytest(test_dir: str) -> dict:
    """Exécute les tests avec Pytest et retourne les résultats"""
    if not is_path_allowed(test_dir):
        raise PermissionError("Forbidden path")
    path = Path(test_dir)
    if not path.exists():
        return {"success": False, "error": "Test folder not found", "passed": 0, "failed": 0}

    try:
        report_file = path / "temp_report.json"
        result = subprocess.run(
            ["pytest", str(path), "-v", "--tb=short", "--json-report", f"--json-report-file={report_file}"],
            capture_output=True,
            text=True,
            timeout=60
        )

        test_data = None
        if report_file.exists():
            with open(report_file, "r") as f:
                test_data = json.load(f)
            report_file.unlink()

        passed = failed = 0
        for line in result.stdout.split("\n"):
            if " passed" in line:
                try:
                    passed = int(line.split()[0])
                except: pass
            if " failed" in line:
                try:
                    failed = int(line.split()[0])
                except: pass

        success = result.returncode == 0
        return {"success": success, "passed": passed, "failed": failed, "output": result.stdout, "errors": result.stderr, "test_data": test_data}

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout", "passed": 0, "failed": 0}
    except Exception as e:
        return {"success": False, "error": str(e), "passed": 0, "failed": 0}
