"""
Outils de manipulation de fichiers sécurisés
"""
from pathlib import Path
from typing import Optional, List
import os

class FileOperations:
    """Classe pour les opérations sur les fichiers avec sécurité sandbox"""
    
    def __init__(self, sandbox_dir: str):
        """
        Initialise les opérations de fichiers
        
        Args:
            sandbox_dir: Répertoire racine autorisé pour les opérations
        """
        self.sandbox_dir = Path(sandbox_dir).resolve()
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
    
    def _validate_path(self, file_path: str) -> Path:
        """
        Valide qu'un chemin est dans le sandbox
        
        Args:
            file_path: Chemin à valider
            
        Returns:
            Path résolu et validé
            
        Raises:
            SecurityError: Si le chemin sort du sandbox
        """
        resolved = (self.sandbox_dir / file_path).resolve()
        
        if not str(resolved).startswith(str(self.sandbox_dir)):
            raise SecurityError(f"Accès refusé: {file_path} est hors du sandbox")
        
        return resolved
    
    def read_file(self, file_path: str) -> str:
        """Lit le contenu d'un fichier"""
        path = self._validate_path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def write_file(self, file_path: str, content: str):
        """Écrit du contenu dans un fichier"""
        path = self._validate_path(file_path)
        
        # Créer les répertoires parents si nécessaire
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def list_python_files(self) -> List[str]:
        """Liste tous les fichiers Python dans le sandbox"""
        python_files = []
        for path in self.sandbox_dir.rglob("*.py"):
            rel_path = path.relative_to(self.sandbox_dir)
            python_files.append(str(rel_path))
        return python_files
    
    def file_exists(self, file_path: str) -> bool:
        """Vérifie si un fichier existe"""
        try:
            path = self._validate_path(file_path)
            return path.exists()
        except SecurityError:
            return False

class SecurityError(Exception):
    """Exception levée pour les violations de sécurité du sandbox"""
    pass
