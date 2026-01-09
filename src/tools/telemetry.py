"""
Telemetry Tracker - Surcouche compatible avec le logger imposé
Responsable: Data Officer
"""
import json
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import threading

# Import corrigé pour éviter les erreurs d'import relatif
try:
    from ..utils.logger import log_experiment, ActionType as OfficialActionType
except ImportError:
    # Fallback pour exécution directe
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from utils.logger import log_experiment, ActionType as OfficialActionType


class EventType(Enum):
    """Types d'événements tracés (mapping vers ActionType imposé)"""
    AGENT_START = "agent_start"
    AGENT_END = "agent_end"
    CODE_ANALYSIS = "code_analysis"          # → ActionType.ANALYSIS
    CODE_MODIFICATION = "code_modification"  # → ActionType.FIX
    TEST_EXECUTION = "test_execution"        # → ActionType.DEBUG
    ITERATION_START = "iteration_start"
    ITERATION_END = "iteration_end"
    ERROR = "error"
    QUALITY_METRIC = "quality_metric"
    TOOL_CALL = "tool_call"


# Mapping vers les types imposés
EVENT_TO_ACTION_MAPPING = {
    EventType.CODE_ANALYSIS: OfficialActionType.ANALYSIS,
    EventType.CODE_MODIFICATION: OfficialActionType.FIX,
    EventType.TEST_EXECUTION: OfficialActionType.DEBUG,
}


@dataclass
class Event:
    """Structure d'un événement tracé"""
    event_id: str
    timestamp: str
    event_type: str
    agent_name: str
    iteration: int
    data: Dict[str, Any]
    duration_ms: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None


class TelemetryTracker:
    """
    Tracker compatible avec le logger imposé
    Convertit automatiquement vers log_experiment() quand nécessaire
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.events: List[Event] = []
            self.session_id = str(uuid.uuid4())
            self.start_time = datetime.now().isoformat()
            self.current_iteration = 0
            self.log_file: Optional[Path] = None
            self._initialized = True
    
    def initialize(self, log_dir: Path):
        """Initialise le répertoire de logs"""
        self.log_file = log_dir / "telemetry_data.json"
        log_dir.mkdir(parents=True, exist_ok=True)
        self._save_to_disk()
    
    def track_event(
        self,
        event_type: EventType,
        agent_name: str,
        data: Dict[str, Any],
        duration_ms: Optional[float] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        model_used: str = "gemini-2.5-flash"
    ) -> str:
        """
        Enregistre un événement ET log vers le système imposé si applicable
        """
        with self._lock:
            event = Event(
                event_id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                event_type=event_type.value,
                agent_name=agent_name,
                iteration=self.current_iteration,
                data=data,
                duration_ms=duration_ms,
                success=success,
                error_message=error_message
            )
            
            self.events.append(event)
            
            # INTÉGRATION: Si l'événement correspond à une action LLM, logger officiellement
            if event_type in EVENT_TO_ACTION_MAPPING:
                self._log_to_official_system(
                    event=event,
                    action_type=EVENT_TO_ACTION_MAPPING[event_type],
                    model_used=model_used
                )
            
            if len(self.events) % 5 == 0:
                self._save_to_disk()
            
            return event.event_id
    
    def _log_to_official_system(
        self,
        event: Event,
        action_type: OfficialActionType,
        model_used: str
    ):
        """
        Convertit un événement vers le format imposé et appelle log_experiment()
        """
        try:
            # Extraire ou créer les champs obligatoires
            input_prompt = event.data.get("input_prompt", "")
            output_response = event.data.get("output_response", "")
            
            # Si manquants, créer des placeholders pour conformité
            if not input_prompt:
                input_prompt = f"[Auto-generated] {event.event_type} on {event.data.get('file', 'unknown')}"
            if not output_response:
                output_response = f"[Auto-generated] Result: {event.success}"
            
            # Préparer les détails
            details = {
                "input_prompt": input_prompt,
                "output_response": output_response,
                **{k: v for k, v in event.data.items() if k not in ["input_prompt", "output_response"]}
            }
            
            # Appeler le logger imposé
            log_experiment(
                agent_name=event.agent_name,
                model_used=model_used,
                action=action_type,
                details=details,
                status="SUCCESS" if event.success else "FAILURE"
            )
        except Exception as e:
            print(f"⚠️  Erreur lors du logging vers le système imposé: {e}")
    
    def start_iteration(self, iteration_number: int):
        """Marque le début d'une itération"""
        self.current_iteration = iteration_number
        self.track_event(
            EventType.ITERATION_START,
            "system",
            {"iteration": iteration_number}
        )
    
    def end_iteration(self, iteration_number: int, success: bool):
        """Marque la fin d'une itération"""
        self.track_event(
            EventType.ITERATION_END,
            "system",
            {"iteration": iteration_number, "success": success},
            success=success
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Calcule les métriques globales"""
        total_events = len(self.events)
        successful_events = sum(1 for e in self.events if e.success)
        
        return {
            "session_id": self.session_id,
            "total_events": total_events,
            "successful_events": successful_events,
            "current_iteration": self.current_iteration
        }
    
    def _save_to_disk(self):
        """Sauvegarde les données (télémétrie étendue)"""
        if not self.log_file:
            return
        
        data = {
            "metadata": {
                "session_id": self.session_id,
                "start_time": self.start_time,
                "last_update": datetime.now().isoformat(),
            },
            "events": [asdict(event) for event in self.events]
        }
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def finalize(self):
        """Finalise et sauvegarde"""
        self._save_to_disk()
    
    def reset(self):
        """Réinitialise (pour tests)"""
        with self._lock:
            self.events.clear()
            self.session_id = str(uuid.uuid4())
            self.start_time = datetime.now().isoformat()
            self.current_iteration = 0
