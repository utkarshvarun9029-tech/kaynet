import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# -------------------------
# INDEX
# -------------------------
@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]

    # Get cash
    rows = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
    cash = rows[0]["cash"] if rows else 0

    # Get holdings (symbol + sum of shares)
    holdings_query = db.execute(
        "SELECT symbol, SUM(shares) AS shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING shares > 0",
        user_id
    )

    holdings = []
    total = cash

    for row in holdings_query:
        symbol = row["symbol"]
        shares = row["shares"]
        quote = lookup(symbol)
        if quote is None:
            # fallback if API fails
            price = 0
            name = symbol
        else:
            price = quote["price"]
            name = quote.get("name", symbol)

        value = price * shares
        total += value

        holdings.append({
            "symbol": symbol,
            "name": name,
            "shares": shares,
            "price": price,
            "total": value
        })

    return render_template("index.html", holdings=holdings, cash=cash, grand_total=total)


# -------------------------
# QUOTE
# -------------------------
@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide symbol", 400)

        quote = lookup(symbol)
        if quote is None:
            return apology("invalid symbol", 400)

        # pass a simple dict to template
        return render_template("quoted.html", quote=quote)
    else:
        return render_template("quote.html")


# -------------------------
# BUY
# -------------------------
@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol:
            return apology("must provide symbol", 400)
        if not shares:
            return apology("must provide shares", 400)

        # ensure integer shares
        try:
            shares = int(shares)
            if shares <= 0:
                return apology("shares must be a positive integer", 400)
        except ValueError:
            return apology("shares must be a positive integer", 400)

        quote = lookup(symbol)
        if quote is None:
            return apology("invalid symbol", 400)

        price = quote["price"]
        cost = price * shares

        rows = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        if not rows:
            return apology("user not found", 500)
        cash = rows[0]["cash"]

        if cost > cash:
            return apology("can't afford", 400)

        # record purchase
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
            session["user_id"], quote["symbol"], shares, price
        )
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", cost, session["user_id"])

        return redirect("/")
    else:
        return render_template("buy.html")


# -------------------------
# SELL
# -------------------------
@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]

    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol:
            return apology("must provide symbol", 400)
        if not shares:
            return apology("must provide shares", 400)

        try:
            shares = int(shares)
            if shares <= 0:
                return apology("shares must be a positive integer", 400)
        except ValueError:
            return apology("shares must be a positive integer", 400)

        # check how many owned
        rows = db.execute(
            "SELECT SUM(shares) AS shares FROM transactions WHERE user_id = ? AND symbol = ? GROUP BY symbol",
            user_id, symbol
        )
        owned = rows[0]["shares"] if rows else 0
        if shares > owned:
            return apology("too many shares", 400)

        quote = lookup(symbol)
        if quote is None:
            return apology("invalid symbol", 400)

        price = quote["price"]

        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
            user_id, symbol, -shares, price
        )
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", price * shares, user_id)

        return redirect("/")
    else:
        # show symbols user owns
        rows = db.execute(
            "SELECT symbol FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0",
            user_id
        )
        symbols = [r["symbol"] for r in rows]
        return render_template("sell.html", symbols=symbols)


# -------------------------
# HISTORY
# -------------------------
@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    rows = db.execute(
        "SELECT symbol, shares, price, time FROM transactions WHERE user_id = ? ORDER BY time DESC",
        session["user_id"]
    )
    # optionally convert type for display (BUY/SELL)
    out = []
    for r in rows:
        out.append({
            "symbol": r["symbol"],
            "shares": r["shares"],
            "price": r["price"],
            "time": r["time"],
            "type": "BUY" if r["shares"] > 0 else "SELL"
        })
    return render_template("history.html", rows=out)


# -------------------------
# REGISTER / LOGIN / LOGOUT
# -------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("must provide username", 400)
        if not password:
            return apology("must provide password", 400)
        if password != confirmation:
            return apology("passwords do not match", 400)

        # try insert, handle duplicate
        try:
            hash_pw = generate_password_hash(password)
            new_id = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_pw)
        except Exception:
            return apology("username already exists", 400)

        # log in new user
        session["user_id"] = new_id
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)
        if not request.form.get("password"):
            return apology("must provide password", 403)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        session["user_id"] = rows[0]["id"]
        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")
