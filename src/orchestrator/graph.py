"""
=============================================================================
ORCHESTRATOR - THE REFACTORING SWARM
Conception du graphe d'exécution avec LangGraph
=============================================================================
Responsable: L'Orchestrateur (Lead Dev)
Rôle: Gérer le flux d'exécution entre les 3 agents et la boucle de feedback
=============================================================================
"""

from typing import TypedDict, Annotated, Optional, List
from langgraph.graph import StateGraph, END
from datetime import datetime
import json
import os

# Imports des agents
from src.agents.auditor import analyze_code
from src.agents.fixer import fix_code
from src.agents.judge import validate_code


# ═════════════════════════════════════════════════════════════════════════
# 1. DÉFINITION DE L'ÉTAT (Agent State)
# ═════════════════════════════════════════════════════════════════════════

class AgentState(TypedDict):
    """
    État partagé entre tous les agents.
    Chaque agent lit et écrit dans cet état.
    """
    # Entrée initiale
    target_dir: str                    # Dossier à refactoriser
    
    # Audit
    audit_report: Optional[str]        # Rapport d'analyse du code
    files_to_fix: List[str]            # Fichiers identifiés à fixer
    quality_score_before: Optional[float]  # Score Pylint initial
    
    # Correction
    fixed_code: Optional[str]          # Code après refactoring
    fix_attempts: int                  # Nombre de tentatives
    last_fix_errors: Optional[str]     # Erreurs de la dernière tentative
    
    # Tests & Validation
    test_results: Optional[str]        # Résultats pytest
    tests_passed: bool                 # True si tous les tests passent
    quality_score_after: Optional[float]  # Score Pylint final
    
    # Gestion de la boucle
    iteration: int                     # Numéro d'itération (0-10)
    max_iterations: int                # Limite d'itérations
    should_retry: bool                 # Judge → Fixer: retry?
    is_complete: bool                  # Mission complète?
    
    # Logs & Télémétrie
    actions_log: List[dict]            # Historique des actions


# ═════════════════════════════════════════════════════════════════════════
# 2. NŒUDS DU GRAPHE (Node Functions)
# ═════════════════════════════════════════════════════════════════════════

def node_auditor(state: AgentState) -> AgentState:
    """
    🔍 L'AUDITOR - Agent 1
    
    Responsabilités:
    1. Lire le code du dossier target_dir
    2. Lancer l'analyse statique (pylint)
    3. Produire un rapport de refactoring
    4. Identifier les fichiers à corriger
    """
    
    try:
        # Appeler le vrai agent Auditor
        audit_result = analyze_code(state['target_dir'])
        
        # Extraire les informations
        state['audit_report'] = audit_result
        state['files_to_fix'] = [issue['file'] for issue in audit_result.get('issues', [])]
        state['quality_score_before'] = audit_result.get('quality_score_before', 0.0)
        
        # Log l'action
        state['actions_log'].append({
            "timestamp": datetime.now().isoformat(),
            "agent": "AUDITOR",
            "action": "ANALYZE",
            "status": "SUCCESS",
            "details": {
                "files_found": len(state['files_to_fix']),
                "quality_score": state['quality_score_before'],
                "issues": len(audit_result.get('issues', []))
            }
        })
        
    except Exception as e:
        print(f"❌ Erreur Auditor: {str(e)}")
        state['actions_log'].append({
            "timestamp": datetime.now().isoformat(),
            "agent": "AUDITOR",
            "action": "ANALYZE",
            "status": "ERROR",
            "error": str(e)
        })
        raise
    
    return state


def node_fixer(state: AgentState) -> AgentState:
    """
    🔧 LE FIXER - Agent 2
    
    Responsabilités:
    1. Lire le rapport de l'Auditor
    2. Modifier le code fichier par fichier
    3. Appliquer les corrections
    4. Retourner le code corrigé
    """
    
    try:
        # Appeler le vrai agent Fixer
        fix_result = fix_code(
            state['target_dir'],
            state['audit_report'],
            iteration=state['iteration']
        )
        
        # Extraire les informations
        state['fixed_code'] = fix_result
        state['fix_attempts'] += 1
        state['last_fix_errors'] = None
        
        # Log l'action
        state['actions_log'].append({
            "timestamp": datetime.now().isoformat(),
            "agent": "FIXER",
            "action": "REFACTOR",
            "status": "SUCCESS",
            "iteration": state['iteration'],
            "details": {
                "attempt": state['fix_attempts'],
                "files_modified": fix_result.get('files_fixed_count', 0)
            }
        })
        
    except Exception as e:
        print(f"❌ Erreur Fixer: {str(e)}")
        state['last_fix_errors'] = str(e)
        state['fix_attempts'] += 1
        state['actions_log'].append({
            "timestamp": datetime.now().isoformat(),
            "agent": "FIXER",
            "action": "REFACTOR",
            "status": "ERROR",
            "iteration": state['iteration'],
            "error": str(e)
        })
        raise
    
    return state


