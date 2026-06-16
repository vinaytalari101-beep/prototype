import streamlit as st
import sqlite3
import pandas as pd
from database import init_db

st.set_page_config(page_title="Inventory Prototype", page_icon="📦", layout="wide")
init_db()

def get_conn():
    return sqlite3.connect("inventory.db", check_same_thread=False)

st.title("📦 Smart Inventory Management Prototype")

page = st.sidebar.selectbox("Navigation", ["Dashboard", "Inventory", "POS"])

conn = get_conn()

if page == "Inventory":
    st.header("Add Product")

    with st.form("product_form"):
        name = st.text_input("Product Name")
        category = st.text_input("Category")
        price = st.number_input("Price", min_value=0.0)
        stock = st.number_input("Stock", min_value=0, step=1)
        submitted = st.form_submit_button("Add Product")

    if submitted and name:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO products(name,category,price,stock) VALUES(?,?,?,?)",
            (name, category, price, stock),
        )
        conn.commit()
        st.success("Product added successfully")

    st.subheader("Inventory")
    df = pd.read_sql_query("SELECT * FROM products", conn)

    search = st.text_input("Search Product")
    if search:
        df = df[df["name"].str.contains(search, case=False, na=False)]

    st.dataframe(df, use_container_width=True)

elif page == "POS":
    st.header("Point of Sale")

    df = pd.read_sql_query("SELECT * FROM products", conn)

    if len(df) == 0:
        st.info("Add products first.")
    else:
        product = st.selectbox("Select Product", df["name"].tolist())
        qty = st.number_input("Quantity", min_value=1, step=1)

        if st.button("Sell Product"):
            row = df[df["name"] == product].iloc[0]

            if row["stock"] >= qty:
                new_stock = int(row["stock"]) - int(qty)

                cur = conn.cursor()
                cur.execute(
                    "UPDATE products SET stock=? WHERE id=?",
                    (new_stock, int(row["id"])),
                )
                conn.commit()

                st.success(f"Sale completed. Remaining stock: {new_stock}")
            else:
                st.error("Insufficient stock")

else:
    df = pd.read_sql_query("SELECT * FROM products", conn)

    total_products = len(df)
    total_stock = int(df["stock"].sum()) if len(df) else 0

    c1, c2 = st.columns(2)
    c1.metric("Total Products", total_products)
    c2.metric("Total Stock", total_stock)

    if len(df):
        low_stock = df[df["stock"] < 10]
        if not low_stock.empty:
            st.warning("Low Stock Alert")
            st.dataframe(low_stock, use_container_width=True)

conn.close()
