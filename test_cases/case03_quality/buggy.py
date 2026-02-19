def add_numbers(x, y):
    """Add two numbers and return the result."""
    return x + y

def sum_list(numbers):
    """Calculate the sum of all numbers in a list."""
    total = 0
    for item in numbers:
        total += item
    return total

class Calculator:
    """A simple calculator class for basic arithmetic operations."""
    
    def __init__(self, number):
        """Initialize calculator with a number."""
        self.number = number
    
    def multiply_by_two(self):
        """Multiply the stored number by 2."""
        return self.number * 2
    
    def get_constant(self):
        """Return a constant value of 10."""
        return 10
    
    def multiply(self, factor=None):
        """Multiply the stored number by a factor or by itself if no factor provided."""
        if factor is None:
            return self.number * self.number
        return self.number * factor

# Add the missing functions that are being imported in the test
def double_value(x):
    """Double the input value."""
    return x * 2

def add_values(x, y):
    """Add two values together."""
    return x + y

class SimpleClass:
    """A simple class with basic functionality."""
    
    def __init__(self):
        """Initialize the class."""
        pass
    
    def get_constant_string(self):
        """Return a constant string."""
        return "constant"