"""
Outils d'analyse de code (pylint)
"""
from pathlib import Path
from typing import Dict, List
import subprocess
import json

class CodeAnalyzer:
    """Analyseur de code utilisant pylint"""
    
    def __init__(self, sandbox_dir: str):
        self.sandbox_dir = Path(sandbox_dir).resolve()
    
    def analyze_file(self, file_path: str) -> Dict:
        """
        Analyse un fichier Python avec pylint
        
        Args:
            file_path: Chemin relatif du fichier dans le sandbox
            
        Returns:
            Dictionnaire contenant le score et les problèmes détectés
        """
        full_path = self.sandbox_dir / file_path
        
        if not full_path.exists():
            return {
                "error": f"Fichier non trouvé: {file_path}",
                "score": 0,
                "issues": []
            }
        
        try:
            # Exécuter pylint avec sortie JSON
            result = subprocess.run(
                ['pylint', str(full_path), '--output-format=json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parser les résultats
            issues = json.loads(result.stdout) if result.stdout else []
            
            # Extraire le score
            score_result = subprocess.run(
                ['pylint', str(full_path), '--score=y'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            score = self._extract_score(score_result.stdout)
            
            return {
                "file": file_path,
                "score": score,
                "issues": issues,
                "issue_count": len(issues)
            }
            
        except subprocess.TimeoutExpired:
            return {
                "error": "Timeout lors de l'analyse",
                "score": 0,
                "issues": []
            }
        except Exception as e:
            return {
                "error": str(e),
                "score": 0,
                "issues": []
            }
    
    def _extract_score(self, output: str) -> float:
        """Extrait le score pylint de la sortie"""
        for line in output.split('\n'):
            if 'Your code has been rated at' in line:
                try:
                    score_str = line.split('rated at')[1].split('/')[0].strip()
                    return float(score_str)
                except:
                    pass
        return 0.0
    
    def analyze_all_files(self) -> List[Dict]:
        """Analyse tous les fichiers Python du sandbox"""
        results = []
        for py_file in self.sandbox_dir.rglob("*.py"):
            rel_path = py_file.relative_to(self.sandbox_dir)
            result = self.analyze_file(str(rel_path))
            results.append(result)
        return results
