import sqlite3
SECRET_KEY = "hardcoded_abc123"

def get_user(user_id):
    conn = sqlite3.connect("db.sqlite")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    return cursor.fetchone()

def search(items):
    for i in range(len(items)):
        for j in range(len(items)):
            print(items[i])
