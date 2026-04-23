import streamlit as st
import sqlite3

# ---------------- DATABASE ----------------
def connect():
    return sqlite3.connect("users.db", check_same_thread=False)

conn = connect()
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    account_no TEXT UNIQUE,
    password TEXT,
    balance REAL
)
""")
conn.commit()

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- FUNCTIONS ----------------
def create_account(name, acc, pwd):
    try:
        cur.execute("INSERT INTO users(name, account_no, password, balance) VALUES (?, ?, ?, ?)",
                    (name, acc, pwd, 0))
        conn.commit()
        return True
    except:
        return False

def login(acc, pwd):
    cur.execute("SELECT * FROM users WHERE account_no=? AND password=?", (acc, pwd))
    return cur.fetchone()

def get_balance(acc):
    cur.execute("SELECT balance FROM users WHERE account_no=?", (acc,))
    return cur.fetchone()[0]

def deposit(acc, amt):
    cur.execute("UPDATE users SET balance = balance + ? WHERE account_no=?", (amt, acc))
    conn.commit()

def withdraw(acc, amt):
    cur.execute("SELECT balance FROM users WHERE account_no=?", (acc,))
    bal = cur.fetchone()[0]
    if bal >= amt:
        cur.execute("UPDATE users SET balance = balance - ? WHERE account_no=?", (amt, acc))
        conn.commit()
        return True
    return False

# ---------------- UI ----------------

st.title("🏦 Smart Banking System")

menu = ["Home", "Login", "Create Account"]
choice = st.sidebar.selectbox("Menu", menu)

# ---------------- HOME ----------------
if choice == "Home":
    st.subheader("Welcome to Smart Bank")
    st.write("Create account or login to continue")

# ---------------- CREATE ACCOUNT ----------------
elif choice == "Create Account":
    st.subheader("Create New Account")

    name = st.text_input("Name")
    acc = st.text_input("Account Number")
    pwd = st.text_input("Password", type="password")

    if st.button("Create Account"):
        if create_account(name, acc, pwd):
            st.success("Account Created Successfully")
        else:
            st.error("Account already exists")

# ---------------- LOGIN ----------------
elif choice == "Login":
    st.subheader("Login")

    acc = st.text_input("Account Number")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login(acc, pwd)
        if user:
            st.session_state.user = acc
            st.success("Login Successful")
        else:
            st.error("Invalid Details")

# ---------------- DASHBOARD ----------------
if st.session_state.user:
    st.sidebar.success("Logged In")

    st.subheader("Dashboard")

    balance = get_balance(st.session_state.user)
    st.write(f"💳 Balance: ₹{balance}")

    amt = st.number_input("Enter Amount", min_value=0.0)

    col1, col2 = st.columns(2)

    if col1.button("Deposit"):
        deposit(st.session_state.user, amt)
        st.success("Deposited")

    if col2.button("Withdraw"):
        if withdraw(st.session_state.user, amt):
            st.success("Withdraw Successful")
        else:
            st.error("Insufficient Balance")

    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()
