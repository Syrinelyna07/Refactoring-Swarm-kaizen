"""Tests for syntax errors case"""
from buggy import calculate_sum, print_message

def test_calculate_sum():
    assert calculate_sum(5, 10) == 15
    assert calculate_sum(0, 0) == 0
    assert calculate_sum(-5, 5) == 0