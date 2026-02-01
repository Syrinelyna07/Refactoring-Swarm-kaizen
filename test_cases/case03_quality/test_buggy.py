"""Tests for code quality"""
from buggy import add_numbers, sum_list, Calculator

def test_f():
    assert add_numbers(5, 10) == 15

def test_g():
    assert sum_list([1, 2, 3]) == 6

def test_c():
    obj = Calculator(5)
    assert obj.multiply(5) == 25