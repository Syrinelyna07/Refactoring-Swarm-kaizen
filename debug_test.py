"""Debug script to test individual components"""
import os
from src.tools.sandbox_guard import is_path_allowed
from src.tools.file_tools import read_file, write_file
from pathlib import Path

# Test sandbox security
sandbox_path = Path("sandbox/buggy_code.py")
print(f"Testing path: {sandbox_path.resolve()}")
print(f"Path allowed: {is_path_allowed(str(sandbox_path))}")

# Test file operations
try:
    content = read_file(str(sandbox_path))
    print(f"✅ Read file successfully: {len(content)} chars")
    print(f"Content preview: {content[:100]}")
except Exception as e:
    print(f"❌ Failed to read: {e}")

# Test write
try:
    test_content = "# Test write\nprint('hello')\n"
    write_file(str(sandbox_path), test_content)
    print(f"✅ Write successful")
except Exception as e:
    print(f"❌ Failed to write: {e}")

# Test pylint
from src.tools.pylint_tool import run_pylint
result = run_pylint(str(sandbox_path))
print(f"\nPylint result: {result}")

# Test pytest
from src.tools.pytest_tool import run_pytest
test_result = run_pytest("sandbox")
print(f"\nPytest result: {test_result}")
