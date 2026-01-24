"""
=============================================================================
AGENT AUDITOR - L'AUDITEUR
=============================================================================
Rôle: Analyser le code et produire un plan de refactoring
=============================================================================
"""

from src.tools import call_gemini, read_files, run_pylint, load_prompt, validate_json_output
from src.utils.logger import log_experiment, ActionType
from typing import Dict, List, Optional


def analyze_code(target_dir: str) -> Dict:
    """
    L'Auditor analyse le code cible.
    
    Args:
        target_dir (str): Dossier contenant le code à analyser
    
    Returns:
        Dict: Résultat d'analyse avec rapport et plan
    """
    
    print(f"\n{'='*70}")
    print("🔍 AGENT AUDITOR - LANCEMENT DE L'ANALYSE")
    print(f"{'='*70}")
    
    # Étape 1: Lire tous les fichiers
    print("📁 Lecture des fichiers...")
    files_content = read_files(target_dir)
    
    if not files_content:
        raise Exception(f"Aucun fichier Python trouvé dans {target_dir}")
    
    print(f"   ✅ {len(files_content)} fichier(s) trouvé(s)")
    
    # Étape 2: Lancer pylint
    print("📊 Analyse pylint...")
    quality_score, pylint_output = run_pylint(target_dir)
    print(f"   ✅ Score pylint: {quality_score}/10")
    
    # Étape 3: Préparer le prompt
    print("🤖 Appel Gemini...")
    system_prompt = load_prompt("src/prompts/auditor.txt")
    
    # Créer le message utilisateur
    files_text = "\n\n".join([
        f"## File: {name}\n```python\n{content}\n```"
        for name, content in list(files_content.items())[:5]  # Limiter à 5 fichiers pour éviter les tokens
    ])
    
    user_message = f"""
Analyze the following Python code for quality and correctness:

{files_text}

Also consider these metrics:
- Pylint score: {quality_score}/10
- Number of files: {len(files_content)}

Provide your analysis in the JSON format specified.
    """
    
    # Étape 4: Appeler Gemini
    try:
        response = call_gemini(system_prompt, user_message)
        
        # Parser la réponse JSON
        analysis = validate_json_output(response)
        
        # Log l'action
        log_experiment(
            agent_name="Auditor",
            model_used="gemini-2.0-flash",
            action=ActionType.ANALYSIS,
            details={
                "file_analyzed": target_dir,
                "input_prompt": user_message[:500],  # Premiers 500 chars
                "output_response": response[:500],
                "issues_found": len(analysis.get("issues", [])),
                "quality_score": quality_score
            },
            status="SUCCESS"
        )
        
        # Ajouter les metadata
        analysis["quality_score_before"] = quality_score
        analysis["files_analyzed"] = len(files_content)
        analysis["pylint_output"] = pylint_output
        
        print(f"✅ Audit terminé")
        print(f"   - Issues trouvés: {len(analysis.get('issues', []))}")
        print(f"   - Étapes de refactoring: {len(analysis.get('refactoring_plan', []))}")
        
        return analysis
    
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        log_experiment(
            agent_name="Auditor",
            model_used="gemini-2.0-flash",
            action=ActionType.ANALYSIS,
            details={
                "file_analyzed": target_dir,
                "input_prompt": user_message[:500],
                "output_response": str(e),
                "error": True
            },
            status="FAILURE"
        )
        raise


if __name__ == "__main__":
    # Test
    result = analyze_code("./test_code")
    print(result)
