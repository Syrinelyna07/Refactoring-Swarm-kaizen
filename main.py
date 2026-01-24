#!/usr/bin/env python3
"""
=============================================================================
THE REFACTORING SWARM - MAIN ORCHESTRATOR
=============================================================================
Responsable: L'Orchestrateur (Lead Dev)
Rôle: Entry point + CLI + Gestion des arguments
=============================================================================
"""

import argparse
import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Imports du projet
from src.orchestrator.graph import run_orchestrator, validate_state
from src.utils.logger import log_experiment, finalize_experiment_data, ActionType


def validate_target_directory(target_dir: str) -> bool:
    """
    ✅ Valide que le dossier cible existe et est accessible.
    """
    if not os.path.exists(target_dir):
        print(f"❌ ERREUR: Le dossier '{target_dir}' n'existe pas.")
        return False
    
    if not os.path.isdir(target_dir):
        print(f"❌ ERREUR: '{target_dir}' n'est pas un dossier.")
        return False
    
    if not os.access(target_dir, os.R_OK):
        print(f"❌ ERREUR: Pas d'accès en lecture au dossier '{target_dir}'.")
        return False
    
    print(f"✅ Dossier validé: {os.path.abspath(target_dir)}")
    return True


def validate_python_files(target_dir: str) -> bool:
    """
    ✅ Vérifie que le dossier contient au moins des fichiers Python.
    """
    python_files = list(Path(target_dir).rglob("*.py"))
    
    if not python_files:
        print(f"❌ ERREUR: Aucun fichier Python trouvé dans '{target_dir}'.")
        return False
    
    print(f"✅ {len(python_files)} fichier(s) Python trouvé(s)")
    return True


def validate_environment() -> bool:
    """
    ✅ Valide l'environnement avant le lancement.
    """
    print("\n" + "="*70)
    print("🔍 VÉRIFICATION DE L'ENVIRONNEMENT")
    print("="*70)
    
    checks = []
    
    # Vérifier .env
    if os.path.exists(".env"):
        print("✅ Fichier .env détecté")
        load_dotenv()
        checks.append(True)
    else:
        print("⚠️ Fichier .env non trouvé (optionnel si variables système)")
        checks.append(True)
    
    # Vérifier dossier logs
    if not os.path.exists("logs"):
        os.makedirs("logs", exist_ok=True)
        print("✅ Dossier logs/ créé")
    else:
        print("✅ Dossier logs/ existant")
    checks.append(True)
    
    # Vérifier structure du projet
    required_files = [
        "src/orchestrator/graph.py",
        "src/utils/logger.py",
        "requirements.txt"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} présent")
            checks.append(True)
        else:
            print(f"❌ {file} manquant")
            checks.append(False)
    
    return all(checks)


