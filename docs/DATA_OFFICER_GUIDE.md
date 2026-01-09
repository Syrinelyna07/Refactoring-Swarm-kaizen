# Guide d'Utilisation - Système de Télémétrie
**Responsable : Data Officer**

## 🎯 Pour les Autres Rôles

### Orchestrateur (Lead Dev)

Dans votre `main.py`, initialisez le logger :

```python
from src.utils.logger import initialize_logger, finalize_logger

def main():
    # Au début
    initialize_logger(Path("logs"))
    
    # ... votre code d'orchestration ...
    
    # À la fin
    finalize_logger()
```

### Toolsmith (Ingénieur Outils)

Quand vos outils sont appelés par un agent, loggez l'interaction :

```python
from src.utils.logger import log_experiment, ActionType

def analyze_code(file_path: str, llm_prompt: str, llm_response: str):
    # Votre logique...
    
    # Logger l'interaction LLM
    log_experiment(
        agent_name="Auditor_Agent",
        model_used="gemini-2.5-flash",
        action=ActionType.ANALYSIS,
        details={
            "input_prompt": llm_prompt,          # OBLIGATOIRE
            "output_response": llm_response,     # OBLIGATOIRE
            "file_analyzed": file_path,
            "issues_found": len(issues)
        },
        status="SUCCESS"
    )
```

### Prompt Engineer

Chaque fois qu'un agent utilise un prompt :

```python
from src.utils.logger import log_experiment, ActionType

# Après avoir reçu la réponse du LLM
log_experiment(
    agent_name="Fixer_Agent",
    model_used="gemini-2.5-flash",
    action=ActionType.FIX,
    details={
        "input_prompt": your_system_prompt + user_context,
        "output_response": llm_response,
        "file_modified": filepath,
        "prompt_version": "v2.1"
    },
    status="SUCCESS"
)
```

## 📊 Les 4 ActionType Imposés

```python
from src.utils.logger import ActionType

ActionType.ANALYSIS    # Lecture et analyse du code
ActionType.GENERATION  # Création de nouveau contenu (tests, docs)
ActionType.DEBUG       # Analyse d'erreurs et logs
ActionType.FIX         # Correction/Refactoring du code
```

## ⚠️ RÈGLE CRITIQUE

**Chaque appel à `log_experiment()` DOIT contenir :**
- `input_prompt` : Le prompt exact envoyé au LLM
- `output_response` : La réponse brute du LLM

Sinon, le programme s'arrêtera avec une erreur.

## 🧪 Validation

Pour valider vos logs :

```bash
python scripts/validate_telemetry.py logs/experiment_data.json
```

## 📈 Analyse des Métriques

Pour analyser les performances :

```python
from src.tools.metrics_analyzer import MetricsAnalyzer

analyzer = MetricsAnalyzer(Path("logs/experiment_data.json"))
report = analyzer.generate_summary_report()
print(report)
```

## 🗂️ Dataset de Test

Dataset disponible dans `test_dataset/` avec 8 cas :
1. `case01_syntax_errors` - Erreurs de syntaxe
2. `case02_undefined_variables` - Variables non définies
3. `case03_import_errors` - Imports manquants
4. `case04_type_errors` - Erreurs de types
5. `case05_code_quality_issues` - Problèmes de qualité
6. `case06_no_documentation` - Sans documentation
7. `case07_logic_errors` - Erreurs de logique
8. `case08_security_issues` - Problèmes de sécurité

Utilisez-les pour tester votre système avant la soumission finale.

## ❓ Questions / Support

Contactez le Data Officer pour toute question sur :
- Format des logs
- Validation JSON
- Métriques de performance
- Dataset de test
