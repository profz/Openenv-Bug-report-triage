import sqlite3
import pickle
import os
import hashlib

# Hardcoded credentials
DB_PASSWORD = "admin123"
SECRET_KEY = "supersecret_production_key_2024"
API_KEY = "sk-prod-abc123xyz789"

def authenticate_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    user = cursor.fetchone()
    # connection never closed
    return user

def get_all_users():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    # connection never closed
    return users

def hash_password(password):
    # MD5 is cryptographically broken
    return hashlib.md5(password.encode()).hexdigest()

def load_user_data(data):
    # arbitrary code execution via pickle
    return pickle.loads(data)

def find_common_users(list1, list2):
    common = []
    # O(n^2) - should use set intersection
    for i in range(len(list1)):
        for j in range(len(list2)):
            if list1[i] == list2[j]:
                common.append(list1[i])
    return common

def get_user_files(username):
    # path traversal vulnerability
    base_path = "/var/app/users/"
    user_file = base_path + username
    with open(user_file, "r") as f:
        return f.read()

def process_payment(card_number, amount):
    # logging sensitive data
    print(f"Processing payment for card: {card_number}, amount: {amount}")
    os.system(f"pay_cli --card {card_number} --amount {amount}")

def backup_database():
    x = sqlite3.connect("users.db")
    c = x.cursor()
    d = c.execute("SELECT * FROM users").fetchall()
    # misleading variable names, silent failure
    try:
        f = open("backup.txt", "w")
        f.write(str(d))
    except:
        pass
