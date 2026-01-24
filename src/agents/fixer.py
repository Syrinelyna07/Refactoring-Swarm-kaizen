"""
=============================================================================
AGENT FIXER - LE CORRECTEUR
=============================================================================
Rôle: Refactoriser le code selon le plan de l'Auditor
=============================================================================
"""

from src.tools import call_gemini, read_files, write_file, load_prompt, validate_json_output
from src.utils.logger import log_experiment, ActionType
from typing import Dict, List, Optional
import json


def fix_code(target_dir: str, audit_report: Dict, iteration: int = 1) -> Dict:
    """
    Le Fixer refactorise le code selon le plan d'audit.
    
    Args:
        target_dir (str): Dossier contenant le code
        audit_report (Dict): Rapport d'analyse de l'Auditor
        iteration (int): Numéro d'itération (pour le logging)
    
    Returns:
        Dict: Résultat du refactoring avec code modifié
    """
    
    print(f"\n{'='*70}")
    print(f"🔧 AGENT FIXER - ITÉRATION {iteration}")
    print(f"{'='*70}")
    
    # Étape 1: Lire les fichiers actuels
    print("📁 Lecture des fichiers...")
    files_content = read_files(target_dir)
    
    if not files_content:
        raise Exception(f"Aucun fichier Python trouvé dans {target_dir}")
    
    print(f"   ✅ {len(files_content)} fichier(s) chargé(s)")
    
    # Étape 2: Préparer le prompt
    print("🤖 Appel Gemini...")
    system_prompt = load_prompt("src/prompts/fixer.txt")
    
    # Créer le message utilisateur
    refactoring_plan = audit_report.get("refactoring_plan", [])
    issues = audit_report.get("issues", [])
    
    user_message = f"""
Here's the refactoring plan from the Auditor:

{json.dumps(refactoring_plan, indent=2)}

And the identified issues:

{json.dumps(issues, indent=2)}

Current code files:
{json.dumps(files_content, indent=2)}

Please fix the code according to the plan. Return ONLY the corrected Python code files as JSON:
{{
  "files_fixed": {{
    "filename.py": "corrected code here",
    ...
  }},
  "summary": "What was changed"
}}
    """
    
    # Étape 3: Appeler Gemini
    try:
        response = call_gemini(system_prompt, user_message)
        
        # Parser la réponse JSON
        fix_result = validate_json_output(response)
        
        # Étape 4: Écrire les fichiers corrigés
        print("💾 Écriture des fichiers corrigés...")
        files_fixed = fix_result.get("files_fixed", {})
        
        for file_path, content in files_fixed.items():
            full_path = f"{target_dir}/{file_path}"
            success = write_file(full_path, content)
            if success:
                print(f"   ✅ {file_path}")
            else:
                print(f"   ❌ {file_path}")
        
        # Log l'action
        log_experiment(
            agent_name="Fixer",
            model_used="gemini-2.0-flash",
            action=ActionType.FIX,
            details={
                "iteration": iteration,
                "input_prompt": user_message[:500],
                "output_response": response[:500],
                "files_fixed": len(files_fixed),
                "summary": fix_result.get("summary", "")
            },
            status="SUCCESS"
        )
        
        fix_result["files_fixed_count"] = len(files_fixed)
        
        print(f"✅ Refactoring complété")
        print(f"   - Fichiers modifiés: {len(files_fixed)}")
        print(f"   - Résumé: {fix_result.get('summary', 'N/A')[:100]}")
        
        return fix_result
    
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        log_experiment(
            agent_name="Fixer",
            model_used="gemini-2.0-flash",
            action=ActionType.FIX,
            details={
                "iteration": iteration,
                "input_prompt": user_message[:500],
                "output_response": str(e),
                "error": True
            },
            status="FAILURE"
        )
        raise


if __name__ == "__main__":
    # Test
    audit_result = {
        "issues": [{"file": "test.py", "line": 1, "type": "BUG", "description": "Test"}],
        "refactoring_plan": []
    }
    result = fix_code("./test_code", audit_result)
    print(result)
