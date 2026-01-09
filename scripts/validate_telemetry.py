"""
Script de validation de télémétrie
Responsable: Data Officer
"""
import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools.data_validator import DataValidator
from tools.metrics_analyzer import MetricsAnalyzer


def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Valide et analyse les données de télémétrie"
    )
    parser.add_argument(
        "log_file",
        type=Path,
        help="Chemin vers experiment_data.json"
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Fichier de sortie pour le rapport détaillé"
    )
    parser.add_argument(
        "--export",
        type=Path,
        help="Exporter les métriques pour visualisation"
    )
    
    args = parser.parse_args()
    
    # Validation
    print("🔍 Validation du fichier de télémétrie...\n")
    report = DataValidator.generate_report(args.log_file)
    print(report)
    
    is_valid, errors = DataValidator.validate_file(args.log_file)
    
    if not is_valid:
        print("\n❌ VALIDATION ÉCHOUÉE")
        sys.exit(1)
    
    # Analyse des métriques
    print("\n📊 Analyse des métriques...\n")
    analyzer = MetricsAnalyzer(args.log_file)
    summary = analyzer.generate_summary_report()
    print(summary)
    
    # Sauvegarder le rapport si demandé
    if args.report:
        with open(args.report, 'w', encoding='utf-8') as f:
            f.write(report)
            f.write("\n\n")
            f.write(summary)
        print(f"\n💾 Rapport sauvegardé dans: {args.report}")
    
    # Exporter pour visualisation si demandé
    if args.export:
        analyzer.export_for_visualization(args.export)
        print(f"📈 Données exportées pour visualisation: {args.export}")
    
    print("\n✅ Validation et analyse terminées avec succès!")


if __name__ == "__main__":
    main()
