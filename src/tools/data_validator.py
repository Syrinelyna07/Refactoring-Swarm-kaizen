"""
Data Validator - Valide la conformité des données de télémétrie
Responsable: Data Officer
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Import avec fallback
try:
    from jsonschema import validate, ValidationError, Draft7Validator
except ImportError:
    print("⚠️  jsonschema non installé. Installez avec: pip install jsonschema")
    # Créer des classes mock pour éviter les erreurs
    class ValidationError(Exception):
        pass
    def validate(*args, **kwargs):
        pass


class DataValidator:
    """Validateur de données pour le fichier experiment_data.json"""
    
    # Schéma JSON attendu pour le fichier de télémétrie
    SCHEMA = {
        "type": "object",
        "required": ["metadata", "metrics", "events"],
        "properties": {
            "metadata": {
                "type": "object",
                "required": ["session_id", "start_time", "last_update", "total_events", "current_iteration"],
                "properties": {
                    "session_id": {"type": "string"},
                    "start_time": {"type": "string"},
                    "last_update": {"type": "string"},
                    "total_events": {"type": "integer", "minimum": 0},
                    "current_iteration": {"type": "integer", "minimum": 0}
                }
            },
            "metrics": {
                "type": "object",
                "required": [
                    "session_id", "start_time", "end_time", 
                    "total_iterations", "total_events", 
                    "successful_events", "failed_events", "success_rate"
                ],
                "properties": {
                    "session_id": {"type": "string"},
                    "start_time": {"type": "string"},
                    "end_time": {"type": "string"},
                    "total_iterations": {"type": "integer", "minimum": 0},
                    "total_events": {"type": "integer", "minimum": 0},
                    "successful_events": {"type": "integer", "minimum": 0},
                    "failed_events": {"type": "integer", "minimum": 0},
                    "success_rate": {"type": "number", "minimum": 0, "maximum": 1},
                    "agents_statistics": {"type": "object"},
                    "event_types_distribution": {"type": "object"}
                }
            },
            "events": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": [
                        "event_id", "timestamp", "event_type", 
                        "agent_name", "iteration", "data", "success"
                    ],
                    "properties": {
                        "event_id": {"type": "string"},
                        "timestamp": {"type": "string"},
                        "event_type": {"type": "string"},
                        "agent_name": {"type": "string"},
                        "iteration": {"type": "integer", "minimum": 0},
                        "data": {"type": "object"},
                        "duration_ms": {"type": ["number", "null"]},
                        "success": {"type": "boolean"},
                        "error_message": {"type": ["string", "null"]}
                    }
                }
            }
        }
    }
    
    @classmethod
    def validate_file(cls, file_path: Path) -> Tuple[bool, List[str]]:
        """
        Valide un fichier experiment_data.json
        
        Args:
            file_path: Chemin vers le fichier à valider
            
        Returns:
            Tuple (is_valid, errors_list)
        """
        errors = []
        
        # Vérifier que le fichier existe
        if not file_path.exists():
            return False, ["Le fichier experiment_data.json n'existe pas"]
        
        # Charger le JSON
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return False, [f"Erreur de parsing JSON: {str(e)}"]
        except Exception as e:
            return False, [f"Erreur de lecture du fichier: {str(e)}"]
        
        # Valider contre le schéma
        try:
            validate(instance=data, schema=cls.SCHEMA)
        except ValidationError as e:
            errors.append(f"Erreur de validation du schéma: {e.message}")
            errors.append(f"Chemin: {' -> '.join(str(p) for p in e.path)}")
        
        # Validations supplémentaires
        additional_errors = cls._validate_business_rules(data)
        errors.extend(additional_errors)
        
        return len(errors) == 0, errors
    
    @classmethod
    def _validate_business_rules(cls, data: Dict[str, Any]) -> List[str]:
        """
        Valide les règles métier
        
        Args:
            data: Données à valider
            
        Returns:
            Liste des erreurs trouvées
        """
        errors = []
        
        # Vérifier la cohérence des compteurs
        metadata = data.get("metadata", {})
        events = data.get("events", [])
        
        if metadata.get("total_events") != len(events):
            errors.append(
                f"Incohérence: metadata.total_events ({metadata.get('total_events')}) "
                f"!= nombre réel d'événements ({len(events)})"
            )
        
        # Vérifier que tous les événements ont des IDs uniques
        event_ids = [e.get("event_id") for e in events]
        if len(event_ids) != len(set(event_ids)):
            errors.append("Des event_id en double ont été détectés")
        
        # Vérifier que les timestamps sont dans l'ordre chronologique
        timestamps = [e.get("timestamp") for e in events]
        if timestamps != sorted(timestamps):
            errors.append("Les événements ne sont pas triés chronologiquement")
        
        # Vérifier les métriques
        metrics = data.get("metrics", {})
        total_events = metrics.get("total_events", 0)
        successful = metrics.get("successful_events", 0)
        failed = metrics.get("failed_events", 0)
        
        if successful + failed != total_events:
            errors.append(
                f"Incohérence: successful_events ({successful}) + "
                f"failed_events ({failed}) != total_events ({total_events})"
            )
        
        return errors
    
    @classmethod
    def generate_report(cls, file_path: Path) -> str:
        """
        Génère un rapport de validation
        
        Args:
            file_path: Chemin vers le fichier à valider
            
        Returns:
            Rapport textuel
        """
        is_valid, errors = cls.validate_file(file_path)
        
        report = ["=" * 60]
        report.append("RAPPORT DE VALIDATION - experiment_data.json")
        report.append("=" * 60)
        report.append(f"Fichier: {file_path}")
        report.append("")
        
        if is_valid:
            report.append("✓ VALIDATION RÉUSSIE")
            report.append("Le fichier respecte tous les critères requis.")
        else:
            report.append("✗ VALIDATION ÉCHOUÉE")
            report.append("")
            report.append("Erreurs détectées:")
            for i, error in enumerate(errors, 1):
                report.append(f"  {i}. {error}")
        
        report.append("=" * 60)
        
        return "\n".join(report)
