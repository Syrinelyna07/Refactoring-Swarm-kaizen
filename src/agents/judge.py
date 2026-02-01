"""
The Judge Agent - Runs tests and validates the code
"""
from src.tools.pytest_tool import run_pytest
from src.tools.pylint_tool import run_pylint_analysis
from src.utils.logger import log_experiment
import os

def run_judge(target_dir: str) -> dict:
    """
    Runs tests on the target directory
    Returns pass/fail status and details
    """
    log_experiment("Judge", "START", f"Testing {target_dir}", "INFO")
    
    # Run pytest
    test_result = run_pytest(target_dir)
    
    # Run pylint for quality score
    python_files = []
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    total_score = 0
    for filepath in python_files:
        result = run_pylint_analysis(filepath)
        total_score += result.get("score", 0)
    
    avg_score = total_score / len(python_files) if python_files else 0
    
    # Determine if tests passed
    tests_passed = test_result.get("returncode", 1) == 0
    
    if tests_passed:
        status = "success"
        log_experiment("Judge", "TESTS_PASSED", f"Quality: {avg_score:.2f}/10", "SUCCESS")
    else:
        status = "failed"
        log_experiment("Judge", "TESTS_FAILED", "Need retry", "WARNING")
    
    result = {
        "status": status,
        "tests_passed": tests_passed,
        "quality_score": avg_score,
        "output": test_result.get("output", ""),
        "returncode": test_result.get("returncode", 1)
    }
    
    return result
