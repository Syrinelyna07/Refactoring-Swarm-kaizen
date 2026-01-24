"""
Test simple pour vérifier que le système fonctionne
"""

import sys
import os

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("🧪 TEST D'IMPORTS")
print("=" * 70)

try:
    print("\n1️⃣ Import des outils...")
    from src.tools import call_gemini, read_files, run_pylint, run_pytest, load_prompt
    print("   ✅ Outils OK")
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    sys.exit(1)

try:
    print("\n2️⃣ Import du logger...")
    from src.utils.logger import log_experiment, ActionType
    print("   ✅ Logger OK")
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    sys.exit(1)

try:
    print("\n3️⃣ Import du graph...")
    from src.orchestrator.graph import AgentState, run_orchestrator
    print("   ✅ Graph OK")
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    sys.exit(1)

try:
    print("\n4️⃣ Import des agents...")
    from src.agents.auditor import analyze_code
    from src.agents.fixer import fix_code
    from src.agents.judge import validate_code
    print("   ✅ Agents OK")
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ TOUS LES IMPORTS PASSENT")
print("=" * 70)

print("\n📋 Vérifications:")
print("   ✅ src/tools.py - Outils")
print("   ✅ src/agents/auditor.py - Auditor")
print("   ✅ src/agents/fixer.py - Fixer")
print("   ✅ src/agents/judge.py - Judge")
print("   ✅ src/orchestrator/graph.py - Graphe")
print("   ✅ src/utils/logger.py - Logger")

print("\n🚀 PRÊT À COMMENCER!")
print("Exécutez: python main.py --target_dir ./sandbox/test_code")
