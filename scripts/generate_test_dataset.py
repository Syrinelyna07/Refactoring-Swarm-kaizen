"""
Script de génération du dataset de test
Responsable: Data Officer
"""
import sys
from pathlib import Path

# Ajouter le répertoire tests au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.test_dataset_generator import TestDatasetGenerator


def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Génère un dataset de test avec du code buggé"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("test_dataset"),
        help="Répertoire de sortie (défaut: test_dataset)"
    )
    parser.add_argument(
        "--num-cases",
        type=int,
        default=None,
        help="Nombre de cas à générer (défaut: tous)"
    )
    
    args = parser.parse_args()
    
    print(f"🏗️  Génération du dataset de test...")
    print(f"📁 Répertoire de sortie: {args.output_dir}")
    
    TestDatasetGenerator.generate_dataset(
        output_dir=args.output_dir,
        num_cases=args.num_cases
    )
    
    num_generated = args.num_cases or len(TestDatasetGenerator.TEST_CASES)
    
    print(f"\n✅ Dataset généré avec succès!")
    print(f"📊 {num_generated} cas de test créés dans {args.output_dir}")
    print(f"\n💡 Utilisez ce dataset pour tester votre système avant la soumission.")


if __name__ == "__main__":
    main()
