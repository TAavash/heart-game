import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def init_db():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    # Drop the old table if it exists to add the password column
    c.execute('DROP TABLE IF EXISTS users')
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            score INTEGER NOT NULL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_user_by_username(username):
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(username, password):
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    try:
        hashed_password = generate_password_hash(password)
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        # User already exists
        conn.close()
        return False
    conn.close()
    return True

def update_score(username, score):
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("UPDATE users SET score=? WHERE username=?", (score, username))
    conn.commit()
    conn.close()

def get_leaderboard():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("SELECT username, score FROM users ORDER BY score DESC")
    leaderboard = c.fetchall()
    conn.close()
    return leaderboard

def check_user_credentials(username, password):
    user = get_user_by_username(username)
    if user and check_password_hash(user[2], password):
        return True
    return False