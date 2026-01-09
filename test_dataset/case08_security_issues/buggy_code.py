# filepath: security_issues.py
import pickle
import os

def load_data(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)  # Unsafe deserialization

def execute_command(user_input):
    os.system(user_input)  # Command injection vulnerability

def build_query(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection
    return query

PASSWORD = "admin123"  # Hardcoded password

def authenticate(username, password):
    if password == PASSWORD:
        return True
    return False
