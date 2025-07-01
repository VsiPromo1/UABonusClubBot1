import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        referrer_id INTEGER,
        balance REAL DEFAULT 0
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS withdrawals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        card_number TEXT,
        amount REAL
    )
""")

conn.commit()


def register_user(user_id, referrer_id=None):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (user_id, referrer_id) VALUES (?, ?)", (user_id, referrer_id))
        conn.commit()
        if referrer_id:
            cursor.execute("UPDATE users SET balance = balance + 4.0 WHERE user_id = ?", (referrer_id,))
            conn.commit()


def get_user_balance(user_id):
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0


def save_withdrawal(user_id, card_number, amount):
    cursor.execute("INSERT INTO withdrawals (user_id, card_number, amount) VALUES (?, ?, ?)",
                   (user_id, card_number, amount))
    cursor.execute("UPDATE users SET balance = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
