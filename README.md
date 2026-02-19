# The Refactoring Swarm 🤖

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Framework-green.svg)](https://github.com/langchain-ai/langgraph)
[![Claude](https://img.shields.io/badge/Claude-Sonnet%204-purple.svg)](https://www.anthropic.com/)

**Projet de TP IGL - ESI 2025/2026**

Système multi-agents autonomes pour le refactoring automatique de code Python.

## 🎯 Résultats des Tests

| Test Case      | Status      | Iterations | Quality Score |
| -------------- | ----------- | ---------- | ------------- |
| case01_syntax  | ✅ PASSED   | 1          | Auto-fixed    |
| case02_logic   | ✅ PASSED   | 1          | Complex logic |
| case03_quality | ✅ PASSED   | 1          | Improved      |
| case04_complex | ⚠️ MAX_ITER | 15         | Multi-issue   |

**Taux de réussite:** 75% (3/4 tests passés automatiquement)

## 🏗️ Architecture

- **Auditor Agent:** Analyse le code avec Pylint et Claude
- **Fixer Agent:** Applique les corrections intelligentes
- **Judge Agent:** Valide avec Pytest et Pylint
- **Orchestrator:** Gère le workflow avec LangGraph
- **Data Officer:** Logging et métriques complètes

## 🏗️ Architecture Détaillée

### Workflow du Système

## 📦 Installation

1. Créer un environnement virtuel:

```bash
python -m venv venv
```

2. Activer l'environnement:

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Installer les dépendances:

```bash
pip install -r requirements.txt
```

4. Configurer l'API key:

```bash
# Copier .env.example vers .env
# Ajouter votre ANTHROPIC_API_KEY ou ANTHROPIC_API_KEY=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

```

5. Vérifier l'installation:

```bash
python check_setup.py
python check_data_officer.py
```

## 🚀 Utilisation

### Lancer un test simple:

```bash
python main.py --target_dir test_cases/case03_quality
```

### Lancer tous les tests:

```bash
python run_all_tests.py
```

### Vérifier les logs:

```bash
python check_data_officer.py
python test_my_role_simple.py
```

## 📊 Data Officer (Logging)

Tous les appels LLM sont automatiquement loggés dans `logs/experiment_data.json` avec:

- ✅ 4 ActionType obligatoires (ANALYSIS, GENERATION, DEBUG, FIX)
- ✅ input_prompt et output_response validés
- ✅ Métriques de performance par agent
- ✅ TelemetryTracker intégré

## 🔧 Structure du Projet
