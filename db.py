import psycopg2

DB_URL = "postgresql://postgres:20072009abC$@db.iqkrnjjklahkyoisbgvf.supabase.co:5432/postgres"  # Buraya öz Supabase bağlantını qoy

conn = psycopg2.connect(DB_URL, sslmode='require')
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY,
        coins INTEGER DEFAULT 0
    )
""")
conn.commit()

def get_coins(user_id):
    cur.execute("SELECT coins FROM users WHERE user_id = %s", (user_id,))
    result = cur.fetchone()
    return result[0] if result else 0

def add_coins(user_id, amount):
    cur.execute("SELECT coins FROM users WHERE user_id = %s", (user_id,))
    if cur.fetchone():
        cur.execute("UPDATE users SET coins = coins + %s WHERE user_id = %s", (amount, user_id))
    else:
        cur.execute("INSERT INTO users (user_id, coins) VALUES (%s, %s)", (user_id, amount))
    conn.commit()

def remove_coins(user_id, amount):
    cur.execute("UPDATE users SET coins = coins - %s WHERE user_id = %s", (amount, user_id))
    conn.commit()
