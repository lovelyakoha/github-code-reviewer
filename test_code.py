import os

password = "admin123"
secret_key = "abc123secret"

def get_users(db):
    query = "SELECT * FROM users WHERE id = " + db
    return query

def calculate(numbers):
    result = []
    for i in range(len(numbers)):
        for j in range(len(numbers)):
            result.append(numbers[i] * numbers[j])
    return result

def a(x, y, z, w):
    if x > 0:
        if y > 0:
            if z > 0:
                return x + y + z + w
