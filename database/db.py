import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

DATABASE_PATH = "spendly.db"

def get_db():
    """
    Returns a SQLite connection with row_factory set to sqlite3.Row
    and foreign keys enabled.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """
    Creates all necessary tables for the Spendly application.
    """
    with get_db() as conn:
        # Users Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)

        # Expenses Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.commit()
    print("Database initialized successfully.")

def seed_db():
    """
    Inserts sample data for development if the database is empty.
    """
    with get_db() as conn:
        # Check if users table already contains data
        user_exists = conn.execute("SELECT 1 FROM users LIMIT 1").fetchone()
        if user_exists:
            return

        # Insert demo user
        hashed_password = generate_password_hash("demo123")
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", hashed_password)
        )
        user_id = cursor.lastrowid

        # Sample expenses data
        # Categories: Food, Transport, Bills, Health, Entertainment, Shopping, Other
        today = datetime.now().strftime("%Y-%m-%d")

        expenses = [
            (user_id, 15.50, "Food", today, "Lunch at Cafe"),
            (user_id, 45.00, "Transport", today, "Weekly fuel"),
            (user_id, 120.00, "Bills", today, "Internet Bill"),
            (user_id, 30.00, "Health", today, "Pharmacy"),
            (user_id, 20.00, "Entertainment", today, "Cinema"),
            (user_id, 60.00, "Shopping", today, "New T-shirt"),
            (user_id, 10.00, "Other", today, "Parking fee"),
            (user_id, 25.00, "Food", today, "Dinner with friends"),
        ]

        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses
        )
        conn.commit()
    print("Database seeded successfully.")

if __name__ == "__main__":
    init_db()
    seed_db()
