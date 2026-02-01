import argparse
import sys
import os
from dotenv import load_dotenv
from src.utils.logger import log_experiment, ActionType
from src.orchestrator.graph import run_refactoring_swarm

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="The Refactoring Swarm - Automated Code Refactoring System")
    parser.add_argument("--target_dir", type=str, required=True, help="Directory containing code to refactor")
    args = parser.parse_args()

    if not os.path.exists(args.target_dir):
        print(f"❌ Dossier {args.target_dir} introuvable.")
        sys.exit(1)

    print(f"🚀 DEMARRAGE SUR : {args.target_dir}")
    log_experiment(
        agent_name="System",
        model_used="system",
        action=ActionType.ANALYSIS,  # Using existing action
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
        print(f"\n📊 RESULTATS:")
        print(f"   Iterations: {final_state['iteration']}")
        print(f"   Status: {final_state['status']}")
        
        if final_state.get('test_result'):
            test_result = final_state['test_result']
            print(f"   Tests: {'✅ PASSED' if test_result.get('tests_passed') else '❌ FAILED'}")
            print(f"   Quality Score: {test_result.get('quality_score', 0):.2f}/10")
        
        if final_state['status'] == 'complete':
            print("\n✅ MISSION_COMPLETE")
        else:
            print(f"\n⚠️ MISSION_INCOMPLETE: {final_state['status']}")
            
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
        print(f"❌ ERREUR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()