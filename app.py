import streamlit as st

from database import (
    init_db,
    create_default_admin
)

from auth import login_page

# -------------------
# PAGE CONFIG
# -------------------

st.set_page_config(
    page_title="Smart Inventory AI",
    page_icon="📦",
    layout="wide"
)

# -------------------
# DATABASE INIT
# -------------------

init_db()
create_default_admin()

# -------------------
# SESSION
# -------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# -------------------
# LOGIN
# -------------------

if not st.session_state.logged_in:
    login_page()
    st.stop()

# -------------------
# MAIN APP
# -------------------

st.title("🏪 Smart Inventory Management System")

st.success(
    f"Welcome {st.session_state.username}"
)

st.markdown(
"""
### Features

✅ Product Management

✅ POS Billing

✅ Invoice Generation

✅ Analytics Dashboard

✅ Low Stock Alerts

✅ Reports

✅ Voice Search

"""
)

st.info(
"""
Use the left sidebar to open:

Dashboard

Inventory

POS

Analytics

Reports
"""
)

# Sidebar Logout

with st.sidebar:

    st.title("⚙ Menu")

    if st.button("Logout"):

        st.session_state.logged_in = False
        st.rerun()