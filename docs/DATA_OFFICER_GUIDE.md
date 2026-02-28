"""
Exemple d'utilisation du logger imposé
À utiliser dans vos agents
"""
from src.utils import log_experiment, ActionType, initialize_logger, finalize_logger

# Au début de main.py
initialize_logger()

# Dans votre agent Auditeur
log_experiment(
    agent_name="Auditor_Agent",
    model_used="gemini-2.5-flash",
    action=ActionType.ANALYSIS,
    details={
        "file_analyzed": "messy_code.py",
        "input_prompt": "Tu es un expert Python. Analyse ce code et identifie les problèmes...",
        "output_response": "J'ai détecté 3 problèmes: 1) Absence de docstrings...",
        "issues_found": 3,
        "pylint_score": 4.5
    },
    status="SUCCESS"
)

# Dans votre agent Correcteur
log_experiment(
    agent_name="Fixer_Agent",
    model_used="gemini-2.5-flash",
    action=ActionType.FIX,
    details={
        "file_modified": "messy_code.py",
        "input_prompt": "Corrige les problèmes suivants dans ce code...",
        "output_response": "J'ai corrigé le code en ajoutant des docstrings...",
        "changes_made": 5
    },
    status="SUCCESS"
)

# À la fin de main.py
finalize_logger()
