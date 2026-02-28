# check_setup.py
"""
=============================================================================
SETUP CHECKER - Validation de l'environnement
=============================================================================
Vérifie que tout est en place avant de lancer le système.
Lancez: python check_setup.py
=============================================================================
"""

import sys
import os
import subprocess
from pathlib import Path

# Couleurs pour le terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(title):
    print(f"\n{BOLD}{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}{RESET}\n")


def check_python_version():
    """✅ Vérifie la version de Python."""
    print_header("🐍 PYTHON VERSION")
    
    version = sys.version_info
    print(f"Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor in [10, 11, 12]:
        print(f"{GREEN}✅ Version compatible{RESET}")
        return True
    else:
        print(f"{RED}❌ Python 3.10+ requis{RESET}")
        return False


def check_directories():
    """✅ Vérifie la structure des dossiers."""
    print_header("📁 STRUCTURE DES DOSSIERS")
    
    required_dirs = ["src", "src/agents", "src/orchestrator", "src/utils", "logs"]
    all_ok = True
    
    for dir_name in required_dirs:
        if os.path.isdir(dir_name):
            print(f"{GREEN}✅{RESET} {dir_name}/")
        else:
            print(f"{RED}❌{RESET} {dir_name}/ manquant")
            all_ok = False
    
    return all_ok


def check_files():
    """✅ Vérifie les fichiers essentiels."""
    print_header("📄 FICHIERS ESSENTIELS")
    
    required_files = {
        "main.py": "Entry point principal",
        "requirements.txt": "Dépendances Python",
        "check_setup.py": "Ce script",
        "src/__init__.py": "Package Python",
        "src/orchestrator/graph.py": "Graphe LangGraph",
        "src/utils/logger.py": "Système de logging",
    }
    
    all_ok = True
    for file_name, description in required_files.items():
        if os.path.isfile(file_name):
            print(f"{GREEN}✅{RESET} {file_name:40} - {description}")
        else:
            print(f"{RED}❌{RESET} {file_name:40} - MANQUANT")
            all_ok = False
    
    return all_ok


def check_dependencies():
    """✅ Vérifie les dépendances Python."""
    print_header("📦 DÉPENDANCES PYTHON")
    
    # Dépendances clés à vérifier
    key_packages = {
        "langgraph": "Orchestration LangGraph",
        "langchain": "Framework LLM",
        "python-dotenv": "Gestion .env",
        "pytest": "Tests unitaires",
        "pylint": "Analyse statique",
    }
    
    missing = []
    installed = []
    
    for package_name, description in key_packages.items():
        try:
            __import__(package_name.replace("-", "_"))
            print(f"{GREEN}✅{RESET} {package_name:20} - {description}")
            installed.append(package_name)
        except ImportError:
            print(f"{RED}❌{RESET} {package_name:20} - MANQUANT")
            missing.append(package_name)
    
    if missing:
        print(f"\n{YELLOW}⚠️ Packages manquants: {', '.join(missing)}{RESET}")
        print(f"{YELLOW}Installez avec: pip install -r requirements.txt{RESET}")
        return False
    
    return True


def check_env_file():
    """✅ Vérifie le fichier .env."""
    print_header("🔑 CONFIGURATION .env")
    
    if os.path.exists(".env"):
        print(f"{GREEN}✅{RESET} Fichier .env trouvé")
        return True
    else:
        print(f"{YELLOW}⚠️{RESET} Fichier .env non trouvé")
        print("   Créez-le avec vos clés API (voir .env.example)")
        return True  # Non-bloquant


def check_logs_directory():
    """✅ Crée le dossier logs s'il n'existe pas."""
    print_header("📊 LOGS")
    
    if not os.path.exists("logs"):
        try:
            os.makedirs("logs")
            print(f"{GREEN}✅{RESET} Dossier logs/ créé")
        except Exception as e:
            print(f"{RED}❌{RESET} Impossible de créer logs/: {str(e)}")
            return False
    else:
        print(f"{GREEN}✅{RESET} Dossier logs/ existe")
    
    return True


def check_git():
    """✅ Vérifie Git (optionnel)."""
    print_header("🔄 GIT")
    
    if os.path.isdir(".git"):
        print(f"{GREEN}✅{RESET} Dépôt Git détecté")
        return True
    else:
        print(f"{YELLOW}⚠️{RESET} Dépôt Git non trouvé")
        print("   Initialisez avec: git init")
        return True  # Non-bloquant


def main():
    """🎯 Lancer tous les checks."""
    
    banner = f"""
{BOLD}{GREEN}╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                   🚀 THE REFACTORING SWARM - SETUP CHECKER 🚀             ║
║                                                                            ║
║                      Validation de l'environnement                         ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝{RESET}
    """
    print(banner)
    
    # Liste des checks
    checks = [
        ("Python Version", check_python_version),
        ("Structure Dossiers", check_directories),
        ("Fichiers Essentiels", check_files),
        ("Dépendances Python", check_dependencies),
        ("Fichier .env", check_env_file),
        ("Dossier logs/", check_logs_directory),
        ("Dépôt Git", check_git),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"{RED}❌ Erreur lors de {check_name}: {str(e)}{RESET}")
            results.append((check_name, False))
    
    # Résumé
    print_header("📋 RÉSUMÉ")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Checks réussis: {passed}/{total}\n")
    
    for check_name, result in results:
        status = f"{GREEN}✅ PASS{RESET}" if result else f"{RED}❌ FAIL{RESET}"
        print(f"{status} - {check_name}")
    
    # Conclusion
    print_header("RÉSULTAT FINAL")
    
    if all(result for _, result in results):
        print(f"{GREEN}{BOLD}🎉 TOUT EST PRÊT!{RESET}")
        print(f"{GREEN}Vous pouvez lancer: python main.py --target_dir ./code{RESET}\n")
        return 0
    else:
        print(f"{RED}{BOLD}⚠️ CORRIGEZ LES ERREURS AVANT DE CONTINUER{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())