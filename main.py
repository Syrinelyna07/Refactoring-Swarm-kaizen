import argparse
import sys
import os
from dotenv import load_dotenv
from src.utils.logger import log_experiment, ActionType, initialize_logger, finalize_logger
from src.orchestrator.graph import run_refactoring_swarm

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="The Refactoring Swarm - Automated Code Refactoring System")
    parser.add_argument("--target_dir", type=str, required=True, help="Directory containing code to refactor")
    args = parser.parse_args()

    if not os.path.exists(args.target_dir):
        print(f"ERROR: Dossier {args.target_dir} introuvable.")
        sys.exit(1)

    # Initialize logger (OBLIGATOIRE pour le protocole)
    initialize_logger()

    print(f"DEMARRAGE SUR : {args.target_dir}")
    log_experiment(
        agent_name="System",
        model_used="system",
        action=ActionType.ANALYSIS,
        details={
            "input_prompt": f"Starting refactoring on {args.target_dir}",
            "output_response": "System initialized successfully",
            "target_dir": args.target_dir
        },
        status="SUCCESS"
    )
    
    # Run the refactoring swarm
    try:
        final_state = run_refactoring_swarm(args.target_dir)
        
        # Print results
        print(f"\nRESULTATS:")
        print(f"   Iterations: {final_state['iteration']}")
        print(f"   Status: {final_state['status']}")
        
        if final_state.get('test_result'):
            test_result = final_state['test_result']
            status_icon = "PASSED" if test_result.get('tests_passed') else "FAILED"
            print(f"   Tests: {status_icon}")
            print(f"   Quality Score: {test_result.get('quality_score', 0):.2f}/10")
        
        if final_state['status'] == 'complete':
            print("\nMISSION_COMPLETE")
        else:
            print(f"\nMISSION_INCOMPLETE: {final_state['status']}")
            
    except Exception as e:
        log_experiment(
            agent_name="System",
            model_used="system",
            action=ActionType.DEBUG,
            details={
                "input_prompt": "System error occurred",
                "output_response": str(e),
                "error": str(e)
            },
            status="ERROR"
        )
        print(f"ERREUR: {e}")
        finalize_logger()  # Sauvegarder même en cas d'erreur
        sys.exit(1)
    
    # Finalize logger (OBLIGATOIRE - sauvegarde sur disque)
    finalize_logger()

if __name__ == "__main__":
    main()