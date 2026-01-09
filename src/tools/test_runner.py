"""
Outils d'exécution des tests (pytest)
"""
from pathlib import Path
import subprocess
from typing import Dict

class TestRunner:
    """Exécuteur de tests utilisant pytest"""
    
    def __init__(self, sandbox_dir: str):
        self.sandbox_dir = Path(sandbox_dir).resolve()
    
    def run_tests(self) -> Dict:
        """
        Exécute tous les tests pytest dans le sandbox
        
        Returns:
            Dictionnaire contenant les résultats des tests
        """
        try:
            result = subprocess.run(
                ['pytest', str(self.sandbox_dir), '-v', '--tb=short'],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.sandbox_dir)
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Timeout: les tests ont pris trop de temps",
                "return_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Erreur lors de l'exécution des tests: {str(e)}",
                "return_code": -1
            }
