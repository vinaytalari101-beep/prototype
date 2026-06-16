import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Smart Inventory Dashboard")
st.caption("Real-time overview of inventory, sales, and business performance.")

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
conn = sqlite3.connect("inventory.db", check_same_thread=False)

# -----------------------------
# LOAD DATA
# -----------------------------
try:
    products_df = pd.read_sql_query(
        "SELECT * FROM products",
        conn
    )
except:
    products_df = pd.DataFrame()

try:
    sales_df = pd.read_sql_query(
        "SELECT * FROM sales",
        conn
    )
except:
    sales_df = pd.DataFrame()

# -----------------------------
# CALCULATE METRICS
# -----------------------------
total_products = len(products_df)

total_stock = (
    products_df["stock"].sum()
    if not products_df.empty
    else 0
)

inventory_value = (
    (products_df["price"] * products_df["stock"]).sum()
    if not products_df.empty
    else 0
)

total_revenue = (
    sales_df["total_price"].sum()
    if not sales_df.empty
    else 0
)

total_orders = (
    len(sales_df)
    if not sales_df.empty
    else 0
)

# -----------------------------
# KPI CARDS
# -----------------------------
st.subheader("📌 Business Overview")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "📦 Products",
    total_products
)

col2.metric(
    "🏷 Stock Units",
    f"{total_stock:,}"
)

col3.metric(
    "💰 Revenue",
    f"₹{total_revenue:,.0f}"
)

col4.metric(
    "🧾 Orders",
    total_orders
)

col5.metric(
    "🏦 Inventory Value",
    f"₹{inventory_value:,.0f}"
)

# -----------------------------
# LOW STOCK ALERTS
# -----------------------------
st.divider()

col1, col2 = st.columns([2, 1])

with col1:

    st.subheader("⚠ Low Stock Products")

    if not products_df.empty:

        low_stock = products_df[
            products_df["stock"] <= 10
        ]

        if len(low_stock) > 0:

            st.dataframe(
                low_stock[
                    ["name", "category", "stock"]
                ],
                use_container_width=True
            )

        else:
            st.success(
                "All products have sufficient stock."
            )

with col2:

    st.subheader("📉 Stock Summary")

    if not products_df.empty:

        out_stock = len(
            products_df[
                products_df["stock"] == 0
            ]
        )

        low_stock_count = len(
            products_df[
                products_df["stock"] <= 10
            ]
        )

        healthy_stock = len(
            products_df[
                products_df["stock"] > 10
            ]
        )

        st.metric(
            "Out of Stock",
            out_stock
        )

        st.metric(
            "Low Stock",
            low_stock_count
        )

        st.metric(
            "Healthy Stock",
            healthy_stock
        )

# -----------------------------
# SALES OVERVIEW
# -----------------------------
st.divider()

st.subheader("📈 Revenue Trend")

if not sales_df.empty:

    sales_df["sale_date"] = pd.to_datetime(
        sales_df["sale_date"]
    )

    revenue_data = (
        sales_df.groupby(
            sales_df["sale_date"].dt.date
        )["total_price"]
        .sum()
        .reset_index()
    )

    fig = px.line(
        revenue_data,
        x="sale_date",
        y="total_price",
        markers=True,
        title="Daily Revenue"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:
    st.info("No sales data available.")

# -----------------------------
# INVENTORY DISTRIBUTION
# -----------------------------
st.divider()

col1, col2 = st.columns(2)

with col1:

    st.subheader("📦 Inventory Levels")

    if not products_df.empty:

        fig = px.bar(
            products_df,
            x="name",
            y="stock",
            color="stock",
            title="Current Stock"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

with col2:

    st.subheader("🛒 Product Categories")

    if (
        not products_df.empty
        and "category" in products_df.columns
    ):

        category_counts = (
            products_df["category"]
            .value_counts()
            .reset_index()
        )

        category_counts.columns = [
            "Category",
            "Count"
        ]

        fig = px.pie(
            category_counts,
            names="Category",
            values="Count",
            title="Products by Category"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# -----------------------------
# TOP SELLERS
# -----------------------------
st.divider()

st.subheader("🏆 Top Selling Products")

if (
    not sales_df.empty
    and "product_name" in sales_df.columns
):

    top_products = (
        sales_df.groupby(
            "product_name"
        )["quantity"]
        .sum()
        .reset_index()
        .sort_values(
            by="quantity",
            ascending=False
        )
        .head(10)
    )

    fig = px.bar(
        top_products,
        x="product_name",
        y="quantity",
        text_auto=True,
        title="Top 10 Selling Products"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# -----------------------------
# RECENT SALES
# -----------------------------
st.divider()

st.subheader("🧾 Recent Transactions")

if not sales_df.empty:

    recent_sales = sales_df.sort_values(
        by="sale_date",
        ascending=False
    )

    st.dataframe(
        recent_sales.head(10),
        use_container_width=True
    )

else:
    st.info("No transactions available.")

# -----------------------------
# QUICK ACTIONS
# -----------------------------
st.divider()

st.subheader("🚀 Quick Actions")

c1, c2, c3 = st.columns(3)

with c1:
    st.info(
        "➕ Add new products from Inventory page."
    )

with c2:
    st.info(
        "💳 Create sales using POS page."
    )

with c3:
    st.info(
        "📊 View detailed reports in Analytics page."
    )

# -----------------------------
# FOOTER
# -----------------------------
st.divider()

st.caption(
    f"Last Updated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
)

conn.close()