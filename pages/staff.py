import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(
    page_title="Staff Management",
    page_icon="👨‍💼",
    layout="wide"
)

st.title("👨‍💼 Staff Management")
st.caption("Manage employees, attendance, and staff records.")

# ----------------------------------
# DATABASE CONNECTION
# ----------------------------------
conn = sqlite3.connect(
    "inventory.db",
    check_same_thread=False
)
cursor = conn.cursor()

# ----------------------------------
# CREATE TABLES
# ----------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    role TEXT,
    phone TEXT,
    salary REAL,
    joining_date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER,
    staff_name TEXT,
    attendance_date TEXT,
    status TEXT
)
""")

conn.commit()

# ----------------------------------
# ADD STAFF
# ----------------------------------
st.subheader("➕ Add Staff Member")

with st.form("staff_form"):

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Full Name")

        role = st.selectbox(
            "Role",
            [
                "Manager",
                "Cashier",
                "Sales Executive",
                "Store Keeper",
                "Delivery Staff",
                "Other"
            ]
        )

    with col2:
        phone = st.text_input("Phone Number")

        salary = st.number_input(
            "Monthly Salary",
            min_value=0.0,
            step=1000.0
        )

    joining_date = st.date_input(
        "Joining Date"
    )

    submitted = st.form_submit_button(
        "Add Staff"
    )

    if submitted:

        cursor.execute("""
        INSERT INTO staff
        (
            name,
            role,
            phone,
            salary,
            joining_date
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            name,
            role,
            phone,
            salary,
            str(joining_date)
        ))

        conn.commit()

        st.success(
            "Staff member added successfully."
        )

# ----------------------------------
# STAFF LIST
# ----------------------------------
st.divider()

st.subheader("👥 Staff Directory")

staff_df = pd.read_sql_query(
    "SELECT * FROM staff",
    conn
)

if not staff_df.empty:

    st.dataframe(
        staff_df,
        use_container_width=True
    )

else:
    st.info("No staff records found.")

# ----------------------------------
# ATTENDANCE
# ----------------------------------
st.divider()

st.subheader("📅 Mark Attendance")

if not staff_df.empty:

    selected_staff = st.selectbox(
        "Select Staff",
        staff_df["name"].tolist()
    )

    attendance_status = st.radio(
        "Attendance Status",
        [
            "Present",
            "Absent",
            "Half Day"
        ]
    )

    if st.button("Mark Attendance"):

        staff_row = staff_df[
            staff_df["name"] == selected_staff
        ].iloc[0]

        today = datetime.now().strftime(
            "%Y-%m-%d"
        )

        cursor.execute("""
        INSERT INTO attendance
        (
            staff_id,
            staff_name,
            attendance_date,
            status
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            int(staff_row["id"]),
            selected_staff,
            today,
            attendance_status
        ))

        conn.commit()

        st.success(
            "Attendance marked successfully."
        )

# ----------------------------------
# ATTENDANCE REPORT
# ----------------------------------
st.divider()

st.subheader("📊 Attendance Records")

attendance_df = pd.read_sql_query(
    """
    SELECT *
    FROM attendance
    ORDER BY attendance_date DESC
    """,
    conn
)

if not attendance_df.empty:

    st.dataframe(
        attendance_df,
        use_container_width=True
    )

else:
    st.info("No attendance records.")

# ----------------------------------
# UPDATE STAFF
# ----------------------------------
st.divider()

st.subheader("✏️ Update Staff Details")

if not staff_df.empty:

    selected_update = st.selectbox(
        "Select Employee",
        staff_df["name"].tolist(),
        key="update_staff"
    )

    employee = staff_df[
        staff_df["name"] == selected_update
    ].iloc[0]

    new_phone = st.text_input(
        "Phone",
        value=employee["phone"]
    )

    new_salary = st.number_input(
        "Salary",
        value=float(employee["salary"])
    )

    if st.button("Update Employee"):

        cursor.execute("""
        UPDATE staff
        SET phone = ?,
            salary = ?
        WHERE id = ?
        """,
        (
            new_phone,
            new_salary,
            int(employee["id"])
        ))

        conn.commit()

        st.success(
            "Employee updated successfully."
        )

# ----------------------------------
# DELETE STAFF
# ----------------------------------
st.divider()

st.subheader("🗑️ Delete Staff")

if not staff_df.empty:

    delete_staff = st.selectbox(
        "Choose Employee",
        staff_df["name"].tolist(),
        key="delete_staff"
    )

    if st.button("Delete Employee"):

        cursor.execute("""
        DELETE FROM staff
        WHERE name = ?
        """,
        (delete_staff,)
        )

        conn.commit()

        st.success(
            "Employee removed successfully."
        )

        st.rerun()

# ----------------------------------
# STAFF SUMMARY
# ----------------------------------
st.divider()

st.subheader("📈 Staff Summary")

if not staff_df.empty:

    total_staff = len(staff_df)

    total_salary = (
        staff_df["salary"].sum()
    )

    managers = len(
        staff_df[
            staff_df["role"] == "Manager"
        ]
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Staff",
        total_staff
    )

    col2.metric(
        "Monthly Payroll",
        f"₹{total_salary:,.0f}"
    )

    col3.metric(
        "Managers",
        managers
    )

# ----------------------------------
# EXPORT STAFF DATA
# ----------------------------------
st.divider()

st.subheader("⬇️ Export Staff Data")

if not staff_df.empty:

    csv = staff_df.to_csv(
        index=False
    )

    st.download_button(
        label="Download Staff CSV",
        data=csv,
        file_name="staff_records.csv",
        mime="text/csv"
    )

# ----------------------------------
# FOOTER
# ----------------------------------
st.divider()

st.caption(
    f"Last Updated: "
    f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
)

conn.close()