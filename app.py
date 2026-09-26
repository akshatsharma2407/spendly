from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import init_db, seed_db, get_db
from database.queries import (
    get_user_by_id,
    get_summary_stats,
    get_recent_transactions,
    get_category_breakdown
)
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'dev-secret-key-change-me-in-production'


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    user_name = None
    if session.get('user_id'):
        with get_db() as conn:
            user = conn.execute("SELECT name FROM users WHERE id = ?", (session['user_id'],)).fetchone()
            if user:
                user_name = user['name']
    return render_template("landing.html", user_name=user_name)


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get('user_id'):
        return redirect(url_for('landing'))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not password or len(password) < 8:
            return render_template("register.html", error="Password must be at least 8 characters long.")

        with get_db() as conn:
            existing_user = conn.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone()
            if existing_user:
                return render_template("register.html", error="An account with this email already exists.")

            hashed_password = generate_password_hash(password)
            conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, hashed_password)
            )
            conn.commit()

        return redirect(url_for('login'))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get('user_id'):
        return redirect(url_for('landing'))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        with get_db() as conn:
            user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect(url_for('profile'))

        return render_template("login.html", error="Invalid email or password.")

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('landing'))


@app.route("/profile")
@login_required
def profile():
    user_id = session.get('user_id')

    # Extract and validate date filters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    try:
        if start_date:
            datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        # Fallback to None if date format is invalid
        start_date = None
        end_date = None

    # Fetch filtered data from database helpers
    user_info = get_user_by_id(user_id)
    summary_stats = get_summary_stats(user_id, start_date=start_date, end_date=end_date)
    transactions = get_recent_transactions(user_id, start_date=start_date, end_date=end_date)
    category_breakdown = get_category_breakdown(user_id, start_date=start_date, end_date=end_date)

    return render_template(
        "profile.html",
        user=user_info,
        stats=summary_stats,
        transactions=transactions,
        breakdown=category_breakdown,
        filters=request.args # Pass args back to template to preserve form state
    )


@app.route("/expenses/add")
@login_required
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
@login_required
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
@login_required
def delete_expense(id):
    return "Delete expense — coming in Step 9"


# ------------------------------------------------------------------ #
# Database Initialization                                                 #
# ------------------------------------------------------------------ #
with app.app_context():
    init_db()
    seed_db()

if __name__ == "__main__":
    app.run(debug=True, port=5001)