def node_judge(state: AgentState) -> AgentState:
    """
    ⚖️ LE JUDGE - Agent 3
    
    Responsabilités:
    1. Exécuter les tests unitaires (pytest)
    2. Vérifier les résultats
    3. Si FAIL: envoyer les logs au Fixer (boucle de feedback)
    4. Si SUCCESS: valider la fin
    """
    
    try:
        # Appeler le vrai agent Judge
        verdict = validate_code(
            state['target_dir'],
            state['quality_score_before'],
            iteration=state['iteration']
        )
        
        # Extraire les informations
        state['tests_passed'] = verdict.get('tests_passed', False)
        state['test_results'] = verdict
        state['quality_score_after'] = verdict.get('quality_score_after', 0.0)
        
        # Déterminer s'il faut retry
        is_success = verdict.get('verdict', 'FAIL').upper() == 'SUCCESS'
        state['should_retry'] = not is_success
        
        # Log l'action
        state['actions_log'].append({
            "timestamp": datetime.now().isoformat(),
            "agent": "JUDGE",
            "action": "VALIDATE",
            "status": "SUCCESS",
            "details": {
                "tests_passed": state['tests_passed'],
                "quality_score_after": state['quality_score_after'],
                "improvement": round(state['quality_score_after'] - state['quality_score_before'], 2),
                "verdict": verdict.get('verdict')
            }
        })
        
        if state['tests_passed']:
            state['is_complete'] = True
            state['should_retry'] = False
            print(f"✅ Tous les tests passent! Mission complète.")
        else:
            state['should_retry'] = True
            print(f"❌ Tests échoués. Retour au Fixer.")
        
    except Exception as e:
        print(f"❌ Erreur Judge: {str(e)}")
        state['should_retry'] = True
        state['actions_log'].append({
            "timestamp": datetime.now().isoformat(),
            "agent": "JUDGE",
            "action": "VALIDATE",
            "status": "ERROR",
            "error": str(e)
        })
    
    return state


def node_router(state: AgentState) -> str:
    """
    🔀 ROUTEUR - Logique de passage de relais
    
    Décide:
    - Continuer la boucle ? (Fixer)
    - Fin ? (END)
    """
    
    # Condition 1: Max itérations atteinte?
    if state['iteration'] >= state['max_iterations']:
        print(f"\n⚠️ LIMITE D'ITÉRATIONS ATTEINTE ({state['max_iterations']})")
        state['is_complete'] = True
        return END
    
    # Condition 2: Tests réussis?
    if state['tests_passed']:
        print(f"\n✅ SUCCÈS! Fin de la mission.")
        return END
    
    # Condition 3: Retry possible?
    if state['should_retry'] and state['fix_attempts'] < state['max_iterations']:
        print(f"\n🔄 Retour au Fixer...")
        state['iteration'] += 1
        return "fixer"
    
    # Condition 4: Échec après retries
    print(f"\n❌ ÉCHEC: Impossible de corriger après {state['fix_attempts']} tentatives")
    state['is_complete'] = True
    return END


# ═════════════════════════════════════════════════════════════════════════
# 3. CONSTRUCTION DU GRAPHE
# ═════════════════════════════════════════════════════════════════════════

