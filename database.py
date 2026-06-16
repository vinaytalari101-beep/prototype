import sqlite3
from datetime import datetime

DB_NAME = "inventory.db"


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Users
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    # Products
    c.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_code TEXT UNIQUE,
        name TEXT,
        category TEXT,
        purchase_price REAL,
        selling_price REAL,
        quantity INTEGER,
        image_path TEXT,
        created_at TEXT
    )
    """)

    # Sales
    c.execute("""
    CREATE TABLE IF NOT EXISTS sales(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_no TEXT,
        product_id INTEGER,
        product_name TEXT,
        quantity INTEGER,
        price REAL,
        total REAL,
        sale_date TEXT
    )
    """)

    conn.commit()
    conn.close()


# ---------- USERS ----------

def create_default_admin():
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username='admin'")
    admin = c.fetchone()

    if not admin:
        c.execute("""
        INSERT INTO users(username,password,role)
        VALUES(?,?,?)
        """, ("admin", "admin123", "admin"))

    conn.commit()
    conn.close()


# ---------- PRODUCTS ----------

def add_product(code, name, category,
                purchase_price,
                selling_price,
                quantity,
                image_path):

    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    INSERT INTO products(
    product_code,
    name,
    category,
    purchase_price,
    selling_price,
    quantity,
    image_path,
    created_at
    )
    VALUES(?,?,?,?,?,?,?,?)
    """,
              (
                  code,
                  name,
                  category,
                  purchase_price,
                  selling_price,
                  quantity,
                  image_path,
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
              ))

    conn.commit()
    conn.close()


def get_products():
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM products")
    data = c.fetchall()

    conn.close()
    return data


def search_products(keyword):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    SELECT * FROM products
    WHERE name LIKE ?
    """, (f"%{keyword}%",))

    rows = c.fetchall()

    conn.close()
    return rows


def update_stock(product_id, qty_sold):

    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    UPDATE products
    SET quantity = quantity - ?
    WHERE id = ?
    """, (qty_sold, product_id))

    conn.commit()
    conn.close()


def low_stock_products(limit=10):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    SELECT * FROM products
    WHERE quantity <= ?
    """, (limit,))

    rows = c.fetchall()

    conn.close()
    return rows


# ---------- SALES ----------

def add_sale(
        invoice_no,
        product_id,
        product_name,
        qty,
        price,
        total):

    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    INSERT INTO sales(
    invoice_no,
    product_id,
    product_name,
    quantity,
    price,
    total,
    sale_date
    )
    VALUES(?,?,?,?,?,?,?)
    """,
              (
                  invoice_no,
                  product_id,
                  product_name,
                  qty,
                  price,
                  total,
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
              ))

    conn.commit()
    conn.close()


def get_sales():

    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    SELECT * FROM sales
    ORDER BY id DESC
    """)

    rows = c.fetchall()

    conn.close()
    return rows


def total_sales_amount():

    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    SELECT SUM(total)
    FROM sales
    """)

    amount = c.fetchone()[0]

    conn.close()

    return amount if amount else 0