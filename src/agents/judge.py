"""
The Judge Agent - Runs tests and validates the code
"""
from src.tools.pytest_tool import run_pytest
from src.tools.pylint_tool import run_pylint_directory
from src.utils.logger import log_experiment, ActionType
import os

def run_judge(target_dir: str) -> dict:
    """
    Runs tests on the target directory
    Returns pass/fail status and details
    """
    log_experiment(
        agent_name="Judge",
        model_used="pytest/pylint",
        action=ActionType.ANALYSIS,
        details={
            "input_prompt": f"Testing {target_dir}",
            "output_response": "Starting tests and quality checks",
            "target_dir": target_dir
        },
        status="SUCCESS"
    )
    
    # Run pytest
    test_result = run_pytest(target_dir)
    
    # Run pylint for quality score
    pylint_result = run_pylint_directory(target_dir)
    
    # Extract score
    avg_score = 0.0
    if pylint_result.get("success"):
        avg_score = pylint_result.get("average_score", 0.0)
    
    # Determine if tests passed
    tests_passed = test_result.get("success", False)
    
    if tests_passed:
        status = "success"
        log_experiment(
            agent_name="Judge",
            model_used="pytest/pylint",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": f"Running tests on {target_dir}",
                "output_response": f"Quality: {avg_score:.2f}/10, Passed: {test_result.get('passed', 0)}",
                "quality_score": avg_score,
                "tests_passed": test_result.get('passed', 0)
            },
            status="SUCCESS"
        )
    else:
        status = "failed"
        log_experiment(
            agent_name="Judge",
            model_used="pytest/pylint",
            action=ActionType.DEBUG,
            details={
                "input_prompt": f"Running tests on {target_dir}",
                "output_response": f"Tests failed: {test_result.get('failed', 0)} failures",
                "test_output": test_result.get('output', ''),
                "failed": test_result.get('failed', 0)
            },
            status="ERROR"
        )
    
    result = {
        "status": status,
        "tests_passed": tests_passed,
        "quality_score": avg_score,
        "passed": test_result.get("passed", 0),
        "failed": test_result.get("failed", 0),
        "output": test_result.get("output", ""),
        "returncode": 0 if tests_passed else 1
    }
    
    return result
