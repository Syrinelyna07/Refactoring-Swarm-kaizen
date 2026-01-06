import subprocess
import json
from src.tools.sandbox_guard import is_path_allowed
from pathlib import Path

def run_pylint(file_path: str) -> dict:
    """Exécute pylint sur un fichier avec sortie JSON"""
    if not is_path_allowed(file_path):
        raise PermissionError("Forbidden path")
    path = Path(file_path)
    if not path.exists():
        return {"success": False, "error": "File not found", "score": 0.0, "messages": []}

    try:
        result = subprocess.run(
            ["pylint", str(path), "--output-format=json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        messages = []
        if result.stdout:
            try:
                messages = json.loads(result.stdout)
            except json.JSONDecodeError:
                pass

        score = 0.0
        for line in result.stdout.split("\n"):
            if "rated at" in line:
                try:
                    score = float(line.split("rated at")[1].split("/")[0].strip())
                except:
                    pass

        return {"success": True, "score": score, "messages": messages, "file": str(file_path)}

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout", "score": 0.0, "messages": []}
    except Exception as e:
        return {"success": False, "error": str(e), "score": 0.0, "messages": []}

def run_pylint_directory(directory: str) -> dict:
    """Exécute pylint sur tous les fichiers Python d'un dossier"""
    from src.tools.file_tools import read_file
    from pathlib import Path

    dir_path = Path(directory)
    python_files = list(dir_path.rglob("*.py"))
    if not python_files:
        return {"success": False, "error": "No Python files", "average_score": 0.0, "files": []}

    results = []
    total_score = 0.0
    for file in python_files:
        res = run_pylint(file)
        results.append(res)
        if res["success"]:
            total_score += res["score"]

    avg_score = total_score / len(python_files)
    return {"success": True, "average_score": avg_score, "total_files": len(python_files), "files": results}
