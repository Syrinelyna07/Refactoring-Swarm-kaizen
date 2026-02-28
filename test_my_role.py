"""
Script de test complet pour le rôle Data Officer
Lance tous les tests pour valider que votre implémentation fonctionne
"""
import sys
import json
import shutil
from pathlib import Path

# Ajouter src au path AVANT tout import
base_path = Path(__file__).parent / "src"
if str(base_path) not in sys.path:
    sys.path.insert(0, str(base_path))

# Imports directs maintenant
from utils.logger import log_experiment, ActionType, initialize_logger, finalize_logger, get_logger_stats

# Import avec gestion d'erreur pour telemetry
try:
    from tools.telemetry import TelemetryTracker, EventType
except ImportError as e:
    print(f"⚠️  Import telemetry échoué, chargement direct...")
    import importlib.util
    telemetry_path = Path(__file__).parent / "src" / "tools" / "telemetry.py"
    spec = importlib.util.spec_from_file_location("telemetry", telemetry_path)
    telemetry_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(telemetry_module)
    TelemetryTracker = telemetry_module.TelemetryTracker
    EventType = telemetry_module.EventType

from tools.data_validator import DataValidator
from tools.metrics_analyzer import MetricsAnalyzer


def test_1_logger_base():
    """Test 1 : Fonctionnement de base du logger"""
    print("\n🧪 Test 1 : Logger de base")
    print("-" * 60)
    
    test_dir = Path("test_outputs/test1_logger")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    initialize_logger(test_dir)
    
    # Log simple
    log_experiment(
        agent_name="TestAgent",
        model_used="gemini-2.5-flash",
        action=ActionType.ANALYSIS,
        details={
            "input_prompt": "Analyse ce code Python",
            "output_response": "Le code contient 3 problèmes",
            "file": "test.py"
        },
        status="SUCCESS"
    )
    
    finalize_logger()
    
    # Vérification
    json_file = test_dir / "experiment_data.json"
    assert json_file.exists(), "❌ experiment_data.json non créé"
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    assert len(data["logs"]) == 1, "❌ Nombre de logs incorrect"
    assert data["logs"][0]["action"] == "analysis", "❌ Type d'action incorrect"
    
    print("✅ Logger de base fonctionne parfaitement")


def test_2_validation_champs_obligatoires():
    """Test 2 : Validation des champs obligatoires"""
    print("\n🧪 Test 2 : Validation champs obligatoires")
    print("-" * 60)
    
    test_dir = Path("test_outputs/test2_validation")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    initialize_logger(test_dir)
    
    # Test sans input_prompt (doit échouer)
    try:
        log_experiment(
            agent_name="TestAgent",
            model_used="test",
            action=ActionType.FIX,
            details={"output_response": "test"},
            status="SUCCESS"
        )
        print("❌ ERREUR : Devrait échouer sans input_prompt")
        return False
    except ValueError as e:
        if "input_prompt" in str(e):
            print("✅ Validation input_prompt OK")
        else:
            print(f"❌ Mauvais message d'erreur: {e}")
            return False
    
    # Test sans output_response (doit échouer)
    try:
        log_experiment(
            agent_name="TestAgent",
            model_used="test",
            action=ActionType.FIX,
            details={"input_prompt": "test"},
            status="SUCCESS"
        )
        print("❌ ERREUR : Devrait échouer sans output_response")
        return False
    except ValueError as e:
        if "output_response" in str(e):
            print("✅ Validation output_response OK")
        else:
            print(f"❌ Mauvais message d'erreur: {e}")
            return False
    
    print("✅ Validation des champs obligatoires fonctionne")


def test_3_les_4_action_types():
    """Test 3 : Les 4 ActionType imposés"""
    print("\n🧪 Test 3 : Les 4 ActionType imposés")
    print("-" * 60)
    
    test_dir = Path("test_outputs/test3_actions")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    initialize_logger(test_dir)
    
    actions_a_tester = [
        (ActionType.ANALYSIS, "Analyse du code"),
        (ActionType.GENERATION, "Génération de tests"),
        (ActionType.DEBUG, "Debug d'une erreur"),
        (ActionType.FIX, "Correction du code")
    ]
    
    for action, description in actions_a_tester:
        log_experiment(
            agent_name="MultiAgent",
            model_used="gemini-2.5-flash",
            action=action,
            details={
                "input_prompt": f"Prompt pour {description}",
                "output_response": f"Résultat de {description}",
                "task": description
            },
            status="SUCCESS"
        )
        print(f"  ✓ {action.value} testé")
    
    finalize_logger()
    
    # Vérifier le fichier
    with open(test_dir / "experiment_data.json", 'r') as f:
        data = json.load(f)
    
    actions_logged = [log["action"] for log in data["logs"]]
    assert "analysis" in actions_logged, "❌ ANALYSIS manquant"
    assert "generation" in actions_logged, "❌ GENERATION manquant"
    assert "debug" in actions_logged, "❌ DEBUG manquant"
    assert "fix" in actions_logged, "❌ FIX manquant"
    
    print("✅ Les 4 ActionType fonctionnent correctement")


