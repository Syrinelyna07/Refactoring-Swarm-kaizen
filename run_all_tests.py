"""Run the refactoring swarm on all test cases"""
import os
import subprocess
import json
from pathlib import Path

test_cases = [
    "test_cases/case01_syntax",
    "test_cases/case02_logic",
    "test_cases/case03_quality",
    "test_cases/case04_complex"
]

results = {}

for test_case in test_cases:
    print(f"\n{'='*60}")
    print(f"🧪 Testing: {test_case}")
    print(f"{'='*60}\n")
    
    # Run the refactoring swarm
    result = subprocess.run(
        ["python", "main.py", "--target_dir", test_case],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    # Store result
    results[test_case] = {
        "returncode": result.returncode,
        "success": result.returncode == 0
    }

# Summary
print("\n" + "="*60)
print("📊 SUMMARY")
print("="*60)
for case, result in results.items():
    status = "✅ PASSED" if result["success"] else "❌ FAILED"
    print(f"{case}: {status}")
