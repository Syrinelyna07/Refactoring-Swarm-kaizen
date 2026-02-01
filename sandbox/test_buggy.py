"""Test file for buggy_code"""
from buggy_code import add_numbers, multiply

def test_add_numbers():
    result = add_numbers(5, 10)
    assert result == 15, f"Expected 15, got {result}"

def test_multiply():
    result = multiply(3, 4)
    assert result == 12, f"Expected 12, got {result}"