# filepath: logic_bugs.py
def find_maximum(numbers):
    max_value = 0  # Bug: ne fonctionne pas avec des nombres négatifs
    for num in numbers:
        if num > max_value:
            max_value = num
    return max_value

def calculate_discount(price, discount_percent):
    discount = price * discount_percent  # Bug: oubli de diviser par 100
    return price - discount

def is_palindrome(text):
    return text == text[::-1]  # Bug: sensible à la casse

def divide_list(items, chunk_size):
    chunks = []
    for i in range(0, len(items), chunk_size):
        chunks.append(items[i:i+chunk_size])
    return chunks[:-1]  # Bug: perd le dernier chunk
