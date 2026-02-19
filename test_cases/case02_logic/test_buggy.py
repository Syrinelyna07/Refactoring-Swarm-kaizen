"""Tests for logic errors"""
from buggy import divide_numbers, find_maximum, is_even

def test_divide_numbers():
    assert divide_numbers(10, 2) == 5
    assert divide_numbers(9, 3) == 3
    # Should handle zero division
    try:
        divide_numbers(5, 0)
        assert False, "Should raise exception"
    except ZeroDivisionError:
        pass

def test_find_maximum():
    assert find_maximum([1, 5, 3, 9, 2]) == 9
    assert find_maximum([10, 20, 5]) == 20

def test_is_even():
    assert is_even(2) is True
    assert is_even(3) is False
    assert is_even(0) is True