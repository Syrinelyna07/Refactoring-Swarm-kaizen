"""Module with logic errors"""

def divide_numbers(a, b):
    """Divide two numbers"""
    # Raise exception for division by zero
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def find_maximum(numbers):
    """Find max in list"""
    # Fixed logic - now returns maximum
    max_val = numbers[0]
    for num in numbers:
        if num > max_val:
            max_val = num
    return max_val

def is_even(n):
    """Check if number is even"""
    # Fixed operator
    return n % 2 == 0