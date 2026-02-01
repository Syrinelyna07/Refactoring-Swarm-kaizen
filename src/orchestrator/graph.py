"""
LangGraph Orchestration for The Refactoring Swarm
Implements the feedback loop: Auditor -> Fixer -> Judge
"""
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal
from src.agents.auditor import run_auditor
from src.agents.fixer import run_fixer
from src.agents.judge import run_judge
from src.utils.logger import log_experiment

class RefactoringState(TypedDict):
    """State shared between agents"""
    target_dir: str
    plan: dict
    fix_result: dict
    test_result: dict
    iteration: int
    status: str

MAX_ITERATIONS = 10

def auditor_node(state: RefactoringState) -> RefactoringState:
    """Run the auditor agent"""
    plan = run_auditor(state["target_dir"])
    state["plan"] = plan
    state["status"] = "audited"
    return state

def fixer_node(state: RefactoringState) -> RefactoringState:
    """Run the fixer agent"""
    fix_result = run_fixer(state["plan"], state["target_dir"], state.get("test_result"))
    state["fix_result"] = fix_result
    state["status"] = "fixed"
    return state

def judge_node(state: RefactoringState) -> RefactoringState:
    """Run the judge agent"""
    test_result = run_judge(state["target_dir"])
    state["test_result"] = test_result
    state["iteration"] = state.get("iteration", 0) + 1
    
    if test_result["status"] == "success":
        state["status"] = "complete"
    elif state["iteration"] >= MAX_ITERATIONS:
        state["status"] = "max_iterations"
        log_experiment("Orchestrator", "MAX_ITERATIONS", f"Stopped at {MAX_ITERATIONS}", "WARNING")
    else:
        state["status"] = "retry"
    
    return state

def should_continue(state: RefactoringState) -> Literal["fixer", "end"]:
    """Decide whether to retry or end"""
    if state["status"] == "retry":
        return "fixer"
    return "end"

def create_graph():
    """Create the LangGraph workflow"""
    workflow = StateGraph(RefactoringState)
    
    # Add nodes
    workflow.add_node("auditor", auditor_node)
    workflow.add_node("fixer", fixer_node)
    workflow.add_node("judge", judge_node)
    
    # Define edges
    workflow.set_entry_point("auditor")
    workflow.add_edge("auditor", "fixer")
    workflow.add_edge("fixer", "judge")
    workflow.add_conditional_edges(
        "judge",
        should_continue,
        {
            "fixer": "fixer",
            "end": END
        }
    )
    
    return workflow.compile()

def run_refactoring_swarm(target_dir: str) -> dict:
    """
    Main orchestration function
    Returns the final state after refactoring
    """
    log_experiment("Orchestrator", "START", f"Target: {target_dir}", "INFO")
    
    # Initialize state
    initial_state: RefactoringState = {
        "target_dir": target_dir,
        "plan": {},
        "fix_result": {},
        "test_result": {},
        "iteration": 0,
        "status": "init"
    }
    
    # Create and run graph
    graph = create_graph()
    final_state = graph.invoke(initial_state)
    
    log_experiment("Orchestrator", "COMPLETE", f"Status: {final_state['status']}", "SUCCESS")
    return final_state
