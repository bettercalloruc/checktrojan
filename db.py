import sqlite3
import threading

# Thread-safe kilid
db_lock = threading.Lock()

# Baza bağlantısı funksiyası
def get_db():
    return sqlite3.connect("users.db", check_same_thread=False)

# Baza qurulması (bir dəfə çağır)
def setup():
    with db_lock:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            coins INTEGER DEFAULT 0
        )
        """)
        conn.commit()
        conn.close()

# İstifadəçini əlavə et (əgər yoxdursa)
def add_user(user_id):
    with db_lock:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()

# Coinləri al
def get_coins(user_id):
    with db_lock:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT coins FROM users WHERE user_id=?", (user_id,))
        result = cur.fetchone()
        conn.close()
        return result[0] if result else 0

# Coin əlavə et
def add_coins(user_id, amount):
    with db_lock:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE users SET coins = coins + ? WHERE user_id=?", (amount, user_id))
        conn.commit()
        conn.close()

# Coin çıxart
def remove_coins(user_id, amount):
    with db_lock:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE users SET coins = coins - ? WHERE user_id=? AND coins >= ?", (amount, user_id, amount))
        conn.commit()
        conn.close()
