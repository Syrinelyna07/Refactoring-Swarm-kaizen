"""Module with syntax errors"""

def calculate_sum(a, b):
    # Missing closing parenthesis
    result = (a + b)
    return result

def print_message(msg):
    # Missing quotes
    print("Hello, " + msg)

# Missing colon
if __name__ == "__main__":
    calculate_sum(5, 10)