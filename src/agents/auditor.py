"""
The Auditor Agent - Analyzes code and creates refactoring plan
"""
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage
from src.tools.code_analysis import analyze_file
from src.tools.pylint_tool import run_pylint_analysis
from src.utils.logger import log_experiment
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
    log_experiment("Auditor", "START", f"Analyzing {target_dir}", "INFO")
    
    # Find all Python files
    python_files = []
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    if not python_files:
        log_experiment("Auditor", "NO_FILES", "No Python files found", "WARNING")
        return {"status": "no_files", "plan": []}
    
    # Analyze each file
    analysis_results = []
    for filepath in python_files:
        pylint_result = run_pylint_analysis(filepath)
        analysis_results.append({
            "file": filepath,
            "pylint_score": pylint_result.get("score", 0),
            "issues": pylint_result.get("messages", [])
        })
    
    # Create refactoring plan using LLM
    llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0)
    system_prompt = load_system_prompt()
    
    analysis_summary = "\n".join([
        f"File: {r['file']}\nScore: {r['pylint_score']}/10\nIssues: {len(r['issues'])}"
        for r in analysis_results
    ])
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Analyze this code and create a refactoring plan:\n\n{analysis_summary}")
    ]
    
    response = llm.invoke(messages)
    
    plan = {
        "status": "plan_created",
        "files_analyzed": len(python_files),
        "plan": response.content,
        "details": analysis_results
    }
    
    log_experiment("Auditor", "COMPLETE", f"Analyzed {len(python_files)} files", "SUCCESS")
    return plan
