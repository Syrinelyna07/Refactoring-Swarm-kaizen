"""
Script de test simplifié pour le rôle Data Officer
Version sans imports complexes
"""
import sys
import json
import shutil
import importlib.util
from pathlib import Path


def load_module(module_name: str, file_path: Path):
    """Charge un module Python dynamiquement"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


# Charger les modules nécessaires
base_dir = Path(__file__).parent
src_dir = base_dir / "src"

# Ajouter src au path
sys.path.insert(0, str(src_dir))

# Charger logger
logger_module = load_module("logger", src_dir / "utils" / "logger.py")
log_experiment = logger_module.log_experiment
ActionType = logger_module.ActionType
initialize_logger = logger_module.initialize_logger
finalize_logger = logger_module.finalize_logger
get_logger_stats = logger_module.get_logger_stats

# Charger telemetry
telemetry_module = load_module("telemetry", src_dir / "tools" / "telemetry.py")
TelemetryTracker = telemetry_module.TelemetryTracker
EventType = telemetry_module.EventType

# Charger validator
validator_module = load_module("validator", src_dir / "tools" / "data_validator.py")
DataValidator = validator_module.DataValidator

# Charger analyzer
analyzer_module = load_module("analyzer", src_dir / "tools" / "metrics_analyzer.py")
MetricsAnalyzer = analyzer_module.MetricsAnalyzer


def test_1_logger_base():
    """Test 1 : Fonctionnement de base du logger"""
    print("\n🧪 Test 1 : Logger de base")
    print("-" * 60)
    
    test_dir = Path("test_outputs/test1_logger")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    initialize_logger(test_dir)
    
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
    
    telemetry_file = test_dir / "telemetry_data.json"
    experiment_file = test_dir / "experiment_data.json"
    
    assert telemetry_file.exists(), "❌ telemetry_data.json manquant"
    assert experiment_file.exists(), "❌ experiment_data.json manquant"
    
    print("  ✓ Les deux fichiers JSON créés")
    
    with open(experiment_file, 'r') as f:
        exp_data = json.load(f)
    
    assert len(exp_data["logs"]) >= 2, f"❌ Pas assez de logs: {len(exp_data['logs'])}"
    
    print("✅ TelemetryTracker compatible avec le logger imposé")


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
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            result = test_func()
            if result is False:
                failed += 1
            else:
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
    else:
        print("\n⚠️  Certains tests ont échoué")
    
    print("=" * 70)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
