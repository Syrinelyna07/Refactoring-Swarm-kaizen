"""Tests for code quality"""
from buggy import add_numbers, sum_list, Calculator

def test_add_numbers():
    assert add_numbers(5, 10) == 15

def test_sum_list():
    assert sum_list([1, 2, 3]) == 6

def test_calculator():
    obj = Calculator(5)
    assert obj.multiply(5) == 25