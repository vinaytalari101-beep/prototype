from database import get_connection
import streamlit as st


def login(username, password):

    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    SELECT * FROM users
    WHERE username=?
    AND password=?
    """, (username, password))

    user = c.fetchone()

    conn.close()

    return user


def login_page():

    st.title("🔐 Smart Inventory Login")

    username = st.text_input("Username")
    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        user = login(
            username,
            password
        )

        if user:

            st.session_state.logged_in = True
            st.session_state.username = username

            st.success("Login Successful")
            st.rerun()

        else:
            st.error("Invalid Credentials")