"""
The Auditor Agent - Analyzes code and creates refactoring plan
"""
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from src.tools.pylint_tool import run_pylint_directory
from src.utils.logger import log_experiment, ActionType
import os

def load_system_prompt():
    """Load the auditor system prompt"""
    prompt_path = os.path.join("src", "prompts", "auditor.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def run_auditor(target_dir: str) -> dict:
    """
    Analyzes all Python files in target directory
    Returns a refactoring plan
    """
    log_experiment(
        agent_name="Auditor",
        model_used="claude-sonnet-4-20250514",
        action=ActionType.ANALYSIS,
        details={
            "input_prompt": f"Analyzing {target_dir}",
            "output_response": "Starting code analysis",
            "target_dir": target_dir
        },
        status="SUCCESS"
    )
    
    # Run pylint on entire directory
    pylint_result = run_pylint_directory(target_dir)
    
    if not pylint_result.get("success"):
        log_experiment(
            agent_name="Auditor",
            model_used="claude-sonnet-4-20250514",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": "No files to analyze",
                "output_response": pylint_result.get("error", "Analysis failed"),
                "error": pylint_result.get("error", "Analysis failed")
            },
            status="ERROR"
        )
        return {"status": "no_files", "plan": "No Python files to analyze"}
    
    # Create refactoring plan using LLM
    llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0)
    system_prompt = load_system_prompt()
    
    # Build analysis summary
    files_info = pylint_result.get("files", [])
    analysis_summary = f"Average Quality Score: {pylint_result.get('average_score', 0):.2f}/10\n"
    analysis_summary += f"Total Files: {pylint_result.get('total_files', 0)}\n\n"
    
    for file_result in files_info[:5]:  # Limit to first 5 files for context
        analysis_summary += f"File: {file_result.get('file', 'unknown')}\n"
        analysis_summary += f"Score: {file_result.get('score', 0):.2f}/10\n"
        analysis_summary += f"Issues: {len(file_result.get('messages', []))}\n\n"
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Analyze this code and create a refactoring plan:\n\n{analysis_summary}")
    ]
    
    response = llm.invoke(messages)
    
    plan = {
        "status": "plan_created",
        "files_analyzed": pylint_result.get('total_files', 0),
        "average_score": pylint_result.get('average_score', 0),
        "plan": response.content,
        "details": files_info
    }
    
    log_experiment(
        agent_name="Auditor",
        model_used="claude-sonnet-4-20250514",
        action=ActionType.GENERATION,
        details={
            "input_prompt": analysis_summary,
            "output_response": response.content,
            "files_analyzed": plan['files_analyzed'],
            "average_score": plan['average_score']
        },
        status="SUCCESS"
    )
    return plan
