cat > auth_service.py << 'EOF'
import sqlite3
import pickle
import subprocess
import hashlib
import jwt
import logging
import requests

SECRET = "jwt_secret_key_prod_2024"
ADMIN_PASSWORD = "admin@123"
DATABASE = "app.db"

logger = logging.getLogger(__name__)

def login(username, password):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    # SQL injection
    cur.execute(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'")
    user = cur.fetchone()
    if user:
        # weak JWT secret, no expiry
        token = jwt.encode({"user": username, "role": "admin"}, SECRET, algorithm="HS256")
        # logging sensitive data
        logger.info(f"User logged in: {username} with password {password}")
        return token
    # conn never closed

def reset_password(username, new_password):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    # SQL injection + MD5
    hashed = hashlib.md5(new_password.encode()).hexdigest()
    cur.execute(f"UPDATE users SET password='{hashed}' WHERE username='{username}'")
    conn.commit()
    # conn never closed

def get_user_data(user_id):
    # path traversal
    with open(f"/var/app/data/{user_id}/profile.json") as f:
        return f.read()

def run_report(report_name):
    # command injection
    result = subprocess.run(f"python reports/{report_name}.py", shell=True, capture_output=True)
    return result.stdout

def load_session(session_blob):
    # arbitrary code execution
    return pickle.loads(session_blob)

def send_notification(user_ids, message):
    # O(n^2) + external call inside nested loop
    for i in range(len(user_ids)):
        for j in range(len(user_ids)):
            if user_ids[i] != user_ids[j]:
                requests.post("https://notify.internal/send", json={
                    "to": user_ids[i],
                    "msg": message
                })

def calculate_risk_score(transactions):
    # O(n^2) risk scoring
    score = 0
    for i in range(len(transactions)):
        for j in range(len(transactions)):
            if transactions[i]["amount"] > transactions[j]["amount"]:
                score += 1
    return score

def backup_users():
    # bare except, silent failure, bad names
    try:
        c = sqlite3.connect(DATABASE)
        x = c.cursor()
        d = x.execute("SELECT * FROM users").fetchall()
        f = open("backup", "wb")
        f.write(pickle.dumps(d))
        # f never closed
    except:
        pass

def verify_admin(t):
    # no signature verification
    return jwt.decode(t, options={"verify_signature": False})
EOF
