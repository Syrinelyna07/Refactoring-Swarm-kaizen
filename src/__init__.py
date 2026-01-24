"""
The Refactoring Swarm - Multi-Agent Code Refactoring System

Modules:
  - agents: Les 3 agents (Auditor, Fixer, Judge)
  - orchestrator: Graphe LangGraph et orchestration
  - utils: Logging et utilitaires
"""

__version__ = "1.0.0"
__author__ = "Refactoring Swarm Team"

from . import agents
from . import orchestrator
from . import utils

__all__ = ["agents", "orchestrator", "utils"]
