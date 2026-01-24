"""
=============================================================================
TOOLS - LES OUTILS DE L'ORCHESTRATION
=============================================================================
Responsable: Sérine (Ingénieur Outils) + Orchestrateur
Rôle: Fournir les fonctions que les agents utilisent
=============================================================================
"""

import os
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import google.generativeai as genai
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


# ═════════════════════════════════════════════════════════════════════════
# 1. CONFIGURATION GEMINI
# ═════════════════════════════════════════════════════════════════════════

def configure_gemini() -> str:
    """
    Configure Gemini et retourne la clé API.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "❌ ERREUR: Variable d'environnement GOOGLE_API_KEY non trouvée. "
            "Vérifiez votre fichier .env"
        )
    genai.configure(api_key=api_key)
    return api_key


# ═════════════════════════════════════════════════════════════════════════
# 2. INTERACTIONS AVEC GEMINI
# ═════════════════════════════════════════════════════════════════════════

def call_gemini(system_prompt: str, user_message: str, model: str = "gemini-2.0-flash") -> str:
    """
    Appelle Gemini avec un système prompt et un message utilisateur.
    
    Args:
        system_prompt (str): Instructions système pour le LLM
        user_message (str): Message de l'utilisateur
        model (str): Modèle Gemini à utiliser
    
    Returns:
        str: Réponse du LLM
    """
    try:
        api_key = configure_gemini()
        
        # Créer le modèle
        model_instance = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_prompt
        )
        
        # Appeler l'API
        response = model_instance.generate_content(user_message)
        
        # Retourner le texte
        return response.text
    
    except Exception as e:
        print(f"❌ Erreur Gemini: {str(e)}")
        raise


# ═════════════════════════════════════════════════════════════════════════
# 3. GESTION DES FICHIERS
# ═════════════════════════════════════════════════════════════════════════

def read_files(target_dir: str) -> Dict[str, str]:
    """
    Lit tous les fichiers Python d'un dossier.
    
    Args:
        target_dir (str): Chemin du dossier
    
    Returns:
        Dict[str, str]: {chemin_relatif: contenu}
    """
    files_content = {}
    
    # Chercher tous les fichiers .py
    python_files = Path(target_dir).rglob("*.py")
    
    for file_path in python_files:
        # Ignorer __pycache__
        if "__pycache__" in str(file_path):
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                relative_path = str(file_path.relative_to(target_dir))
                files_content[relative_path] = f.read()
        except Exception as e:
            print(f"⚠️ Erreur lecture {file_path}: {e}")
    
    return files_content


def read_file(file_path: str) -> str:
    """
    Lit un fichier spécifique.
    
    Args:
        file_path (str): Chemin du fichier
    
    Returns:
        str: Contenu du fichier
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise Exception(f"Erreur lecture {file_path}: {e}")


def write_file(file_path: str, content: str) -> bool:
    """
    Écrit du contenu dans un fichier.
    
    Args:
        file_path (str): Chemin du fichier
        content (str): Contenu à écrire
    
    Returns:
        bool: True si succès
    """
    try:
        # Créer les répertoires parents s'ils n'existent pas
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"❌ Erreur écriture {file_path}: {e}")
        return False


# ═════════════════════════════════════════════════════════════════════════
# 4. ANALYSE AVEC PYLINT
# ═════════════════════════════════════════════════════════════════════════

def run_pylint(target_dir: str) -> Tuple[float, str]:
    """
    Lance pylint sur un dossier et retourne le score.
    
    Args:
        target_dir (str): Chemin du dossier
    
    Returns:
        Tuple[float, str]: (score, rapport)
    """
    try:
        # Vérifier que pylint est installé
        result = subprocess.run(
            ["pylint", target_dir, "--disable=all", "--enable=E", "-rn"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout + result.stderr
        
        # Chercher le score dans la sortie
        if "Your code has been rated at" in output:
            # Extraire le score (ex: "Your code has been rated at 7.5/10")
            parts = output.split("Your code has been rated at")
            if len(parts) > 1:
                score_str = parts[1].split("/")[0].strip()
                try:
                    score = float(score_str)
                    return score, output
                except:
                    return 0.0, output
        
        return 0.0, output
    
    except subprocess.TimeoutExpired:
        return 0.0, "❌ Timeout pylint (>30s)"
    except FileNotFoundError:
        return 0.0, "❌ pylint non installé. Installez: pip install pylint"
    except Exception as e:
        return 0.0, f"❌ Erreur pylint: {str(e)}"


# ═════════════════════════════════════════════════════════════════════════
# 5. TESTS AVEC PYTEST
# ═════════════════════════════════════════════════════════════════════════

def run_pytest(target_dir: str) -> Tuple[bool, str]:
    """
    Lance pytest sur un dossier.
    
    Args:
        target_dir (str): Chemin du dossier
    
    Returns:
        Tuple[bool, str]: (succès, rapport)
    """
    try:
        # Vérifier que pytest est installé
        result = subprocess.run(
            ["pytest", target_dir, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        output = result.stdout + result.stderr
        passed = result.returncode == 0
        
        return passed, output
    
    except subprocess.TimeoutExpired:
        return False, "❌ Timeout pytest (>60s)"
    except FileNotFoundError:
        return False, "❌ pytest non installé. Installez: pip install pytest"
    except Exception as e:
        return False, f"❌ Erreur pytest: {str(e)}"


# ═════════════════════════════════════════════════════════════════════════
# 6. UTILITAIRES
# ═════════════════════════════════════════════════════════════════════════

def load_prompt(prompt_file: str) -> str:
    """
    Charge un fichier prompt.
    
    Args:
        prompt_file (str): Chemin du fichier prompt
    
    Returns:
        str: Contenu du prompt
    """
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise Exception(f"Prompt non trouvé: {prompt_file}")


def validate_json_output(text: str) -> dict:
    """
    Extrait et valide du JSON d'une réponse LLM.
    
    Args:
        text (str): Texte contenant du JSON
    
    Returns:
        dict: Données JSON parsées
    """
    try:
        # Chercher les accolades
        start = text.find('{')
        end = text.rfind('}')
        
        if start == -1 or end == -1:
            raise ValueError("Pas de JSON trouvé")
        
        json_str = text[start:end+1]
        return json.loads(json_str)
    
    except json.JSONDecodeError as e:
        raise Exception(f"JSON invalide: {str(e)}")


def copy_directory(src: str, dst: str) -> bool:
    """
    Copie un répertoire (pour créer des sandboxes).
    
    Args:
        src (str): Source
        dst (str): Destination
    
    Returns:
        bool: Succès
    """
    try:
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        return True
    except Exception as e:
        print(f"❌ Erreur copie: {e}")
        return False


# ═════════════════════════════════════════════════════════════════════════
# TEST
# ═════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("✅ Module tools.py chargé avec succès")
