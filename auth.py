import sqlite3
import bcrypt
import os

DB_PATH = os.path.join("auth", "database.db")

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def create_user(username, password):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password BLOB
    )
    """)

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        c.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username.strip(), hashed_password)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "SELECT password FROM users WHERE username = ?",
        (username.strip(),)
    )
    data = c.fetchone()
    conn.close()

    if data and bcrypt.checkpw(password.encode(), data[0]):
        return True
    return False
