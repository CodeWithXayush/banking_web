from flask import Flask, request, redirect, session, render_template_string
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE ----------------
def connect():
    return sqlite3.connect("users.db")

def create_table():
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
    conn.close()

create_table()

# ---------------- HTML TEMPLATES ----------------

index_html = """
<!DOCTYPE html>
<html>
<head>
<title>Bank</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-dark text-white">

<div class="container mt-5">
<div class="card p-4">
<h2 class="text-center text-primary">🏦 Smart Bank</h2>

<form action="/create" method="post">
<input class="form-control mb-2" name="name" placeholder="Name">
<input class="form-control mb-2" name="acc" placeholder="Account No">
<input class="form-control mb-2" name="pwd" type="password" placeholder="Password">
<button class="btn btn-success w-100">Create Account</button>
</form>

<hr>
<a href="/login" class="btn btn-primary w-100">Login</a>

</div>
</div>
</body>
</html>
"""

login_html = """
<!DOCTYPE html>
<html>
<head>
<title>Login</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-secondary">

<div class="container mt-5">
<div class="card p-4">
<h2 class="text-center">Login</h2>

<form method="post">
<input class="form-control mb-3" name="acc" placeholder="Account Number">
<input class="form-control mb-3" name="pwd" type="password" placeholder="Password">
<button class="btn btn-success w-100">Login</button>
</form>

</div>
</div>
</body>
</html>
"""

dashboard_html = """
<!DOCTYPE html>
<html>
<head>
<title>Dashboard</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">

<div class="container mt-5">
<div class="card p-4">

<h2 class="text-center text-success">Dashboard</h2>
<h4 class="text-center">Balance: ₹{{balance}}</h4>

<form method="post">
<input class="form-control mb-3" name="amt" placeholder="Amount">
<button class="btn btn-success w-50" name="action" value="deposit">Deposit</button>
<button class="btn btn-danger w-50" name="action" value="withdraw">Withdraw</button>
</form>

<br>
<a href="/logout" class="btn btn-dark w-100">Logout</a>

</div>
</div>
</body>
</html>
"""

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template_string(index_html)

@app.route("/create", methods=["POST"])
def create():
    name = request.form["name"]
    acc = request.form["acc"]
    pwd = request.form["pwd"]

    conn = connect()
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO users(name, account_no, password, balance) VALUES (?, ?, ?, ?)",
                    (name, acc, pwd, 0))
        conn.commit()
        msg = "Account Created"
    except:
        msg = "Account already exists"

    conn.close()
    return f"{msg} <br><a href='/'>Go Back</a>"

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        acc = request.form["acc"]
        pwd = request.form["pwd"]

        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE account_no=? AND password=?", (acc, pwd))
        user = cur.fetchone()
        conn.close()

        if user:
            session["acc"] = acc
            return redirect("/dashboard")
        else:
            return "Wrong details"

    return render_template_string(login_html)

@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    acc = session.get("acc")

    if not acc:
        return redirect("/login")

    conn = connect()
    cur = conn.cursor()

    if request.method == "POST":
        amt = float(request.form["amt"])
        action = request.form["action"]

        if action == "deposit":
            cur.execute("UPDATE users SET balance = balance + ? WHERE account_no=?", (amt, acc))
        elif action == "withdraw":
            cur.execute("SELECT balance FROM users WHERE account_no=?", (acc,))
            bal = cur.fetchone()[0]
            if bal >= amt:
                cur.execute("UPDATE users SET balance = balance - ? WHERE account_no=?", (amt, acc))

        conn.commit()

    cur.execute("SELECT balance FROM users WHERE account_no=?", (acc,))
    balance = cur.fetchone()[0]

    conn.close()

    return render_template_string(dashboard_html, balance=balance)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)