
import sqlite3
def get_conn():
    return sqlite3.connect('inventory.db', check_same_thread=False)
def init_db():
    conn=get_conn(); cur=conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY,name TEXT,category TEXT,price REAL,stock INTEGER)')
    cur.execute('CREATE TABLE IF NOT EXISTS sales(id INTEGER PRIMARY KEY,product TEXT,qty INTEGER,total REAL)')
    conn.commit(); conn.close()