def test_4_telemetry_tracker():
    """Test 4 : TelemetryTracker compatible"""
    print("\n🧪 Test 4 : TelemetryTracker")
    print("-" * 60)
    
    test_dir = Path("test_outputs/test4_telemetry")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    initialize_logger(test_dir)
    
    tracker = TelemetryTracker()
    tracker.initialize(test_dir)
    
    # Tracker quelques événements
    tracker.start_iteration(1)
    
    tracker.track_event(
        event_type=EventType.CODE_ANALYSIS,
        agent_name="Auditor",
        data={
            "input_prompt": "Analyse le fichier buggy.py",
            "output_response": "Trouvé 5 problèmes",
            "file": "buggy.py"
        },
        duration_ms=150.5
    )
    
    tracker.track_event(
        event_type=EventType.CODE_MODIFICATION,
        agent_name="Fixer",
        data={
            "input_prompt": "Corrige les 5 problèmes",
            "output_response": "Corrections appliquées",
            "file": "buggy.py"
        },
        duration_ms=320.8
    )
    
    tracker.end_iteration(1, success=True)
    tracker.finalize()
    
    # Vérifications
    telemetry_file = test_dir / "telemetry_data.json"
    experiment_file = test_dir / "experiment_data.json"
    
    assert telemetry_file.exists(), "❌ telemetry_data.json manquant"
    assert experiment_file.exists(), "❌ experiment_data.json manquant"
    
    print("  ✓ Les deux fichiers JSON créés")
    
    # Vérifier que les logs LLM sont enregistrés
    with open(experiment_file, 'r') as f:
        exp_data = json.load(f)
    
    # Doit avoir au moins 2 logs (CODE_ANALYSIS et CODE_MODIFICATION)
    assert len(exp_data["logs"]) >= 2, f"❌ Pas assez de logs: {len(exp_data['logs'])}"
    
    print("✅ TelemetryTracker compatible avec le logger imposé")


def test_5_data_validator():
    """Test 5 : DataValidator"""
    print("\n🧪 Test 5 : DataValidator")
    print("-" * 60)
    
    test_dir = Path("test_outputs/test5_validator")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    initialize_logger(test_dir)
    
    # Créer des logs valides
    for i in range(3):
        log_experiment(
            agent_name=f"Agent_{i}",
            model_used="gemini-2.5-flash",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": f"Prompt {i}",
                "output_response": f"Response {i}",
                "iteration": i
            },
            status="SUCCESS"
        )
    
    finalize_logger()
    
    # Valider
    json_file = test_dir / "experiment_data.json"
    is_valid, errors = DataValidator.validate_file(json_file)
    
    if not is_valid:
        print(f"❌ Validation échouée: {errors}")
        return False
    
    print("  ✓ Fichier JSON validé avec succès")
    
    # Générer un rapport
    report = DataValidator.generate_report(json_file)
    assert "VALIDATION RÉUSSIE" in report, "❌ Rapport incorrect"
    
    print("✅ DataValidator fonctionne correctement")


def test_6_metrics_analyzer():
    """Test 6 : MetricsAnalyzer"""
    print("\n🧪 Test 6 : MetricsAnalyzer")
    print("-" * 60)
    
    test_dir = Path("test_outputs/test6_metrics")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    initialize_logger(test_dir)
    
    # Créer des logs variés
    agents = ["Auditor", "Fixer", "Judge"]
    actions = [ActionType.ANALYSIS, ActionType.FIX, ActionType.DEBUG]
    
    for i, (agent, action) in enumerate(zip(agents, actions)):
        status = "SUCCESS" if i % 2 == 0 else "FAILURE"
        log_experiment(
            agent_name=agent,
            model_used="gemini-2.5-flash",
            action=action,
            details={
                "input_prompt": f"Task {i}",
                "output_response": f"Result {i}",
                "iteration": i
            },
            status=status
        )
    
    finalize_logger()
    
    # Analyser
    json_file = test_dir / "experiment_data.json"
    analyzer = MetricsAnalyzer(json_file)
    
    # Tester les métriques
    agent_perf = analyzer.get_agent_performance()
    assert len(agent_perf) == 3, f"❌ Nombre d'agents incorrect: {len(agent_perf)}"
    print(f"  ✓ {len(agent_perf)} agents analysés")
    
    # Tester le rapport
    report = analyzer.generate_summary_report()
    assert "RAPPORT D'ANALYSE" in report, "❌ Rapport mal formaté"
    print("  ✓ Rapport généré")
    
    print("✅ MetricsAnalyzer fonctionne correctement")


