import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")

st.title("📊 Business Analytics Dashboard")
st.markdown("Track sales, inventory performance, and business insights.")

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
conn = sqlite3.connect("inventory.db", check_same_thread=False)

# -----------------------------
# LOAD DATA
# -----------------------------
try:
    sales_df = pd.read_sql_query("SELECT * FROM sales", conn)
except:
    sales_df = pd.DataFrame()

try:
    products_df = pd.read_sql_query("SELECT * FROM products", conn)
except:
    products_df = pd.DataFrame()

# -----------------------------
# KPI SECTION
# -----------------------------
st.subheader("📌 Key Performance Indicators")

if not sales_df.empty:

    total_sales = sales_df["total_price"].sum()
    total_orders = len(sales_df)

    avg_order_value = (
        total_sales / total_orders if total_orders > 0 else 0
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "💰 Total Revenue",
        f"₹{total_sales:,.2f}"
    )

    col2.metric(
        "🧾 Total Orders",
        total_orders
    )

    col3.metric(
        "📦 Avg Order Value",
        f"₹{avg_order_value:,.2f}"
    )

else:
    st.warning("No sales data available.")

# -----------------------------
# SALES TREND
# -----------------------------
st.divider()

st.subheader("📈 Sales Trend")

if not sales_df.empty:

    if "sale_date" in sales_df.columns:

        sales_df["sale_date"] = pd.to_datetime(
            sales_df["sale_date"]
        )

        daily_sales = (
            sales_df.groupby(
                sales_df["sale_date"].dt.date
            )["total_price"]
            .sum()
            .reset_index()
        )

        fig = px.line(
            daily_sales,
            x="sale_date",
            y="total_price",
            markers=True,
            title="Daily Revenue"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# -----------------------------
# TOP SELLING PRODUCTS
# -----------------------------
st.divider()

st.subheader("🏆 Top Selling Products")

if not sales_df.empty:

    if "product_name" in sales_df.columns:

        top_products = (
            sales_df.groupby("product_name")
            ["quantity"]
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
            title="Top Selling Products",
            text_auto=True
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# -----------------------------
# CATEGORY PERFORMANCE
# -----------------------------
st.divider()

st.subheader("🛒 Category Performance")

if (
    not sales_df.empty
    and not products_df.empty
    and "product_name" in sales_df.columns
    and "name" in products_df.columns
):

    merged_df = sales_df.merge(
        products_df,
        left_on="product_name",
        right_on="name",
        how="left"
    )

    if "category" in merged_df.columns:

        category_sales = (
            merged_df.groupby("category")
            ["total_price"]
            .sum()
            .reset_index()
        )

        fig = px.pie(
            category_sales,
            names="category",
            values="total_price",
            title="Revenue by Category"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# -----------------------------
# INVENTORY STATUS
# -----------------------------
st.divider()

st.subheader("📦 Inventory Status")

if not products_df.empty:

    if "stock" in products_df.columns:

        fig = px.bar(
            products_df,
            x="name",
            y="stock",
            title="Current Inventory Levels",
            color="stock"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# -----------------------------
# LOW STOCK PRODUCTS
# -----------------------------
st.divider()

st.subheader("⚠️ Low Stock Alert")

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

# -----------------------------
# SALES TABLE
# -----------------------------
st.divider()

st.subheader("📄 Recent Sales")

if not sales_df.empty:

    st.dataframe(
        sales_df.sort_index(
            ascending=False
        ).head(20),
        use_container_width=True
    )

else:
    st.info("No sales records found.")

# -----------------------------
# DOWNLOAD REPORT
# -----------------------------
st.divider()

st.subheader("⬇ Export Sales Report")

if not sales_df.empty:

    csv = sales_df.to_csv(index=False)

    st.download_button(
        label="Download Sales Report",
        data=csv,
        file_name="sales_report.csv",
        mime="text/csv"
    )

conn.close()