def create_cli_parser() -> argparse.ArgumentParser:
    """
    📋 Crée le parseur des arguments CLI.
    
    Utilisation:
        python main.py --target_dir ./code_to_fix --max_iterations 10
    """
    parser = argparse.ArgumentParser(
        prog="The Refactoring Swarm",
        description="🚀 Système multi-agents autonomes pour refactorisation de code Python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python main.py --target_dir ./buggy_code
  python main.py --target_dir ./project --max_iterations 5 --verbose
  python main.py --target_dir ./app --dry_run

Notes:
  - target_dir est OBLIGATOIRE
  - max_iterations défaut: 10
  - Tous les logs sont écrits dans logs/experiment_data.json
        """
    )
    
    # Argument obligatoire
    parser.add_argument(
        "--target_dir",
        type=str,
        required=True,
        help="Dossier contenant le code Python à refactoriser (OBLIGATOIRE)"
    )
    
    # Arguments optionnels
    parser.add_argument(
        "--max_iterations",
        type=int,
        default=10,
        help="Nombre maximum d'itérations de la boucle de feedback (défaut: 10)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Mode verbose: affiche plus de détails"
    )
    
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Mode simulation: n'écrit aucun fichier"
    )
    
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./output",
        help="Dossier de sortie pour le code refactorisé (défaut: ./output)"
    )
    
    return parser


def print_welcome_banner():
    """
    🎨 Affiche la bannière de bienvenue.
    """
    banner = """
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                  🚀 THE REFACTORING SWARM 🚀                              ║
║                                                                            ║
║              Système Multi-Agents pour Refactorisation de Code             ║
║                                                                            ║
║  Orchestrateur: Lead Dev                                                  ║
║  Agents: Auditor, Fixer, Judge                                            ║
║  Itérations max: 10                                                       ║
║  Boucle de feedback: Automatique avec Self-Healing                        ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """
    🎯 Main Orchestrator Entry Point
    """
    
    # Bannière
    print_welcome_banner()
    
    # Parser les arguments
    parser = create_cli_parser()
    args = parser.parse_args()
    
    # Vérification basique des arguments
    if args.max_iterations < 1 or args.max_iterations > 100:
        print("❌ ERREUR: max_iterations doit être entre 1 et 100")
        sys.exit(1)
    
    # Logging initial
    log_experiment(
        agent_name="ORCHESTRATOR",
        model_used="system",
        action=ActionType.ANALYSIS,
        details={
            "message": "Démarrage du système",
            "target_dir": args.target_dir,
            "max_iterations": args.max_iterations,
            "input_prompt": f"Starting refactoring on {args.target_dir}",
            "output_response": "System initialized"
        },
        status="SUCCESS"
    )
    
    # Validations
    print("\n" + "="*70)
    print("📋 VALIDATIONS PRE-LANCEMENT")
    print("="*70)
    
    # 1. Environnement
    if not validate_environment():
        print("❌ Environnement invalide. Arrêt.")
        log_experiment(
            agent_name="ORCHESTRATOR",
            model_used="system",
            action=ActionType.ANALYSIS,
            details={
                "message": "Environnement invalide",
                "input_prompt": "Validating environment",
                "output_response": "Environment validation failed"
            },
            status="FAILURE"
        )
        sys.exit(1)
    
    # 2. Dossier cible
    if not validate_target_directory(args.target_dir):
        log_experiment(
            agent_name="ORCHESTRATOR",
            model_used="system",
            action=ActionType.ANALYSIS,
            details={
                "message": f"Dossier cible invalide: {args.target_dir}",
                "input_prompt": f"Validating directory {args.target_dir}",
                "output_response": "Directory validation failed"
            },
            status="FAILURE"
        )
        sys.exit(1)
    
    # 3. Fichiers Python
    if not validate_python_files(args.target_dir):
        log_experiment(
            agent_name="ORCHESTRATOR",
            model_used="system",
            action=ActionType.ANALYSIS,
            details={
                "message": "Aucun fichier Python trouvé",
                "input_prompt": f"Checking Python files in {args.target_dir}",
                "output_response": "No Python files found"
            },
            status="FAILURE"
        )
        sys.exit(1)
    
    # ✅ Tous les checks passent
    print("\n" + "="*70)
    print("✅ TOUS LES CHECKS PASSENT - LANCEMENT")
    print("="*70 + "\n")
    
    log_experiment(
        agent_name="ORCHESTRATOR",
        model_used="system",
        action=ActionType.ANALYSIS,
        details={
            "message": "Tous les pré-checks passés",
            "input_prompt": "Running pre-flight checks",
            "output_response": "All checks passed"
        },
        status="SUCCESS"
    )
    
    # Lancer l'orchestrateur
    try:
        final_state = run_orchestrator(
            target_dir=args.target_dir,
            max_iterations=args.max_iterations
        )
        
        # Log du résultat
        log_experiment(
            agent_name="ORCHESTRATOR",
            model_used="system",
            action=ActionType.ANALYSIS,
            details={
                "message": "Exécution complète",
                "input_prompt": f"Running orchestrator on {args.target_dir}",
                "output_response": f"Completed {final_state['iteration']} iterations",
                "iterations": final_state['iteration'],
                "fix_attempts": final_state['fix_attempts'],
                "tests_passed": final_state['tests_passed'],
                "quality_improvement": (
                    final_state['quality_score_after'] - final_state['quality_score_before']
                    if final_state['quality_score_after'] and final_state['quality_score_before']
                    else None
                )
            },
            status="SUCCESS"
        )
        
        # Finalize les logs
        finalize_experiment_data()
        
        # Résumé final
        print("\n" + "="*70)
        print("🎉 MISSION COMPLÈTE")
        print("="*70)
        print(f"📊 Résultats:")
        print(f"   ✅ Tests réussis: {final_state['tests_passed']}")
        print(f"   ✅ Itérations: {final_state['iteration']}")
        print(f"   ✅ Logs sauvegardés dans: logs/experiment_data.json")
        
        sys.exit(0)
    
    except KeyboardInterrupt:
        print("\n\n❌ Interruption utilisateur (Ctrl+C)")
        log_experiment(
            agent_name="ORCHESTRATOR",
            model_used="system",
            action=ActionType.DEBUG,
            details={
                "message": "Arrêt par l'utilisateur",
                "input_prompt": "User interrupted",
                "output_response": "Process terminated"
            },
            status="FAILURE"
        )
        finalize_experiment_data()
        sys.exit(130)
    
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {str(e)}")
        log_experiment(
            agent_name="ORCHESTRATOR",
            model_used="system",
            action=ActionType.DEBUG,
            details={
                "message": f"Erreur: {str(e)}",
                "input_prompt": "Running orchestrator",
                "output_response": str(e)
            },
            status="FAILURE"
        )
        finalize_experiment_data()
        sys.exit(1)


if __name__ == "__main__":
    main()