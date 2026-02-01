"""
Logger Protocol - Système de logging OBLIGATOIRE selon la fiche technique
Ce fichier est IMPOSÉ et ne doit pas être modifié dans sa structure
"""
import json
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional
import threading


class ActionType(Enum):
    """
    Types d'actions standardisés (IMPOSÉS par la fiche technique)
    NE PAS MODIFIER CES VALEURS
    """
    ANALYSIS = "analysis"      # Lecture et analyse du code
    GENERATION = "generation"  # Création de nouveau contenu
    DEBUG = "debug"           # Analyse d'erreurs
    FIX = "fix"              # Correction/Refactoring du code


class ExperimentLogger:
    """
    Logger centralisé pour le protocole de logging imposé
    Thread-safe, Singleton pattern
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
            self.logs: list = []
            self.log_file: Optional[Path] = None
            self.session_id = str(uuid.uuid4())
            self.start_time = datetime.now().isoformat()
            self._initialized = True
    
    def initialize(self, log_dir: Path = None):
        """
        Initialise le système de logging
        
        Args:
            log_dir: Répertoire des logs (défaut: logs/)
        """
        if log_dir is None:
            log_dir = Path("logs")
        
        log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = log_dir / "experiment_data.json"
        
        # Créer le fichier initial
        self._save_to_disk()
    
    def log_entry(
        self,
        agent_name: str,
        model_used: str,
        action: ActionType,
        details: Dict[str, Any],
        status: str = "SUCCESS"
    ) -> str:
        """
        Enregistre une entrée de log (méthode interne)
        
        Args:
            agent_name: Nom de l'agent
            model_used: Modèle LLM utilisé
            action: Type d'action (ActionType)
            details: Détails avec input_prompt et output_response OBLIGATOIRES
            status: Statut (SUCCESS/FAILURE)
            
        Returns:
            ID de l'entrée créée
        """
        # Validation STRICTE des champs obligatoires
        if "input_prompt" not in details:
            raise ValueError(
                "❌ ERREUR CRITIQUE: Le champ 'input_prompt' est OBLIGATOIRE dans details.\n"
                "Votre programme s'arrête pour respecter le protocole de logging."
            )
        
        if "output_response" not in details:
            raise ValueError(
                "❌ ERREUR CRITIQUE: Le champ 'output_response' est OBLIGATOIRE dans details.\n"
                "Votre programme s'arrête pour respecter le protocole de logging."
            )
        
        with self._lock:
            entry_id = str(uuid.uuid4())
            
            log_entry = {
                "log_id": entry_id,
                "timestamp": datetime.now().isoformat(),
                "agent_name": agent_name,
                "model_used": model_used,
                "action": action.value,
                "status": status,
                "details": details
            }
            
            self.logs.append(log_entry)
            
            # Sauvegarde incrémentale toutes les 3 entrées
            if len(self.logs) % 3 == 0:
                self._save_to_disk()
            
            return entry_id
    
    def _save_to_disk(self):
        """Sauvegarde les logs sur disque"""
        if not self.log_file:
            return
        
        data = {
            "session_id": self.session_id,
            "start_time": self.start_time,
            "last_update": datetime.now().isoformat(),
            "total_logs": len(self.logs),
            "logs": self.logs
        }
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def finalize(self):
        """Finalise et sauvegarde les logs"""
        self._save_to_disk()
        print(f"✅ Logs sauvegardés dans: {self.log_file}")
        print(f"📊 Total d'entrées: {len(self.logs)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques des logs"""
        if not self.logs:
            return {"total": 0}
        
        stats = {
            "total_logs": len(self.logs),
            "success_count": sum(1 for log in self.logs if log["status"] == "SUCCESS"),
            "failure_count": sum(1 for log in self.logs if log["status"] == "FAILURE"),
            "agents": list(set(log["agent_name"] for log in self.logs)),
            "actions": {}
        }
        
        for log in self.logs:
            action = log["action"]
            stats["actions"][action] = stats["actions"].get(action, 0) + 1
        
        return stats


# Instance globale (Singleton)
_logger_instance = ExperimentLogger()


def log_experiment(
    agent_name: str,
    model_used: str,
    action: ActionType,
    details: Dict[str, Any],
    status: str = "SUCCESS"
) -> str:
    """
    Fonction PRINCIPALE de logging (API publique imposée)
    
    Args:
        agent_name: Nom de l'agent exécutant l'action
        model_used: Modèle LLM utilisé (ex: "gemini-2.5-flash")
        action: Type d'action (DOIT être un ActionType)
        details: Dictionnaire avec AU MINIMUM:
            - "input_prompt" (str): Prompt envoyé au LLM (OBLIGATOIRE)
            - "output_response" (str): Réponse du LLM (OBLIGATOIRE)
            + autres champs optionnels selon le contexte
        status: "SUCCESS" ou "FAILURE"
    
    Returns:
        ID unique de l'entrée créée
    
    Exemple:
        log_experiment(
            agent_name="Auditor_Agent",
            model_used="gemini-2.5-flash",
            action=ActionType.ANALYSIS,
            details={
                "file_analyzed": "messy_code.py",
                "input_prompt": "Tu es un expert Python. Analyse ce code...",
                "output_response": "J'ai détecté une absence de docstring...",
                "issues_found": 3
            },
            status="SUCCESS"
        )
    """
    return _logger_instance.log_entry(agent_name, model_used, action, details, status)


def initialize_logger(log_dir: Path = None):
    """
    Initialise le système de logging
    À appeler au début de main.py
    
    Args:
        log_dir: Répertoire des logs (défaut: logs/)
    """
    _logger_instance.initialize(log_dir)


def finalize_logger():
    """
    Finalise et sauvegarde les logs
    À appeler à la fin de main.py
    """
    _logger_instance.finalize()


def get_logger_stats() -> Dict[str, Any]:
    """Retourne les statistiques du logger"""
    return _logger_instance.get_stats()