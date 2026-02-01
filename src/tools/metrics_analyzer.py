"""
Metrics Analyzer - Analyse et visualise les métriques de performance
Responsable: Data Officer
"""
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict


class MetricsAnalyzer:
    """Analyseur de métriques pour les données de télémétrie"""
    
    def __init__(self, log_file: Path):
        """
        Initialise l'analyseur
        
        Args:
            log_file: Chemin vers experiment_data.json
        """
        self.log_file = log_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Charge les données depuis le fichier"""
        if not self.log_file.exists():
            raise FileNotFoundError(f"Le fichier {self.log_file} n'existe pas")
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_agent_performance(self) -> Dict[str, Any]:
        """
        Analyse les performances de chaque agent
        
        Returns:
            Statistiques par agent
        """
        agent_stats = defaultdict(lambda: {
            "total_actions": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "average_duration_ms": 0,
            "total_duration_ms": 0,
            "event_types": defaultdict(int)
        })
        
        for event in self.data.get("events", []):
            agent = event["agent_name"]
            agent_stats[agent]["total_actions"] += 1
            
            if event["success"]:
                agent_stats[agent]["successful_actions"] += 1
            else:
                agent_stats[agent]["failed_actions"] += 1
            
            if event.get("duration_ms"):
                agent_stats[agent]["total_duration_ms"] += event["duration_ms"]
            
            agent_stats[agent]["event_types"][event["event_type"]] += 1
        
        # Calculer les moyennes
        for agent, stats in agent_stats.items():
            if stats["total_actions"] > 0:
                stats["success_rate"] = stats["successful_actions"] / stats["total_actions"]
                stats["average_duration_ms"] = stats["total_duration_ms"] / stats["total_actions"]
        
        return dict(agent_stats)
    
    def get_iteration_analysis(self) -> List[Dict[str, Any]]:
        """
        Analyse les performances par itération
        
        Returns:
            Liste des statistiques par itération
        """
        iterations = defaultdict(lambda: {
            "iteration": 0,
            "events_count": 0,
            "successful_events": 0,
            "failed_events": 0,
            "agents_involved": set(),
            "start_time": None,
            "end_time": None
        })
        
        for event in self.data.get("events", []):
            iter_num = event["iteration"]
            iterations[iter_num]["iteration"] = iter_num
            iterations[iter_num]["events_count"] += 1
            
            if event["success"]:
                iterations[iter_num]["successful_events"] += 1
            else:
                iterations[iter_num]["failed_events"] += 1
            
            iterations[iter_num]["agents_involved"].add(event["agent_name"])
            
            # Tracker les timestamps
            timestamp = event["timestamp"]
            if not iterations[iter_num]["start_time"]:
                iterations[iter_num]["start_time"] = timestamp
            iterations[iter_num]["end_time"] = timestamp
        
        # Convertir les sets en listes pour la sérialisation JSON
        result = []
        for iter_data in sorted(iterations.values(), key=lambda x: x["iteration"]):
            iter_data["agents_involved"] = list(iter_data["agents_involved"])
            iter_data["success_rate"] = (
                iter_data["successful_events"] / iter_data["events_count"]
                if iter_data["events_count"] > 0 else 0
            )
            result.append(iter_data)
        
        return result
    
    def get_quality_evolution(self) -> List[Dict[str, Any]]:
        """
        Trace l'évolution de la qualité du code
        
        Returns:
            Liste des métriques de qualité chronologiques
        """
        quality_metrics = []
        
        for event in self.data.get("events", []):
            if event["event_type"] == "quality_metric":
                quality_metrics.append({
                    "timestamp": event["timestamp"],
                    "iteration": event["iteration"],
                    "score": event["data"].get("score", 0),
                    "file": event["data"].get("file", "unknown")
                })
        
        return quality_metrics
    
    def get_error_analysis(self) -> Dict[str, Any]:
        """
        Analyse les erreurs rencontrées
        
        Returns:
            Statistiques sur les erreurs
        """
        errors_by_agent = defaultdict(list)
        errors_by_type = defaultdict(int)
        total_errors = 0
        
        for event in self.data.get("events", []):
            if not event["success"] and event.get("error_message"):
                total_errors += 1
                errors_by_agent[event["agent_name"]].append({
                    "timestamp": event["timestamp"],
                    "iteration": event["iteration"],
                    "error_message": event["error_message"],
                    "event_type": event["event_type"]
                })
                errors_by_type[event["event_type"]] += 1
        
        return {
            "total_errors": total_errors,
            "errors_by_agent": dict(errors_by_agent),
            "errors_by_type": dict(errors_by_type)
        }
    
    def generate_summary_report(self) -> str:
        """
        Génère un rapport résumé complet
        
        Returns:
            Rapport textuel formaté
        """
        lines = []
        lines.append("=" * 80)
        lines.append("RAPPORT D'ANALYSE DES MÉTRIQUES - THE REFACTORING SWARM")
        lines.append("=" * 80)
        lines.append("")
        
        # Métadonnées
        metadata = self.data.get("metadata", {})
        lines.append("MÉTADONNÉES DE SESSION")
        lines.append("-" * 80)
        lines.append(f"Session ID: {metadata.get('session_id')}")
        lines.append(f"Début: {metadata.get('start_time')}")
        lines.append(f"Dernière mise à jour: {metadata.get('last_update')}")
        lines.append(f"Itérations totales: {metadata.get('current_iteration')}")
        lines.append(f"Événements totaux: {metadata.get('total_events')}")
        lines.append("")
        
        # Métriques globales
        metrics = self.data.get("metrics", {})
        lines.append("MÉTRIQUES GLOBALES")
        lines.append("-" * 80)
        lines.append(f"Événements réussis: {metrics.get('successful_events')}")
        lines.append(f"Événements échoués: {metrics.get('failed_events')}")
        lines.append(f"Taux de succès: {metrics.get('success_rate', 0):.2%}")
        lines.append("")
        
        # Performance par agent
        agent_perf = self.get_agent_performance()
        lines.append("PERFORMANCE PAR AGENT")
        lines.append("-" * 80)
        for agent, stats in agent_perf.items():
            lines.append(f"\n{agent}:")
            lines.append(f"  - Actions totales: {stats['total_actions']}")
            lines.append(f"  - Taux de succès: {stats.get('success_rate', 0):.2%}")
            lines.append(f"  - Durée moyenne: {stats.get('average_duration_ms', 0):.2f} ms")
        lines.append("")
        
        # Analyse des itérations
        iterations = self.get_iteration_analysis()
        lines.append("ANALYSE PAR ITÉRATION")
        lines.append("-" * 80)
        for iter_data in iterations:
            lines.append(f"\nItération {iter_data['iteration']}:")
            lines.append(f"  - Événements: {iter_data['events_count']}")
            lines.append(f"  - Taux de succès: {iter_data['success_rate']:.2%}")
            lines.append(f"  - Agents impliqués: {', '.join(iter_data['agents_involved'])}")
        lines.append("")
        
        # Analyse des erreurs
        error_analysis = self.get_error_analysis()
        lines.append("ANALYSE DES ERREURS")
        lines.append("-" * 80)
        lines.append(f"Erreurs totales: {error_analysis['total_errors']}")
        if error_analysis['errors_by_type']:
            lines.append("\nErreurs par type:")
            for error_type, count in error_analysis['errors_by_type'].items():
                lines.append(f"  - {error_type}: {count}")
        lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def export_for_visualization(self, output_file: Path):
        """
        Exporte les données dans un format optimisé pour la visualisation
        
        Args:
            output_file: Fichier de sortie
        """
        export_data = {
            "agent_performance": self.get_agent_performance(),
            "iteration_analysis": self.get_iteration_analysis(),
            "quality_evolution": self.get_quality_evolution(),
            "error_analysis": self.get_error_analysis()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
