# handles chatRoom users
import sqlite3 
import bcrypt
import pytz
from datetime import datetime
from config import DB_NAME

def create_messages_table():
    conn = sqlite3.connect(DB_NAME) 
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            content TEXT NOT NULL,
            timeStamp TEXT NOT NULL
        )                          
    ''')
    conn.commit()
    conn.close()

def create_users_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def register_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(username):
    """Checks if the users exists, it will return True."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE username=?)", (username,))
    exists = cursor.fetchone()[0]
    conn.close()
    return bool(exists)

def authenticate_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None  #user doesn't exist

    stored_hash = row[0]
    if bcrypt.checkpw(password.encode(), stored_hash):
        return True
    else:
        return False
    
def save_message(sender,content):
    israel_tz = pytz.timezone("Asia/Jerusalem")
    timestamp = datetime.now(israel_tz).strftime("%d.%m.%Y %H:%M")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (sender,content, timeStamp)
        VALUES (?,?,?)
        ''', (sender,content,timestamp))
    conn.commit()
    conn.close()

def get_last_messages(limit=15):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT sender,content,timeStamp
        FROM messages 
        ORDER BY id DESC
        LIMIT ?
    ''', (limit,))
    messages =  cursor.fetchall()
    conn.close()
    return messages[::-1]