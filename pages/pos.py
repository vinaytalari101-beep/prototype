import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import uuid

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(
    page_title="POS System",
    page_icon="💳",
    layout="wide"
)

st.title("💳 Point of Sale (POS)")
st.caption("Create bills, manage sales, and generate invoices.")

# ----------------------------------
# DATABASE CONNECTION
# ----------------------------------
conn = sqlite3.connect("inventory.db", check_same_thread=False)
cursor = conn.cursor()

# ----------------------------------
# CREATE SALES TABLE
# ----------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_no TEXT,
    product_name TEXT,
    quantity INTEGER,
    unit_price REAL,
    total_price REAL,
    sale_date TEXT
)
""")

conn.commit()

# ------------------
# MIGRATE LEGACY SCHEMA
# ------------------
# Ensure expected columns exist and migrate old columns if present
cursor.execute("PRAGMA table_info(sales)")
existing_cols = [r[1] for r in cursor.fetchall()]

expected = {
    "invoice_no": "TEXT",
    "product_name": "TEXT",
    "quantity": "INTEGER",
    "unit_price": "REAL",
    "total_price": "REAL",
    "sale_date": "TEXT"
}

for col, coltype in expected.items():
    if col not in existing_cols:
        try:
            cursor.execute(f"ALTER TABLE sales ADD COLUMN {col} {coltype}")
        except Exception:
            pass

# Migrate legacy column names if they exist
legacy_to_new = {
    "product": "product_name",
    "qty": "quantity",
    "total": "total_price"
}

for legacy, newcol in legacy_to_new.items():
    if legacy in existing_cols and newcol in existing_cols:
        try:
            cursor.execute(f"UPDATE sales SET {newcol} = {legacy} WHERE {newcol} IS NULL OR {newcol} = ''")
        except Exception:
            pass

from datetime import datetime as _dt
now = _dt.now().strftime("%Y-%m-%d %H:%M:%S")
if "sale_date" in existing_cols and "sale_date" not in expected:
    # handled above; nothing
    pass
else:
    # Fill empty sale_date with now
    try:
        cursor.execute("UPDATE sales SET sale_date = ? WHERE sale_date IS NULL OR sale_date = ''", (now,))
    except Exception:
        pass

conn.commit()

# ----------------------------------
# LOAD PRODUCTS
# ----------------------------------
products_df = pd.read_sql_query(
    "SELECT * FROM products",
    conn
)

if products_df.empty:
    st.warning("No products available in inventory.")
    st.stop()

# ----------------------------------
# SESSION CART
# ----------------------------------
if "cart" not in st.session_state:
    st.session_state.cart = []

# ----------------------------------
# ADD ITEMS TO CART
# ----------------------------------
st.subheader("🛒 Add Product")

col1, col2 = st.columns(2)

with col1:

    selected_product = st.selectbox(
        "Select Product",
        products_df["name"].tolist()
    )

with col2:

    selected_row = products_df[
        products_df["name"] == selected_product
    ].iloc[0]

    qty = st.number_input(
        "Quantity",
        min_value=1,
        max_value=int(selected_row["stock"]) if selected_row["stock"] > 0 else 1,
        value=1
    )

if st.button("➕ Add To Cart"):

    if selected_row["stock"] < qty:
        st.error("Not enough stock available!")

    else:

        item_total = qty * selected_row["price"]

        st.session_state.cart.append({
            "Product": selected_product,
            "Quantity": qty,
            "Price": selected_row["price"],
            "Total": item_total
        })

        st.success(f"{selected_product} added to cart.")

# ----------------------------------
# CART
# ----------------------------------
st.divider()

st.subheader("🧾 Shopping Cart")

cart_df = pd.DataFrame(st.session_state.cart)

if not cart_df.empty:

    st.dataframe(
        cart_df,
        use_container_width=True
    )

    subtotal = cart_df["Total"].sum()

    gst = subtotal * 0.18

    grand_total = subtotal + gst

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Subtotal",
        f"₹{subtotal:.2f}"
    )

    col2.metric(
        "GST (18%)",
        f"₹{gst:.2f}"
    )

    col3.metric(
        "Grand Total",
        f"₹{grand_total:.2f}"
    )

else:
    st.info("Cart is empty.")

# ----------------------------------
# GENERATE BILL
# ----------------------------------
st.divider()

if not cart_df.empty:

    if st.button("💳 Complete Sale"):

        invoice_no = str(uuid.uuid4())[:8].upper()

        sale_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # Save each item
        for _, row in cart_df.iterrows():

            cursor.execute("""
            INSERT INTO sales
            (
                invoice_no,
                product_name,
                quantity,
                unit_price,
                total_price,
                sale_date
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                invoice_no,
                row["Product"],
                row["Quantity"],
                row["Price"],
                row["Total"],
                sale_time
            ))

            # Deduct stock
            cursor.execute("""
            UPDATE products
            SET stock = stock - ?
            WHERE name = ?
            """,
            (
                row["Quantity"],
                row["Product"]
            ))

        conn.commit()

        st.success(
            f"Sale Completed! Invoice #{invoice_no}"
        )

        # ----------------------------------
        # PRINTABLE INVOICE
        # ----------------------------------
        st.subheader("🧾 Invoice")

        invoice_text = f"""
==================================
SMART INVENTORY POS
==================================

Invoice No : {invoice_no}
Date       : {sale_time}

----------------------------------
"""

        for _, row in cart_df.iterrows():

            invoice_text += (
                f"{row['Product']} "
                f"x {row['Quantity']} "
                f"= ₹{row['Total']:.2f}\n"
            )

        invoice_text += f"""

----------------------------------
Subtotal : ₹{subtotal:.2f}
GST 18%  : ₹{gst:.2f}

TOTAL    : ₹{grand_total:.2f}

==================================
Thank You For Shopping
==================================
"""

        st.code(invoice_text)

        st.download_button(
            label="⬇ Download Invoice",
            data=invoice_text,
            file_name=f"{invoice_no}.txt",
            mime="text/plain"
        )

        # Clear cart
        st.session_state.cart = []

# ----------------------------------
# SALES HISTORY
# ----------------------------------
st.divider()

st.subheader("📊 Recent Sales")

sales_df = pd.read_sql_query(
    """
    SELECT *
    FROM sales
    ORDER BY sale_date DESC
    LIMIT 20
    """,
    conn
)

if not sales_df.empty:

    st.dataframe(
        sales_df,
        use_container_width=True
    )

else:
    st.info("No sales records found.")

# ----------------------------------
# DAILY SALES SUMMARY
# ----------------------------------
st.divider()

st.subheader("💰 Today's Summary")

today = datetime.now().strftime("%Y-%m-%d")

today_sales = pd.read_sql_query(
    f"""
    SELECT *
    FROM sales
    WHERE sale_date LIKE '{today}%'
    """,
    conn
)

if not today_sales.empty:

    revenue = today_sales["total_price"].sum()

    orders = today_sales["invoice_no"].nunique()

    items = today_sales["quantity"].sum()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Revenue",
        f"₹{revenue:.2f}"
    )

    c2.metric(
        "Orders",
        orders
    )

    c3.metric(
        "Items Sold",
        items
    )

else:

    st.info("No sales today.")

conn.close()