# KayNet – Intelligent Trading Assistant

#### Video Demo:  https://youtu.be/jqgAoyQj2QA

#### Description

KayNet is a web-based stock trading simulator inspired by CS50 Finance and reimagined as a modern, minimalist trading assistant. It allows users to register, log in, look up real-time stock quotes, “buy” and “sell” shares, and view their transaction history and current portfolio, all inside a clean KayNet-branded interface.

The application is built with **Python (Flask)**, **SQLite**, **HTML/CSS (Bootstrap)**, and a stock price API (via a key such as Alpha Vantage / IEX). It uses a familiar CS50-style architecture with `app.py` as the core Flask application, Jinja templates under `templates/`, and static styling assets under `static/`. The goal of the project is to simulate a simple trading platform where the user can practice working with a portfolio without risking real money, and at the same time demonstrate knowledge of web programming, databases, sessions, and APIs.

---

## Features

- **User Authentication**
  - Register with a unique username and password.
  - Passwords are securely stored using hashes, not in plain text.
  - Login and logout functionality with session handling.

- **Portfolio Overview (Index Page)**
  - Shows all stocks currently owned by the logged-in user.
  - Displays each stock symbol, number of shares, current price, and total value.
  - Shows the user’s remaining cash and the overall portfolio total (cash + holdings).

- **Real-Time Stock Quotes**
  - `/quote` route allows users to type a stock symbol (e.g., AAPL, TSLA).
  - The app queries a stock price API and returns the latest price.
  - If an invalid symbol is entered, the user gets a friendly error (apology page).

- **Buying Stocks**
  - `/buy` route lets users enter a stock symbol and number of shares.
  - Validates that:
    - The symbol exists via the API.
    - The number of shares is a positive integer.
    - The user has enough cash to complete the purchase.
  - On success, inserts a transaction into the database and updates the user’s cash.

- **Selling Stocks**
  - `/sell` route shows a dropdown of symbols that the user currently owns.
  - Validates that:
    - The user selects a symbol actually owned.
    - The number of shares is a positive integer.
    - The user is not trying to sell more than they own.
  - On success, records a negative-share transaction and increases the user’s cash.

- **Transaction History**
  - `/history` route shows a table of all transactions (buys and sells).
  - Includes stock symbol, number of shares, price, and timestamp for each operation.

- **KayNet Branding & UI**
  - Custom navbar with **KayNet** logo and colors.
  - “Kay” highlighted in cyan and “Net” in white for a clean modern aesthetic.
  - Subtitle: “Intelligent Trading Assistant”.
  - Responsive design using Bootstrap so it looks good on both desktop and mobile.

---

## File Overview

- **`app.py`**
  The main Flask application. It:
  - Configures the database connection using CS50’s `SQL` or standard SQLite.
  - Implements all the routes:
    - `/` (index – portfolio overview)
    - `/register`
    - `/login`
    - `/logout`
    - `/quote`
    - `/buy`
    - `/sell`
    - `/history`
  - Handles form submissions, server-side validation, portfolio calculations, and API integration for stock prices.

- **`helpers.py`**
  Contains helper functions:
  - `apology(message, code)` – renders a simple error page.
  - `login_required` decorator – restricts access to certain routes unless user is logged in.
  - `lookup(symbol)` – queries the stock API and returns name, price, and symbol.
  - `usd(value)` – formats numbers as US dollar strings.

- **`finance.db`** (ignored in `.gitignore` when needed)
  - SQLite database storing:
    - `users` table: users, password hashes, and cash.
    - `transactions` table: each buy/sell with user_id, symbol, shares, price, and timestamp.

- **`templates/`**
  - `layout.html` – base template with KayNet navbar and main layout. Other templates extend this.
  - `index.html` – portfolio overview page showing current holdings and cash.
  - `login.html` – login form.
  - `register.html` – registration form.
  - `quote.html` – form to request stock quotes.
  - `quoted.html` – page showing a returned quote for a symbol.
  - `buy.html` – form to buy shares.
  - `sell.html` – form to sell shares (with a dropdown of owned stocks).
  - `history.html` – table of all user transactions.
  - `apology.html` – error page used by `apology()` helper.

- **`static/styles.css`**
  - Custom styling for the KayNet brand:
    - Gradient background.
    - Navbar style, typography choices, spacing.
    - Brand colors (cyan + white).
  - Works together with Bootstrap for responsive design.

- **`static/logo.svg` and `static/favicon.ico`**
  - Visual identity for KayNet (logo + tab icon).

- **`Procfile`**
  - Used for deployment (e.g., on platforms like Render).
  - Contains the process type and command, e.g. `web: gunicorn app:app`.

- **`.gitignore`**
  - Excludes files that should not be committed to version control, such as:
    - `finance.db`
    - `flask_session/`
    - `__pycache__/`
    - `.env`

---

## How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/utkarshvarun9029-tech/kaynet.git
   cd kaynet
