"""
The Fixer Agent - Applies code fixes based on the plan
"""
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from src.tools.file_tools import read_file, write_file
from src.tools.sandbox_guard import is_path_allowed
from src.utils.logger import log_experiment, ActionType
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
    log_experiment(
        agent_name="Fixer",
        model_used="claude-sonnet-4-20250514",
        action=ActionType.FIX,
        details={
            "input_prompt": f"Fixing files in {target_dir}",
            "output_response": "Starting code fixes",
            "target_dir": target_dir
        },
        status="SUCCESS"
    )
    
    llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0)
    system_prompt = load_system_prompt()
    
    files_fixed = []
    
    # Determine context
    if test_results and test_results.get("status") == "failed":
        log_experiment(
            agent_name="Fixer",
            model_used="claude-sonnet-4-20250514",
            action=ActionType.DEBUG,
            details={
                "input_prompt": "Fixing test failures",
                "output_response": "Retry mode activated",
                "test_output": test_results.get('output', '')
            },
            status="SUCCESS"
        )
        context = f"Previous test results:\n{test_results.get('output', '')}\n\nFix the failing tests."
    else:
        context = f"Refactoring plan:\n{plan.get('plan', '')}"
    
    # Process each file from the plan
    for file_info in plan.get("details", []):
        filepath = file_info.get("file")
        if not filepath:
            continue
        
        # Security check
        if not is_path_allowed(filepath):
            log_experiment(
                agent_name="Fixer",
                model_used="claude-sonnet-4-20250514",
                action=ActionType.FIX,
                details={
                    "input_prompt": f"Attempted to access {filepath}",
                    "output_response": "Access denied - path not allowed",
                    "filepath": filepath
                },
                status="ERROR"
            )
            continue
        
        try:
            # Read current code
            current_code = read_file(filepath)
            
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
            write_file(filepath, fixed_code)
            files_fixed.append(filepath)
            log_experiment(
                agent_name="Fixer",
                model_used="gemini-2.0-flash-exp",
                action=ActionType.FIX,
                details={
                    "input_prompt": current_code[:500],
                    "output_response": fixed_code[:500],
                    "filepath": filepath
                },
                status="SUCCESS"
            )
            
        except Exception as e:
            log_experiment(
                agent_name="Fixer",
                model_used="claude-sonnet-4-20250514",
                action=ActionType.DEBUG,
                details={
                    "input_prompt": f"Attempting to fix {filepath}",
                    "output_response": f"Error: {str(e)}",
                    "error": str(e)
                },
                status="ERROR"
            )
    
    result = {
        "status": "fixed",
        "files_fixed": len(files_fixed),
        "files": files_fixed
    }
    
    log_experiment(
        agent_name="Fixer",
        model_used="gemini-2.0-flash-exp",
        action=ActionType.FIX,
        details={
            "input_prompt": f"Completed fixing {len(files_fixed)} files",
            "output_response": f"Fixed {len(files_fixed)} files successfully",
            "files_fixed": files_fixed
        },
        status="SUCCESS"
    )
    return result
