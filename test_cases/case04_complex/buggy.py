"""Complex buggy module"""

def process_data(data):
    """Process data by doubling positive values and filtering negatives.
    
    Args:
        data: List of numeric values to process
        
    Returns:
        List of processed values, sorted in ascending order
        
    Raises:
        TypeError: If data is not iterable or contains non-numeric values
    """
    if not hasattr(data, '__iter__'):
        raise TypeError("Data must be iterable")
    
    result = []
    for item in data:
        if not isinstance(item, (int, float)):
            raise TypeError("All items must be numeric")
        if item > 0:
            result.append(item * 2 + 1)
        # Negative and zero values are filtered out (skipped)
    
    return sorted(result)

class Calculator:
    """A calculator that maintains operation history."""
    
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        """Add two numbers and record the operation.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Sum of a and b
        """
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def get_history(self):
        """Get the operation history.
        
        Returns:
            List of operation strings
        """
        return self.history.copy()

def validate_email(email):
    """Validate email address format.
    
    Args:
        email: Email string to validate
        
    Returns:
        bool: True if email format is valid, False otherwise
    """
    if not isinstance(email, str):
        return False
    
    # Basic email validation
    if "@" not in email:
        return False
    
    parts = email.split("@")
    if len(parts) != 2:
        return False
    
    local, domain = parts
    if not local or not domain:
        return False
    
    # Check for basic domain structure
    if "." not in domain:
        return False
    
    return True