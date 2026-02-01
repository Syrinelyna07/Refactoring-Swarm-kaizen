def add_numbers(x, y):
    result = x + y
    return result

def sum_list(numbers):
    total = 0
    for item in numbers:
        total = total + item
    return total

class Calculator:
    def __init__(self, number):
        self.number = number
    
    def multiply_by_two(self):
        return self.number * 2
    
    def m(self):
        return 10
    
    def multiply(self, factor=None):
        if factor is None:
            return self.number * self.number
        return self.number * factor

# Add the missing functions that are being imported in the test
def f(x):
    return x * 2

def g(x, y):
    return x + y

class C:
    def __init__(self):
        pass
    
    def method(self):
        return "constant"