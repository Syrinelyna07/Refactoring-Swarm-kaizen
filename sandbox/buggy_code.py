def add_numbers(a, b):
    """Add two numbers and return the result.
    
    Args:
        a: First number to add
        b: Second number to add
        
    Returns:
        The sum of a and b
    """
    print("Adding numbers")
    result = a + b
    return result

def multiply(x, y):
    """Multiply two numbers and return the result.
    
    Args:
        x: First number to multiply
        y: Second number to multiply
        
    Returns:
        The product of x and y
    """
    return x * y

x = add_numbers(5, 10)
print(x)