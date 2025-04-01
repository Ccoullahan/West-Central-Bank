from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = 'secret_key'

def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

users = load_users()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        pin = request.form["pin"]
        if username == "admin" and pin == "0000":
            session['user'] = 'admin'
            return redirect(url_for("admin"))
        if username in users and users[username]["pin"] == pin:
            session["user"] = username
            return redirect(url_for("dashboard"))
        return "Invalid credentials"
    return render_template("login.html")

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        pin = request.form["pin"]
        if username in users:
            return "Username already exists."
        users[username] = {"pin": pin, "balance": 0.0, "transactions": []}
        save_users(users)
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route('/dashboard')
def dashboard():
    user = session.get("user")
    if not user or user == "admin":
        return redirect(url_for("login"))
    data = users[user]
    return render_template("dashboard.html", user=user, balance=data["balance"], transactions=data["transactions"])

@app.route('/deposit', methods=["POST"])
def deposit():
    user = session["user"]
    amount = float(request.form["amount"])
    users[user]["balance"] += amount
    users[user]["transactions"].append(f"Deposited ${amount}")
    save_users(users)
    return redirect(url_for("dashboard"))

@app.route('/withdraw', methods=["POST"])
def withdraw():
    user = session["user"]
    amount = float(request.form["amount"])
    if amount <= users[user]["balance"]:
        users[user]["balance"] -= amount
        users[user]["transactions"].append(f"Withdrew ${amount}")
        save_users(users)
    return redirect(url_for("dashboard"))

@app.route('/admin')
def admin():
    if session.get("user") != "admin":
        return redirect(url_for("login"))
    return render_template("admin.html", users=users)

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
