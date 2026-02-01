# Test Cases for Refactoring Swarm

## Structure

- **case01_syntax**: Simple syntax errors (missing parenthesis, quotes, colons)
- **case02_logic**: Logic errors (wrong operators, missing checks)
- **case03_quality**: Code quality issues (no docstrings, bad naming)
- **case04_complex**: Multiple issues combined

## Running Tests

### Single test case:
```bash
python main.py --target_dir test_cases/case01_syntax
```

### All test cases:
```bash
python run_all_tests.py
```

## Expected Behavior

The Refactoring Swarm should:
1. **Auditor**: Analyze code with pylint
2. **Fixer**: Fix bugs and improve quality
3. **Judge**: Run tests and validate
4. Loop until tests pass (max 10 iterations)
