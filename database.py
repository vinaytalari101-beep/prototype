import sqlite3

def init_db():
    conn = sqlite3.connect("inventory.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        price REAL,
        stock INTEGER
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