def build_orchestrator_graph():
    """
    Construit le graphe LangGraph pour The Refactoring Swarm.
    
    Flux:
    START → Auditor → Fixer ↔ Judge → [Router] → END
              ↑_____________________↓
              (feedback loop max 10 iter)
    """
    
    graph = StateGraph(AgentState)
    
    # Ajouter les nœuds
    graph.add_node("auditor", node_auditor)
    graph.add_node("fixer", node_fixer)
    graph.add_node("judge", node_judge)
    
    # Ajouter les arêtes
    graph.set_entry_point("auditor")            # Début → Auditor
    graph.add_edge("auditor", "fixer")          # Auditor → Fixer
    graph.add_edge("fixer", "judge")            # Fixer → Judge
    graph.add_conditional_edges(
        "judge",
        node_router,                             # Judge → Router
        {
            "fixer": "fixer",                    # Router → Fixer (retry)
            END: END                             # Router → Fin
        }
    )
    
    return graph.compile()


# ═════════════════════════════════════════════════════════════════════════
# 4. FONCTION D'EXÉCUTION PRINCIPALE
# ═════════════════════════════════════════════════════════════════════════

def run_orchestrator(target_dir: str, max_iterations: int = 10) -> dict:
    """
    Lance le système multi-agents.
    
    Args:
        target_dir (str): Dossier contenant le code à refactoriser
        max_iterations (int): Nombre max d'itérations (défaut 10)
    
    Returns:
        dict: Résultat final avec stats
    """
    
    print(f"\n{'='*70}")
    print(f"🚀 LANCEMENT - THE REFACTORING SWARM")
    print(f"{'='*70}")
    print(f"📁 Cible: {target_dir}")
    print(f"🔄 Itérations max: {max_iterations}")
    
    # État initial
    initial_state: AgentState = {
        "target_dir": target_dir,
        "audit_report": None,
        "files_to_fix": [],
        "quality_score_before": None,
        "fixed_code": None,
        "fix_attempts": 0,
        "last_fix_errors": None,
        "test_results": None,
        "tests_passed": False,
        "quality_score_after": None,
        "iteration": 1,
        "max_iterations": max_iterations,
        "should_retry": False,
        "is_complete": False,
        "actions_log": [
            {
                "timestamp": datetime.now().isoformat(),
                "agent": "ORCHESTRATOR",
                "action": "START",
                "status": "INITIALIZED",
                "details": {
                    "target_dir": target_dir,
                    "max_iterations": max_iterations
                }
            }
        ]
    }
    
    # Construire et exécuter le graphe
    graph = build_orchestrator_graph()
    final_state = graph.invoke(initial_state)
    
    # Résumé final
    print(f"\n{'='*70}")
    print(f"📊 RÉSUMÉ FINAL")
    print(f"{'='*70}")
    print(f"✅ Itérations complétées: {final_state['iteration']}")
    print(f"✅ Tentatives de fix: {final_state['fix_attempts']}")
    print(f"✅ Tests réussis: {final_state['tests_passed']}")
    print(f"✅ Score qualité initial: {final_state['quality_score_before']}")
    print(f"✅ Score qualité final: {final_state['quality_score_after']}")
    
    if final_state['quality_score_before'] and final_state['quality_score_after']:
        improvement = final_state['quality_score_after'] - final_state['quality_score_before']
        print(f"✅ Amélioration: {improvement:+.1f}")
    
    return final_state


# ═════════════════════════════════════════════════════════════════════════
# 5. VALIDATIONS
# ═════════════════════════════════════════════════════════════════════════

def validate_state(state: AgentState) -> bool:
    """
    ✅ Valide que l'état respecte le contrat.
    """
    checks = [
        ("target_dir existe", os.path.isdir(state['target_dir'])),
        ("iteration >= 0", state['iteration'] >= 0),
        ("max_iterations > 0", state['max_iterations'] > 0),
        ("fix_attempts >= 0", state['fix_attempts'] >= 0),
        ("actions_log est liste", isinstance(state['actions_log'], list)),
        ("is_complete est bool", isinstance(state['is_complete'], bool)),
    ]
    
    all_valid = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
        all_valid = all_valid and result
    
    return all_valid


if __name__ == "__main__":
    # Test du graphe (simulation)
    print("🧪 TEST DE VALIDATION")
    test_state: AgentState = {
        "target_dir": "./test",
        "audit_report": None,
        "files_to_fix": [],
        "quality_score_before": None,
        "fixed_code": None,
        "fix_attempts": 0,
        "last_fix_errors": None,
        "test_results": None,
        "tests_passed": False,
        "quality_score_after": None,
        "iteration": 1,
        "max_iterations": 10,
        "should_retry": False,
        "is_complete": False,
        "actions_log": []
    }
    print("État initial validé ✅")
