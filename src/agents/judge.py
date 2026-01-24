"""
=============================================================================
AGENT JUDGE - LE VALIDATEUR
=============================================================================
Rôle: Tester et valider le code refactorisé
=============================================================================
"""

from src.tools import call_gemini, run_pytest, run_pylint, load_prompt, validate_json_output
from src.utils.logger import log_experiment, ActionType
from typing import Dict, Optional
import json


def validate_code(target_dir: str, quality_score_before: float, iteration: int = 1) -> Dict:
    """
    Le Judge valide le code refactorisé.
    
    Args:
        target_dir (str): Dossier contenant le code
        quality_score_before (float): Score avant refactoring
        iteration (int): Numéro d'itération
    
    Returns:
        Dict: Résultat de validation avec verdict
    """
    
    print(f"\n{'='*70}")
    print(f"⚖️ AGENT JUDGE - VALIDATION (Itération {iteration})")
    print(f"{'='*70}")
    
    # Étape 1: Lancer les tests
    print("🧪 Lancement pytest...")
    tests_passed, pytest_output = run_pytest(target_dir)
    print(f"   {'✅' if tests_passed else '❌'} Tests: {'PASSÉS' if tests_passed else 'ÉCHOUÉS'}")
    
    # Étape 2: Vérifier la qualité
    print("📊 Vérification pylint...")
    quality_score_after, pylint_output = run_pylint(target_dir)
    print(f"   ✅ Score pylint: {quality_score_after}/10 (avant: {quality_score_before}/10)")
    
    # Étape 3: Préparer le verdict
    print("🤖 Appel Gemini pour verdict...")
    system_prompt = load_prompt("src/prompts/judge.txt")
    
    quality_improved = quality_score_after > quality_score_before
    improvement = quality_score_after - quality_score_before
    
    user_message = f"""
Here are the validation results:

**Tests:**
- Status: {'PASSED' if tests_passed else 'FAILED'}
- Output:
{pytest_output[:1000]}

**Code Quality:**
- Score before: {quality_score_before}/10
- Score after: {quality_score_after}/10
- Improvement: {improvement:+.1f} points
- Quality improved: {quality_improved}

Based on these results, decide:
- If ANY test fails → verdict: FAIL
- If pylint score decreased → verdict: FAIL
- Else → verdict: SUCCESS

Return JSON response only.
    """
    
    # Étape 4: Appeler Gemini
    try:
        response = call_gemini(system_prompt, user_message)
        
        # Parser la réponse JSON
        verdict = validate_json_output(response)
        
        # Ajouter des données
        verdict["tests_passed"] = tests_passed
        verdict["quality_score_after"] = quality_score_after
        verdict["quality_score_before"] = quality_score_before
        verdict["improvement"] = improvement
        verdict["pytest_output"] = pytest_output[:500]
        verdict["pylint_output"] = pylint_output[:500]
        
        # Déterminer si c'est un succès
        is_success = verdict.get("verdict", "FAIL").upper() == "SUCCESS"
        
        # Log l'action
        log_experiment(
            agent_name="Judge",
            model_used="gemini-2.0-flash",
            action=ActionType.DEBUG if not tests_passed else ActionType.ANALYSIS,
            details={
                "iteration": iteration,
                "input_prompt": user_message[:500],
                "output_response": response[:500],
                "tests_passed": tests_passed,
                "quality_improvement": improvement,
                "verdict": verdict.get("verdict", "UNKNOWN")
            },
            status="SUCCESS"
        )
        
        # Afficher le résumé
        print(f"\n{'✅' if is_success else '❌'} VERDICT: {verdict.get('verdict', 'UNKNOWN')}")
        print(f"   Raison: {verdict.get('reason', 'N/A')[:100]}")
        print(f"   Amélioration qualité: {improvement:+.1f}")
        
        return verdict
    
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        log_experiment(
            agent_name="Judge",
            model_used="gemini-2.0-flash",
            action=ActionType.DEBUG,
            details={
                "iteration": iteration,
                "input_prompt": user_message[:500],
                "output_response": str(e),
                "error": True
            },
            status="FAILURE"
        )
        
        # Retourner un verdict d'échec
        return {
            "verdict": "FAIL",
            "reason": f"Erreur validation: {str(e)}",
            "tests_passed": False,
            "quality_score_after": quality_score_after,
            "quality_score_before": quality_score_before,
            "improvement": improvement
        }


if __name__ == "__main__":
    # Test
    result = validate_code("./test_code", 45.0, iteration=1)
    print(result)
