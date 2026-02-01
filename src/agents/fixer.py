"""
The Fixer Agent - Applies code fixes based on the plan
"""
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage
from src.tools.file_tools import read_file, write_file
from src.tools.sandbox_guard import validate_path
from src.utils.logger import log_experiment
import os

def load_system_prompt():
    """Load the fixer system prompt"""
    prompt_path = os.path.join("src", "prompts", "fixer.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def run_fixer(plan: dict, target_dir: str, test_results: dict = None) -> dict:
    """
    Applies fixes to code based on the plan
    If test_results provided, focuses on fixing test failures
    """
    log_experiment("Fixer", "START", f"Fixing files in {target_dir}", "INFO")
    
    llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0)
    system_prompt = load_system_prompt()
    
    files_fixed = []
    
    # Get files to fix
    files_to_fix = []
    if test_results and test_results.get("status") == "failed":
        # Focus on files with test failures
        log_experiment("Fixer", "RETRY_MODE", "Fixing test failures", "INFO")
        context = f"Previous test results:\n{test_results.get('output', '')}\n\nFix the failing tests."
    else:
        # Use original plan
        context = f"Refactoring plan:\n{plan.get('plan', '')}"
    
    # Process each file from the plan
    for file_info in plan.get("details", []):
        filepath = file_info["file"]
        
        # Security check
        if not validate_path(filepath, target_dir):
            log_experiment("Fixer", "SECURITY_BLOCK", f"Blocked: {filepath}", "ERROR")
            continue
        
        # Read current code
        current_code = read_file(filepath)
        if not current_code:
            continue
        
        # Ask LLM to fix
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"{context}\n\nFile: {filepath}\n\nCurrent code:\n{current_code}\n\nProvide the fixed code.")
        ]
        
        response = llm.invoke(messages)
        fixed_code = response.content
        
        # Extract code from markdown if present
        if "```python" in fixed_code:
            fixed_code = fixed_code.split("```python")[1].split("```")[0].strip()
        
        # Write fixed code
        if write_file(filepath, fixed_code):
            files_fixed.append(filepath)
            log_experiment("Fixer", "FILE_FIXED", filepath, "SUCCESS")
    
    result = {
        "status": "fixed",
        "files_fixed": len(files_fixed),
        "files": files_fixed
    }
    
    log_experiment("Fixer", "COMPLETE", f"Fixed {len(files_fixed)} files", "SUCCESS")
    return result
