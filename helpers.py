import requests
from functools import wraps
from flask import redirect, render_template, session

# ---- currency formatter ----
def usd(value):
    try:
        return f"${value:,.2f}"
    except Exception:
        return "$0.00"

# ---- apology ----
def apology(message, code=400):
    """Render message as apology page"""
    return render_template("apology.html", top=code, bottom=message), code

# ---- login_required decorator ----
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# ---- lookup using AlphaVantage (or you can replace with mock) ----
API_KEY = "4OSNOS4OPRYSOPHX"   # <-- your key; rotate or keep private

def lookup(symbol):
    """Look up quote price using AlphaVantage GLOBAL_QUOTE"""
    try:
        symbol = symbol.strip().upper()
        url = "https://www.alphavantage.co/query"
        params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": API_KEY}
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()

        if "Global Quote" not in data or not data["Global Quote"]:
            return None

        q = data["Global Quote"]
        price = float(q.get("05. price", 0))
        return {"symbol": symbol, "name": symbol, "price": price}
    except Exception:
        return None
