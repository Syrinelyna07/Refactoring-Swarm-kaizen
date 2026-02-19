import subprocess
import json
from src.tools.sandbox_guard import is_path_allowed
from pathlib import Path
import re

def run_pylint(file_path: str) -> dict:
    """Exécute pylint sur un fichier avec sortie JSON ET score"""
    if not is_path_allowed(file_path):
        raise PermissionError("Forbidden path")
    path = Path(file_path)
    if not path.exists():
        return {"success": False, "error": "File not found", "score": 0.0, "messages": []}

    try:
        # First run: Get JSON messages
        result_json = subprocess.run(
            ["pylint", str(path), "--output-format=json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        messages = []
        if result_json.stdout:
            try:
                messages = json.loads(result_json.stdout)
            except json.JSONDecodeError:
                pass

        # Second run: Get the score (text format)
        result_score = subprocess.run(
            ["pylint", str(path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Extract score from text output
        score = 0.0
        combined_output = result_score.stdout + "\n" + result_score.stderr
        
        # Look for patterns like "Your code has been rated at 8.50/10"
        match = re.search(r'rated at ([-+]?\d*\.?\d+)/10', combined_output, re.IGNORECASE)
        if match:
            score = float(match.group(1))
        
        return {"success": True, "score": score, "messages": messages, "file": str(file_path)}

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout", "score": 0.0, "messages": []}
    except Exception as e:
        return {"success": False, "error": str(e), "score": 0.0, "messages": []}

def run_pylint_directory(directory: str) -> dict:
    """Exécute pylint sur tous les fichiers Python d'un dossier"""
    dir_path = Path(directory)
    python_files = list(dir_path.rglob("*.py"))
    
    # Filter out test files
    python_files = [f for f in python_files if not f.name.startswith("test_")]
    
    if not python_files:
        return {"success": False, "error": "No Python files", "average_score": 0.0, "files": []}

    results = []
    total_score = 0.0
    successful_files = 0
    
    for file in python_files:
        res = run_pylint(str(file))
        results.append(res)
        if res["success"]:
            total_score += res["score"]
            successful_files += 1

    # Calculate average (all files count, even with score 0)
    avg_score = total_score / len(python_files) if python_files else 0.0
    
    return {"success": True, "average_score": avg_score, "total_files": len(python_files), "files": results}
