"""Tests for complex module"""
from buggy import process_data, Calculator, validate_email

def test_process_data():
    result = process_data([1, 2, 3, -1, 0])
    assert result == [3, 5, 7]  # Should be sorted: [3, 5, 7]
    assert result == sorted(result)

def test_calculator():
    calc = Calculator()
    calc.add(5, 3)
    calc.add(10, 2)
    history = calc.get_history()
    assert len(history) == 2

def test_validate_email():
    assert validate_email("test@example.com") is True
    assert validate_email("invalid") is False
    assert validate_email("@invalid") is False