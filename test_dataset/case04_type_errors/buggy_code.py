# filepath: type_issues.py
def concatenate_strings(a, b):
    return a + b

def bad_operations():
    number = 42
    text = "Hello"
    result = number + text  # TypeError
    
    items = [1, 2, 3]
    value = items[10]  # IndexError
    
    data = {"key": "value"}
    x = data["missing"]  # KeyError
    
    return result
