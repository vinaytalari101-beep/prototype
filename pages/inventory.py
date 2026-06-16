import streamlit as st
import pandas as pd
import sqlite3
import os
from PIL import Image

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(
    page_title="Inventory Management",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Inventory Management")

# ----------------------------------
# DATABASE
# ----------------------------------
conn = sqlite3.connect("inventory.db", check_same_thread=False)
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    price REAL,
    stock INTEGER,
    image TEXT
)
""")
conn.commit()

# ----------------------------------
# IMAGE FOLDER
# ----------------------------------
IMAGE_FOLDER = "product_images"

if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

# ----------------------------------
# ADD PRODUCT
# ----------------------------------
st.subheader("➕ Add New Product")

with st.form("add_product_form"):

    col1, col2 = st.columns(2)

    with col1:
        product_name = st.text_input("Product Name")

        category = st.selectbox(
            "Category",
            [
                "Groceries",
                "Electronics",
                "Fashion",
                "Stationery",
                "Home Items",
                "Other"
            ]
        )

    with col2:
        price = st.number_input(
            "Price",
            min_value=0.0,
            step=1.0
        )

        stock = st.number_input(
            "Stock Quantity",
            min_value=0,
            step=1
        )

    image_file = st.file_uploader(
        "Upload Product Image",
        type=["jpg", "jpeg", "png"]
    )

    submit = st.form_submit_button("Add Product")

    if submit:

        image_path = ""

        if image_file:

            image_path = os.path.join(
                IMAGE_FOLDER,
                image_file.name
            )

            with open(image_path, "wb") as f:
                f.write(image_file.getbuffer())

        cursor.execute("""
            INSERT INTO products
            (name, category, price, stock, image)
            VALUES (?, ?, ?, ?, ?)
        """,
        (
            product_name,
            category,
            price,
            stock,
            image_path
        ))

        conn.commit()

        st.success("Product Added Successfully!")

# ----------------------------------
# VIEW INVENTORY
# ----------------------------------
st.divider()

st.subheader("📋 Inventory List")

df = pd.read_sql_query(
    "SELECT * FROM products",conn)

if df.empty:
    st.warning("No products available.")
else:

    # Search
    search = st.text_input(
        "🔍 Search Product"
    )

    if search:
        df = df[
            df["name"]
            .str.contains(
                search,
                case=False,
                na=False
            )
        ]

    st.dataframe(
        df,
        use_container_width=True
    )

# ----------------------------------
# PRODUCT CARDS
# ----------------------------------
st.divider()

st.subheader("🛒 Product Gallery")

products = pd.read_sql_query(
    "SELECT * FROM products",
    conn
)

if not products.empty:

    cols = st.columns(3)

    for index, product in enumerate(products.to_dict(orient="records")):

        with cols[index % 3]:

            img_path = product.get("image", "")

            if img_path and os.path.exists(img_path):

                st.image(
                    img_path,
                    use_container_width=True
                )

            st.markdown(f"### {product.get('name','')}")

            st.write(f"Category: {product.get('category','')}")

            st.write(f"Price: ₹{product.get('price','')}")

            st.write(f"Stock: {product.get('stock','')}")

# ----------------------------------
# UPDATE STOCK
# ----------------------------------
st.divider()

st.subheader("✏ Update Stock")

product_names = products["name"].tolist()

if product_names:

    selected_product = st.selectbox(
        "Select Product",
        product_names
    )

    new_stock = st.number_input(
        "New Stock Quantity",
        min_value=0,
        step=1
    )

    if st.button("Update Stock"):

        cursor.execute("""
            UPDATE products
            SET stock = ?
            WHERE name = ?
        """,
        (
            new_stock,
            selected_product
        ))

        conn.commit()

        st.success(
            "Stock Updated Successfully!"
        )

# ----------------------------------
# DELETE PRODUCT
# ----------------------------------
st.divider()

st.subheader("🗑 Delete Product")

if product_names:

    delete_product = st.selectbox(
        "Choose Product to Delete",
        product_names,
        key="delete"
    )

    if st.button("Delete Product"):

        cursor.execute("""
            DELETE FROM products
            WHERE name = ?
        """,
        (delete_product,)
        )

        conn.commit()

        st.success(
            "Product Deleted Successfully!"
        )

        st.rerun()

# ----------------------------------
# LOW STOCK ALERTS
# ----------------------------------
st.divider()

st.subheader("⚠ Low Stock Alert")

low_stock = products[
    products["stock"] <= 10
]

if not low_stock.empty:

    st.error(
        f"{len(low_stock)} products are running low!"
    )

    st.dataframe(
        low_stock[
            [
                "name",
                "category",
                "stock"
            ]
        ],
        use_container_width=True
    )

else:
    st.success(
        "All products have healthy stock levels."
    )

# ----------------------------------
# INVENTORY SUMMARY
# ----------------------------------
st.divider()

st.subheader("📊 Inventory Summary")

col1, col2, col3 = st.columns(3)

total_products = len(products)

total_stock = products["stock"].sum()

inventory_value = (
    products["price"] *
    products["stock"]
).sum()

col1.metric(
    "Products",
    total_products
)

col2.metric(
    "Stock Units",
    total_stock
)

col3.metric(
    "Inventory Value",
    f"₹{inventory_value:,.0f}"
)

# ----------------------------------
# DOWNLOAD INVENTORY
# ----------------------------------
st.divider()

csv = products.to_csv(index=False)

st.download_button(
    label="⬇ Download Inventory CSV",
    data=csv,
    file_name="inventory.csv",
    mime="text/csv"
)

conn.close()
