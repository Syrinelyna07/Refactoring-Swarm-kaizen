"""
Test Dataset Generator - Génère des cas de test avec du code buggé
Responsable: Data Officer
"""
from pathlib import Path
from typing import List


class TestCase:
    """Représente un cas de test avec du code buggé"""
    
    def __init__(self, name: str, description: str, code: str, expected_issues: List[str]):
        self.name = name
        self.description = description
        self.code = code
        self.expected_issues = expected_issues


class TestDatasetGenerator:
    """Générateur de jeu de données de test"""
    
    # Cas de test prédéfinis
    TEST_CASES = [
        TestCase(
            name="case01_syntax_errors",
            description="Code avec erreurs de syntaxe basiques",
            code="""# filepath: test_module.py
def calculate_sum(a, b)
    return a + b

def multiply(x, y):
    result = x * y
    print(result
    return result

class Calculator
    def add(self, a, b):
        return a + b
""",
            expected_issues=["SyntaxError", "missing colon", "missing parenthesis"]
        ),
        
        TestCase(
            name="case02_undefined_variables",
            description="Utilisation de variables non définies",
            code="""# filepath: math_operations.py
def process_data(data):
    result = []
    for item in data:
        processed = item * factor  # factor n'est pas défini
        result.append(processed)
    return result

def calculate_average():
    total = sum(numbers)  # numbers n'est pas défini
    return total / count  # count n'est pas défini
""",
            expected_issues=["NameError", "undefined variable"]
        ),
        
        TestCase(
            name="case03_import_errors",
            description="Imports manquants ou incorrects",
            code="""# filepath: data_processor.py
import pandas
from numpy import array
from non_existent_module import something  # Module inexistant

def process_dataframe(df):
    # pandas utilisé sans alias
    result = pd.DataFrame(df)  # NameError: pd n'est pas défini
    return result

def create_array(data):
    return array(data)
""",
            expected_issues=["ImportError", "ModuleNotFoundError", "NameError"]
        ),
        
        TestCase(
            name="case04_type_errors",
            description="Erreurs de types et opérations invalides",
            code="""# filepath: type_issues.py
def concatenate_strings(a, b):
    return a + b

def bad_operations():
    number = 42
    text = "Hello"
    result = number + text  # TypeError
    
    items = [1, 2, 3]
    value = items[10]  # IndexError
    
    data = {"key": "value"}
    x = data["missing"]  # KeyError
    
    return result
""",
            expected_issues=["TypeError", "IndexError", "KeyError"]
        ),
        
        TestCase(
            name="case05_code_quality_issues",
            description="Code fonctionnel mais de mauvaise qualité",
            code="""# filepath: quality_issues.py
def VeryLongFunctionNameThatDoesNotFollowPythonConventions(param1,param2,param3,param4,param5):
    x=param1+param2+param3+param4+param5
    if x>100:
        if x<200:
            if x!=150:
                return True
            else:
                return False
        else:
            return False
    else:
        return False

def unused_function():
    pass

a=1
b=2
c=3
GLOBAL_VAR=100

def function_with_many_locals():
    var1=1
    var2=2
    var3=3
    var4=4
    var5=5
    var6=6
    var7=7
    var8=8
    var9=9
    var10=10
    var11=11
    var12=12
    var13=13
    var14=14
    var15=15
    var16=16
    var17=17
    var18=18
    var19=19
    var20=20
    return var1+var2+var3
""",
            expected_issues=["naming convention", "complexity", "too many locals", "line too long"]
        ),
        
        TestCase(
            name="case06_no_documentation",
            description="Code sans documentation ni tests",
            code="""# filepath: undocumented.py
def complex_algorithm(data, threshold, mode):
    if mode == 'fast':
        return [x for x in data if x > threshold]
    elif mode == 'accurate':
        result = []
        for item in data:
            if item > threshold * 1.5:
                result.append(item ** 2)
        return result
    else:
        return data

class DataProcessor:
    def __init__(self, config):
        self.config = config
        self.results = []
    
    def process(self, items):
        for item in items:
            if self._validate(item):
                self.results.append(self._transform(item))
        return self.results
    
    def _validate(self, item):
        return item is not None
    
    def _transform(self, item):
        return item * 2
""",
            expected_issues=["missing docstring", "no tests", "undocumented"]
        ),
        
        TestCase(
            name="case07_logic_errors",
            description="Erreurs de logique subtiles",
            code="""# filepath: logic_bugs.py
def find_maximum(numbers):
    max_value = 0  # Bug: ne fonctionne pas avec des nombres négatifs
    for num in numbers:
        if num > max_value:
            max_value = num
    return max_value

def calculate_discount(price, discount_percent):
    discount = price * discount_percent  # Bug: oubli de diviser par 100
    return price - discount

def is_palindrome(text):
    return text == text[::-1]  # Bug: sensible à la casse

def divide_list(items, chunk_size):
    chunks = []
    for i in range(0, len(items), chunk_size):
        chunks.append(items[i:i+chunk_size])
    return chunks[:-1]  # Bug: perd le dernier chunk
""",
            expected_issues=["logic error", "incorrect calculation", "edge case"]
        ),
        
        TestCase(
            name="case08_security_issues",
            description="Problèmes de sécurité potentiels",
            code="""# filepath: security_issues.py
import pickle
import os

def load_data(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)  # Unsafe deserialization

def execute_command(user_input):
    os.system(user_input)  # Command injection vulnerability

def build_query(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection
    return query

PASSWORD = "admin123"  # Hardcoded password

def authenticate(username, password):
    if password == PASSWORD:
        return True
    return False
""",
            expected_issues=["security", "pickle", "os.system", "hardcoded password"]
        )
    ]
    
    @classmethod
    def generate_dataset(cls, output_dir: Path, num_cases: int = None):
        """
        Génère le jeu de données de test
        
        Args:
            output_dir: Répertoire de sortie
            num_cases: Nombre de cas à générer (None = tous)
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        cases_to_generate = cls.TEST_CASES if num_cases is None else cls.TEST_CASES[:num_cases]
        
        for test_case in cases_to_generate:
            case_dir = output_dir / test_case.name
            case_dir.mkdir(exist_ok=True)
            
            # Créer le fichier de code buggé
            code_file = case_dir / "buggy_code.py"
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(test_case.code)
            
            # Créer le fichier de métadonnées
            metadata_file = case_dir / "metadata.json"
            import json
            metadata = {
                "name": test_case.name,
                "description": test_case.description,
                "expected_issues": test_case.expected_issues,
                "difficulty": cls._estimate_difficulty(test_case)
            }
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            # Créer un README
            readme_file = case_dir / "README.md"
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(f"# {test_case.name}\n\n")
                f.write(f"**Description:** {test_case.description}\n\n")
                f.write(f"**Problèmes attendus:**\n")
                for issue in test_case.expected_issues:
                    f.write(f"- {issue}\n")
        
        # Créer un index
        cls._create_index(output_dir, cases_to_generate)
    
    @staticmethod
    def _estimate_difficulty(test_case: TestCase) -> str:
        """Estime la difficulté d'un cas de test"""
        num_issues = len(test_case.expected_issues)
        if num_issues <= 2:
            return "easy"
        elif num_issues <= 4:
            return "medium"
        else:
            return "hard"
    
    @staticmethod
    def _create_index(output_dir: Path, cases: List[TestCase]):
        """Crée un fichier index pour le dataset"""
        import json
        
        index = {
            "total_cases": len(cases),
            "cases": [
                {
                    "name": case.name,
                    "description": case.description,
                    "difficulty": TestDatasetGenerator._estimate_difficulty(case),
                    "expected_issues_count": len(case.expected_issues)
                }
                for case in cases
            ]
        }
        
        with open(output_dir / "index.json", 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2)
        
        # Créer aussi un README général
        with open(output_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write("# Test Dataset - The Refactoring Swarm\n\n")
            f.write(f"Ce dataset contient {len(cases)} cas de test avec du code buggé.\n\n")
            f.write("## Cas de test disponibles\n\n")
            for case in cases:
                f.write(f"### {case.name}\n")
                f.write(f"{case.description}\n\n")
