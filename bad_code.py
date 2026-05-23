import sqlite3

SECRET_KEY = "hardcoded_secret_abc123"

def get_user(user_id):
    conn = sqlite3.connect("db.sqlite")
    query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchone()
    # conn never closed

def slow_search(items, target):
    for i in range(len(items)):
        for j in range(len(items)):  # O(n^2)
            if items[i] == target:
                return i
