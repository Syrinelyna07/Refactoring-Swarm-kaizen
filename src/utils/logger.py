"""
=============================================================================
LOGGER - Télémétrie & Expérimentation
=============================================================================
Responsable: Data Officer (Responsable Qualité & Data)
Rôle: Enregistrer toutes les actions dans logs/experiment_data.json
=============================================================================
"""

import json
import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

# Chemin du fichier de logs
LOGS_DIR = "logs"
LOG_FILE = os.path.join(LOGS_DIR, "experiment_data.json")


class ActionType(str, Enum):
    """
    Énumération des types d'actions possibles pour standardiser l'analyse.
    """
    ANALYSIS = "CODE_ANALYSIS"  # Audit, lecture, recherche de bugs
    GENERATION = "CODE_GEN"     # Création de nouveau code/tests/docs
    DEBUG = "DEBUG"             # Analyse d'erreurs d'exécution
    FIX = "FIX"                 # Application de correctifs
    VALIDATE = "VALIDATE"       # Tests et validation
    STARTUP = "STARTUP"         # Démarrage du système
    SHUTDOWN = "SHUTDOWN"       # Arrêt du système


def initialize_experiment_data():
    """
    ✅ Initialise le fichier experiment_data.json s'il n'existe pas.
    """
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)
    
    if not os.path.exists(LOG_FILE):
        initial_data = {
            "experiment_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "total_duration_seconds": None,
            "status": "IN_PROGRESS",
            "actions": [],
            "summary": {
                "total_actions": 0,
                "actions_by_agent": {},
                "errors_count": 0,
                "iterations": 0
            }
        }
        with open(LOG_FILE, "w") as f:
            json.dump(initial_data, f, indent=2)


def log_experiment(agent_name: str, model_used: str, action: ActionType, details: dict, status: str):
    """
    Enregistre une interaction d'agent pour l'analyse scientifique.

    Args:
        agent_name (str): Nom de l'agent (ex: "Auditor", "Fixer").
        model_used (str): Modèle LLM utilisé (ex: "gemini-1.5-flash").
        action (ActionType): Le type d'action effectué (utiliser l'Enum ActionType).
        details (dict): Dictionnaire contenant les détails. DOIT contenir 'input_prompt' et 'output_response'.
        status (str): "SUCCESS" ou "FAILURE".

    Raises:
        ValueError: Si les champs obligatoires sont manquants dans 'details' ou si l'action est invalide.
    """
    
    # --- 1. VALIDATION DU TYPE D'ACTION ---
    # Permet d'accepter soit l'objet Enum, soit la chaîne de caractères correspondante
    valid_actions = [a.value for a in ActionType]
    if isinstance(action, ActionType):
        action_str = action.value
    elif action in valid_actions:
        action_str = action
    else:
        raise ValueError(f"❌ Action invalide : '{action}'. Utilisez la classe ActionType (ex: ActionType.FIX).")

    # --- 2. VALIDATION STRICTE DES DONNÉES (Prompts) ---
    # Pour l'analyse scientifique, nous avons absolument besoin du prompt et de la réponse
    # pour les actions impliquant une interaction majeure avec le code.
    if action_str in [ActionType.ANALYSIS.value, ActionType.GENERATION.value, ActionType.DEBUG.value, ActionType.FIX.value]:
        required_keys = ["input_prompt", "output_response"]
        missing_keys = [key for key in required_keys if key not in details]
        
        if missing_keys:
            raise ValueError(
                f"❌ Erreur de Logging (Agent: {agent_name}) : "
                f"Les champs {missing_keys} sont manquants dans le dictionnaire 'details'. "
                f"Ils sont OBLIGATOIRES pour valider le TP."
            )

    # --- 3. PRÉPARATION DE L'ENTRÉE ---
    # Création du dossier logs s'il n'existe pas
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    entry = {
        "id": str(uuid.uuid4()),  # ID unique pour éviter les doublons lors de la fusion des données
        "timestamp": datetime.now().isoformat(),
        "agent": agent_name,
        "model": model_used,
        "action": action_str,
        "details": details,
        "status": status
    }

    # --- 4. LECTURE & ÉCRITURE ROBUSTE ---
    data = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content: # Vérifie que le fichier n'est pas juste vide
                    data = json.loads(content)
        except json.JSONDecodeError:
            # Si le fichier est corrompu, on repart à zéro (ou on pourrait sauvegarder un backup)
            print(f"⚠️ Attention : Le fichier de logs {LOG_FILE} était corrompu. Une nouvelle liste a été créée.")
            data = []

    data.append(entry)
    
    # Écriture
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def finalize_experiment_data():
    """
    ✅ Finalise le fichier experiment_data.json avec timing et statut.
    """
    try:
        if not os.path.exists(LOG_FILE):
            return
        
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return
            experiment_data = json.loads(content)
        
        # Si c'est une liste (ancien format), retourner
        if isinstance(experiment_data, list):
            return
        
        # Ajouter le temps de fin
        experiment_data["end_time"] = datetime.now().isoformat()
        experiment_data["status"] = "COMPLETE"
        
        # Calculer la durée
        if experiment_data.get("start_time") and experiment_data.get("end_time"):
            start = datetime.fromisoformat(experiment_data["start_time"])
            end = datetime.fromisoformat(experiment_data["end_time"])
            duration = (end - start).total_seconds()
            experiment_data["total_duration_seconds"] = duration
        
        # Sauvegarder
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(experiment_data, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Logs finalisés dans {LOG_FILE}")
    
    except Exception as e:
        print(f"⚠️ ERREUR FINALISATION: {str(e)}")


def validate_experiment_data() -> bool:
    """
    ✅ Valide le schéma du fichier experiment_data.json.
    """
    try:
        if not os.path.exists(LOG_FILE):
            print(f"❌ Fichier {LOG_FILE} n'existe pas")
            return False
        
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
        
        # Si c'est une liste (ancien format), c'est OK
        if isinstance(data, list):
            print(f"✅ Format experiment_data.json valide (tableau)")
            return True
        
        # Nouveau format dictionnaire
        required_fields = ["experiment_id", "start_time", "actions", "summary"]
        for field in required_fields:
            if field not in data:
                print(f"❌ Champ obligatoire manquant: {field}")
                return False
        
        # Vérifier la structure des actions
        if not isinstance(data["actions"], list):
            print(f"❌ 'actions' doit être une liste")
            return False
        
        print(f"✅ Format experiment_data.json valide")
        return True
    
    except json.JSONDecodeError:
        print(f"❌ JSON invalide dans {LOG_FILE}")
        return False
    except Exception as e:
        print(f"❌ Erreur validation: {str(e)}")
        return False


# Initialiser à l'import
initialize_experiment_data()