def test_7_scenario_complet():
    """Test 7 : Scénario complet de refactoring"""
    print("\n🧪 Test 7 : Scénario complet (simulation réelle)")
    print("-" * 60)
    
    test_dir = Path("test_outputs/test7_scenario")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    initialize_logger(test_dir)
    tracker = TelemetryTracker()
    tracker.initialize(test_dir)
    
    # Simulation d'un workflow complet
    print("  📝 Itération 1 : Analyse initiale")
    tracker.start_iteration(1)
    
    log_experiment(
        agent_name="Auditor_Agent",
        model_used="gemini-2.5-flash",
        action=ActionType.ANALYSIS,
        details={
            "input_prompt": "Analyse le code dans buggy_code.py et identifie tous les problèmes",
            "output_response": "J'ai identifié 5 problèmes: 1) Pas de docstrings, 2) Variables non définies...",
            "file": "buggy_code.py",
            "issues_found": 5,
            "pylint_score": 3.2
        },
        status="SUCCESS"
    )
    
    print("  🔧 Itération 1 : Corrections")
    log_experiment(
        agent_name="Fixer_Agent",
        model_used="gemini-2.5-flash",
        action=ActionType.FIX,
        details={
            "input_prompt": "Corrige les 5 problèmes identifiés dans buggy_code.py",
            "output_response": "J'ai corrigé le code en ajoutant des docstrings et en définissant les variables",
            "file": "buggy_code.py",
            "changes_made": 5
        },
        status="SUCCESS"
    )
    
    print("  🧪 Itération 1 : Tests")
    log_experiment(
        agent_name="Judge_Agent",
        model_used="gemini-2.5-flash",
        action=ActionType.DEBUG,
        details={
            "input_prompt": "Exécute les tests unitaires sur buggy_code.py",
            "output_response": "2 tests passent, 1 test échoue",
            "file": "buggy_code.py",
            "tests_passed": 2,
            "tests_failed": 1
        },
        status="FAILURE"
    )
    
    tracker.end_iteration(1, success=False)
    
    print("  📝 Itération 2 : Nouvelle correction")
    tracker.start_iteration(2)
    
    log_experiment(
        agent_name="Fixer_Agent",
        model_used="gemini-2.5-flash",
        action=ActionType.FIX,
        details={
            "input_prompt": "Corrige l'erreur qui fait échouer le test",
            "output_response": "Erreur corrigée: mauvais calcul dans la fonction sum",
            "file": "buggy_code.py",
            "changes_made": 1
        },
        status="SUCCESS"
    )
    
    log_experiment(
        agent_name="Judge_Agent",
        model_used="gemini-2.5-flash",
        action=ActionType.DEBUG,
        details={
            "input_prompt": "Exécute les tests unitaires",
            "output_response": "Tous les tests passent!",
            "file": "buggy_code.py",
            "tests_passed": 3,
            "tests_failed": 0
        },
        status="SUCCESS"
    )
    
    tracker.end_iteration(2, success=True)
    
    finalize_logger()
    tracker.finalize()
    
    print("\n  📊 Analyse des résultats...")
    
    # Analyser avec MetricsAnalyzer
    json_file = test_dir / "experiment_data.json"
    analyzer = MetricsAnalyzer(json_file)
    
    stats = get_logger_stats()
    print(f"    • Total logs: {stats['total_logs']}")
    print(f"    • Succès: {stats['success_count']}")
    print(f"    • Échecs: {stats['failure_count']}")
    print(f"    • Agents: {', '.join(stats['agents'])}")
    
    # Valider
    is_valid, errors = DataValidator.validate_file(json_file)
    if is_valid:
        print("    • Validation: ✓ OK")
    else:
        print(f"    • Validation: ✗ Erreurs: {errors}")
        return False
    
    print("\n✅ Scénario complet réussi - Système prêt pour production!")


def main():
    """Lance tous les tests"""
    print("=" * 70)
    print("🚀 TEST COMPLET DU RÔLE DATA OFFICER")
    print("=" * 70)
    
    tests = [
        test_1_logger_base,
        test_2_validation_champs_obligatoires,
        test_3_les_4_action_types,
        test_4_telemetry_tracker,
        test_5_data_validator,
        test_6_metrics_analyzer,
        test_7_scenario_complet
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ Test échoué: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 70)
    print(f"✅ Tests réussis: {passed}/{len(tests)}")
    print(f"❌ Tests échoués: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 FÉLICITATIONS! Tous les tests passent!")
        print("✅ Votre rôle de Data Officer est COMPLET et FONCTIONNEL")
        print("\n📝 Vous pouvez maintenant:")
        print("   1. Générer le dataset de test")
        print("   2. Intégrer avec les autres rôles")
        print("   3. Tester le système complet")
    else:
        print("\n⚠️  Certains tests ont échoué")
        print("Vérifiez les erreurs ci-dessus")
    
    print("=" * 70)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

