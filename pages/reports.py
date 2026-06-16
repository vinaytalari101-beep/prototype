import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(
    page_title="Reports",
    page_icon="📑",
    layout="wide"
)

st.title("📑 Reports & Business Insights")
st.caption("Generate sales reports and export business data.")

# ----------------------------------
# DATABASE
# ----------------------------------
conn = sqlite3.connect(
    "inventory.db",
    check_same_thread=False
)

# ----------------------------------
# LOAD SALES DATA
# ----------------------------------
try:
    sales_df = pd.read_sql_query(
        "SELECT * FROM sales",
        conn
    )

except:
    sales_df = pd.DataFrame()

if sales_df.empty:
    st.warning("No sales records found.")
    st.stop()

# ----------------------------------
# DATE FILTER
# ----------------------------------
st.subheader("📅 Filter Reports")

# Parse dates safely (coerce invalid/missing values to NaT)
sales_df["sale_date"] = pd.to_datetime(
    sales_df.get("sale_date", pd.NaT),
    errors="coerce"
)

# Determine sensible defaults for the date inputs
min_dt = sales_df["sale_date"].min()
if pd.isna(min_dt):
    min_dt = datetime.today()

max_dt = sales_df["sale_date"].max()
if pd.isna(max_dt):
    max_dt = datetime.today()

col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input(
        "Start Date",
        min_dt.date()
    )

with col2:
    end_date = st.date_input(
        "End Date",
        max_dt.date()
    )

filtered_df = sales_df[
    (sales_df["sale_date"].dt.date >= start_date)
    &
    (sales_df["sale_date"].dt.date <= end_date)
]

# ----------------------------------
# KPI SECTION
# ----------------------------------
st.divider()

st.subheader("📊 Report Summary")

total_revenue = filtered_df[
    "total_price"
].sum()

total_sales = len(filtered_df)

total_items = filtered_df[
    "quantity"
].sum()

total_invoices = filtered_df[
    "invoice_no"
].nunique()

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Revenue",
    f"₹{total_revenue:,.2f}"
)

c2.metric(
    "Transactions",
    total_sales
)

c3.metric(
    "Items Sold",
    total_items
)

c4.metric(
    "Invoices",
    total_invoices
)

# ----------------------------------
# INVOICE SEARCH
# ----------------------------------
st.divider()

st.subheader("🔍 Search Invoice")

invoice_search = st.text_input(
    "Enter Invoice Number"
)

if invoice_search:

    invoice_df = filtered_df[
        filtered_df["invoice_no"]
        .str.contains(
            invoice_search,
            case=False,
            na=False
        )
    ]

    st.dataframe(
        invoice_df,
        use_container_width=True
    )

# ----------------------------------
# PRODUCT PERFORMANCE
# ----------------------------------
st.divider()

st.subheader("🏆 Top Selling Products")

top_products = (
    filtered_df
    .groupby("product_name")["quantity"]
    .sum()
    .reset_index()
    .sort_values(
        by="quantity",
        ascending=False
    )
)

if not top_products.empty:

    st.dataframe(
        top_products,
        use_container_width=True
    )

# ----------------------------------
# REVENUE BY PRODUCT
# ----------------------------------
st.divider()

st.subheader("💰 Revenue By Product")

revenue_product = (
    filtered_df
    .groupby("product_name")["total_price"]
    .sum()
    .reset_index()
    .sort_values(
        by="total_price",
        ascending=False
    )
)

st.dataframe(
    revenue_product,
    use_container_width=True
)

# ----------------------------------
# COMPLETE SALES TABLE
# ----------------------------------
st.divider()

st.subheader("📄 Sales Transactions")

st.dataframe(
    filtered_df.sort_values(
        by="sale_date",
        ascending=False
    ),
    use_container_width=True
)

# ----------------------------------
# DOWNLOAD CSV
# ----------------------------------
st.divider()

st.subheader("⬇ Export Reports")

csv = filtered_df.to_csv(
    index=False
)

st.download_button(
    label="Download Sales Report CSV",
    data=csv,
    file_name="sales_report.csv",
    mime="text/csv"
)

# ----------------------------------
# DAILY REVENUE TABLE
# ----------------------------------
st.divider()

st.subheader("📈 Daily Revenue")

daily_sales = (
    filtered_df
    .groupby(
        filtered_df["sale_date"].dt.date
    )["total_price"]
    .sum()
    .reset_index()
)

daily_sales.columns = [
    "Date",
    "Revenue"
]

st.dataframe(
    daily_sales,
    use_container_width=True
)

# ----------------------------------
# MONTHLY REVENUE TABLE
# ----------------------------------
st.divider()

st.subheader("📅 Monthly Revenue")

filtered_df["Month"] = (
    filtered_df["sale_date"]
    .dt.strftime("%Y-%m")
)

monthly_sales = (
    filtered_df
    .groupby("Month")["total_price"]
    .sum()
    .reset_index()
)

st.dataframe(
    monthly_sales,
    use_container_width=True
)

# ----------------------------------
# BUSINESS HEALTH REPORT
# ----------------------------------
st.divider()

st.subheader("🏪 Business Health")

if total_revenue > 100000:
    st.success(
        "Excellent business performance."
    )

elif total_revenue > 50000:
    st.info(
        "Good business growth."
    )

else:
    st.warning(
        "Revenue is currently low. Increase sales promotions."
    )

# ----------------------------------
# FOOTER
# ----------------------------------
st.divider()

st.caption(
    f"Generated on {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
)

conn.close()