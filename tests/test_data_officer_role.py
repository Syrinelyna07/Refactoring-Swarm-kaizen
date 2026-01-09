"""
Test Suite pour valider le rôle du Data Officer
Vérifie que tous les composants de télémétrie fonctionnent correctement
"""
import sys
import json
from pathlib import Path

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.logger import log_experiment, ActionType, initialize_logger, finalize_logger
from tools.telemetry import TelemetryTracker, EventType
from tools.data_validator import DataValidator
from tools.metrics_analyzer import MetricsAnalyzer


class TestDataOfficerRole:
    """Tests pour valider le rôle du Data Officer"""
    
    def __init__(self, test_dir: Path):
        self.test_dir = test_dir
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.results = {
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": []
        }
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print("=" * 70)
        print("🧪 TEST SUITE - RÔLE DATA OFFICER")
        print("=" * 70)
        print()
        
        tests = [
            ("Test 1: Logger imposé existe", self.test_logger_exists),
            ("Test 2: ActionType conforme", self.test_action_type_enum),
            ("Test 3: Validation champs obligatoires", self.test_required_fields),
            ("Test 4: Génération experiment_data.json", self.test_json_generation),
            ("Test 5: Validation du schéma JSON", self.test_json_schema_validation),
            ("Test 6: TelemetryTracker compatible", self.test_telemetry_integration),
            ("Test 7: MetricsAnalyzer fonctionnel", self.test_metrics_analyzer),
            ("Test 8: Dataset de test générable", self.test_dataset_generation),
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
                self._mark_success(test_name)
            except Exception as e:
                self._mark_failure(test_name, str(e))
        
        self._print_summary()
        return self.results["tests_failed"] == 0
    
    def test_logger_exists(self):
        """Vérifie que le logger imposé existe avec la bonne structure"""
        from utils import logger
        
        # Vérifier les exports obligatoires
        assert hasattr(logger, 'log_experiment'), "Fonction log_experiment manquante"
        assert hasattr(logger, 'ActionType'), "Enum ActionType manquante"
        assert hasattr(logger, 'initialize_logger'), "Fonction initialize_logger manquante"
        assert hasattr(logger, 'finalize_logger'), "Fonction finalize_logger manquante"
    
    def test_action_type_enum(self):
        """Vérifie que ActionType a les valeurs imposées"""
        required_actions = ['ANALYSIS', 'GENERATION', 'DEBUG', 'FIX']
        
        for action in required_actions:
            assert hasattr(ActionType, action), f"ActionType.{action} manquant"
            assert ActionType[action].value == action.lower(), f"Valeur incorrecte pour {action}"
    
    def test_required_fields(self):
        """Teste la validation des champs obligatoires"""
        log_dir = self.test_dir / "test_required_fields"
        initialize_logger(log_dir)
        
        # Test 1: Doit échouer sans input_prompt
        try:
            log_experiment(
                agent_name="TestAgent",
                model_used="test-model",
                action=ActionType.ANALYSIS,
                details={"output_response": "test"},
                status="SUCCESS"
            )
            raise AssertionError("Devrait échouer sans input_prompt")
        except ValueError as e:
            assert "input_prompt" in str(e), "Message d'erreur incorrect"
        
        # Test 2: Doit échouer sans output_response
        try:
            log_experiment(
                agent_name="TestAgent",
                model_used="test-model",
                action=ActionType.ANALYSIS,
                details={"input_prompt": "test"},
                status="SUCCESS"
            )
            raise AssertionError("Devrait échouer sans output_response")
        except ValueError as e:
            assert "output_response" in str(e), "Message d'erreur incorrect"
        
        # Test 3: Doit réussir avec les deux champs
        log_experiment(
            agent_name="TestAgent",
            model_used="test-model",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": "Test prompt",
                "output_response": "Test response"
            },
            status="SUCCESS"
        )
    
    def test_json_generation(self):
        """Teste la génération du fichier experiment_data.json"""
        log_dir = self.test_dir / "test_json_generation"
        initialize_logger(log_dir)
        
        # Générer quelques logs
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
        
        # Vérifier que le fichier existe
        json_file = log_dir / "experiment_data.json"
        assert json_file.exists(), "experiment_data.json n'a pas été créé"
        
        # Vérifier que c'est du JSON valide
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Vérifier la structure
        assert "session_id" in data, "session_id manquant"
        assert "logs" in data, "logs manquant"
        assert len(data["logs"]) == 3, f"Nombre de logs incorrect: {len(data['logs'])}"
    
    def test_json_schema_validation(self):
        """Teste la validation du schéma avec DataValidator"""
        log_dir = self.test_dir / "test_validation"
        initialize_logger(log_dir)
        
        # Créer des logs valides
        log_experiment(
            agent_name="Auditor_Agent",
            model_used="gemini-2.5-flash",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": "Analyse ce code",
                "output_response": "Code analysé",
                "file": "test.py"
            },
            status="SUCCESS"
        )
        
        finalize_logger()
        
        # Valider avec DataValidator
        json_file = log_dir / "experiment_data.json"
        is_valid, errors = DataValidator.validate_file(json_file)
        
        if not is_valid:
            print(f"❌ Erreurs de validation: {errors}")
        
        assert is_valid, f"Validation échouée: {errors}"
    
    def test_telemetry_integration(self):
        """Teste l'intégration avec TelemetryTracker"""
        log_dir = self.test_dir / "test_telemetry"
        tracker = TelemetryTracker()
        tracker.initialize(log_dir)
        
        # Utiliser le tracker
        tracker.track_event(
            event_type=EventType.CODE_ANALYSIS,
            agent_name="TestAgent",
            data={
                "input_prompt": "Test",
                "output_response": "Result",
                "file": "test.py"
            },
            success=True
        )
        
        tracker.finalize()
        
        # Vérifier que les fichiers sont créés
        assert (log_dir / "telemetry_data.json").exists(), "telemetry_data.json manquant"
    
    def test_metrics_analyzer(self):
        """Teste l'analyseur de métriques"""
        log_dir = self.test_dir / "test_metrics"
        initialize_logger(log_dir)
        
        # Créer des logs variés
        actions = [ActionType.ANALYSIS, ActionType.FIX, ActionType.DEBUG]
        agents = ["Auditor", "Fixer", "Judge"]
        
        for i, (action, agent) in enumerate(zip(actions, agents)):
            log_experiment(
                agent_name=agent,
                model_used="gemini-2.5-flash",
                action=action,
                details={
                    "input_prompt": f"Prompt {i}",
                    "output_response": f"Response {i}"
                },
                status="SUCCESS" if i % 2 == 0 else "FAILURE"
            )
        
        finalize_logger()
        
        # Analyser
        json_file = log_dir / "experiment_data.json"
        analyzer = MetricsAnalyzer(json_file)
        
        # Vérifier les métriques
        agent_perf = analyzer.get_agent_performance()
        assert len(agent_perf) == 3, "Nombre d'agents incorrect"
        
        report = analyzer.generate_summary_report()
        assert "RAPPORT D'ANALYSE" in report, "Rapport mal formaté"
    
    def test_dataset_generation(self):
        """Teste la génération du dataset de test"""
        from tests.test_dataset_generator import TestDatasetGenerator
        
        output_dir = self.test_dir / "test_dataset"
        TestDatasetGenerator.generate_dataset(output_dir, num_cases=3)
        
        # Vérifier la structure
        assert output_dir.exists(), "Dataset non créé"
        assert (output_dir / "index.json").exists(), "index.json manquant"
        
        # Vérifier qu'il y a des cas
        cases = list(output_dir.glob("case*"))
        assert len(cases) == 3, f"Nombre de cas incorrect: {len(cases)}"
        
        # Vérifier la structure d'un cas
        first_case = cases[0]
        assert (first_case / "buggy_code.py").exists(), "Code buggé manquant"
        assert (first_case / "metadata.json").exists(), "Metadata manquante"
    
    def _mark_success(self, test_name: str):
        """Marque un test comme réussi"""
        self.results["tests_passed"] += 1
        print(f"✅ {test_name}")
    
    def _mark_failure(self, test_name: str, error: str):
        """Marque un test comme échoué"""
        self.results["tests_failed"] += 1
        self.results["errors"].append({"test": test_name, "error": error})
        print(f"❌ {test_name}")
        print(f"   Erreur: {error}")
    
    def _print_summary(self):
        """Affiche le résumé des tests"""
        print()
        print("=" * 70)
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 70)
        print(f"✅ Tests réussis: {self.results['tests_passed']}")
        print(f"❌ Tests échoués: {self.results['tests_failed']}")
        print()
        
        if self.results["tests_failed"] == 0:
            print("🎉 TOUS LES TESTS SONT PASSÉS!")
            print("✅ Votre rôle de Data Officer est correctement implémenté.")
        else:
            print("⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
            print("Erreurs détaillées:")
            for error in self.results["errors"]:
                print(f"  - {error['test']}: {error['error']}")
        
        print("=" * 70)


def main():
    """Point d'entrée principal"""
    test_dir = Path("test_output_data_officer")
    
    # Nettoyer le dossier de test
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    
    # Exécuter les tests
    tester = TestDataOfficerRole(test_dir)
    success = tester.run_all_tests()
    
    # Code de sortie
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
