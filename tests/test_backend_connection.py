import unittest
import sqlite3
import os
from database.db import get_db, init_db
from database.queries import get_recent_transactions, get_summary_stats, get_category_breakdown

class TestBackendConnection(unittest.TestCase):
    def setUp(self):
        # Use a temporary database for testing
        self.test_db = "test_spendly.db"
        # Patch DATABASE_PATH in database.db
        import database.db
        self.original_db_path = database.db.DATABASE_PATH
        database.db.DATABASE_PATH = self.test_db

        # Initialize the test database
        # Instead of removing the file which can fail on Windows due to locks,
        # we can just run init_db and then clear the tables.
        init_db()

        # Create test users
        with get_db() as conn:
            conn.execute("DELETE FROM expenses")
            conn.execute("DELETE FROM users")
            conn.commit()

            conn.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                         ("User With Expenses", "user1@test.com", "hash1"))
            conn.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                         ("User Without Expenses", "user2@test.com", "hash2"))
            conn.commit()
            self.user_with_id = conn.execute("SELECT id FROM users WHERE email = 'user1@test.com'").fetchone()[0]
            self.user_without_id = conn.execute("SELECT id FROM users WHERE email = 'user2@test.com'").fetchone()[0]

            # Insert some expenses for user 1
            expenses = [
                (self.user_with_id, 10.0, "Food", "2023-10-01", "Lunch"),
                (self.user_with_id, 20.0, "Transport", "2023-10-02", "Taxi"),
                (self.user_with_id, 30.0, "Bills", "2023-10-03", "Internet"),
                (self.user_with_id, 40.0, "Health", "2023-10-04", "Meds"),
                (self.user_with_id, 50.0, "Entertainment", "2023-10-05", "Movie"),
                (self.user_with_id, 60.0, "Shopping", "2023-10-06", "Clothes"),
                (self.user_with_id, 70.0, "Other", "2023-10-07", "Misc"),
                (self.user_with_id, 80.0, "Food", "2023-10-08", "Dinner"),
                (self.user_with_id, 90.0, "Transport", "2023-10-09", "Fuel"),
                (self.user_with_id, 100.0, "Bills", "2023-10-10", "Rent"),
                (self.user_with_id, 110.0, "Health", "2023-10-11", "Checkup"),
            ]
            conn.executemany(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                expenses
            )
            conn.commit()

    def tearDown(self):
        # Restore original database path
        import database.db
        database.db.DATABASE_PATH = self.original_db_path
        # Remove temporary database file
        try:
            if os.path.exists(self.test_db):
                os.remove(self.test_db)
        except PermissionError:
            pass

    def test_get_recent_transactions_with_expenses(self):
        """Verify it returns the correct records for a user with expenses."""
        transactions = get_recent_transactions(self.user_with_id)
        self.assertEqual(len(transactions), 10) # Default limit
        self.assertEqual(transactions[0]["date"], "2023-10-11") # Most recent
        self.assertEqual(transactions[0]["description"], "Checkup")

    def test_get_recent_transactions_no_expenses(self):
        """Verify it returns an empty list for a user with no expenses."""
        transactions = get_recent_transactions(self.user_without_id)
        self.assertEqual(transactions, [])

    def test_get_recent_transactions_limit(self):
        """Verify it respects the limit parameter."""
        limit = 5
        transactions = get_recent_transactions(self.user_with_id, limit=limit)
        self.assertEqual(len(transactions), limit)
        self.assertEqual(transactions[0]["date"], "2023-10-11")

    def test_get_summary_stats_with_expenses(self):
        """Verify it returns the correct totals and top category for a user with expenses."""
        stats = get_summary_stats(self.user_with_id)

        # Total spent: 10+20+30+40+50+60+70+80+90+100+110 = 660
        self.assertEqual(stats["total_spent"], 660.0)
        self.assertEqual(stats["transaction_count"], 11)
        # Top category: Health (110+40=150), Bills (100+30=130), Transport (90+20=110), Food (80+10=90)
        self.assertEqual(stats["top_category"], "Health")

    def test_get_summary_stats_no_expenses(self):
        """Verify it returns defaults for a user with no expenses."""
        stats = get_summary_stats(self.user_without_id)
        self.assertEqual(stats["total_spent"], 0.0)
        self.assertEqual(stats["transaction_count"], 0)
        self.assertEqual(stats["top_category"], "—")

    def test_get_category_breakdown_no_expenses(self):
        """Verify it returns an empty list for a user with no expenses."""
        result = get_category_breakdown(self.user_without_id)
        self.assertEqual(result, [])

    def test_get_category_breakdown_with_expenses(self):
        """Verify it returns correct amounts and percentages for a user with expenses."""
        # User 1 totals: 660.0
        # Health: 150 (150/660 = 22.7% -> 23%)
        # Bills: 130 (130/660 = 19.6% -> 20%)
        # Transport: 110 (110/660 = 16.6% -> 17%)
        # Food: 90 (90/660 = 13.6% -> 14%)
        # Other: 70 (70/660 = 10.6% -> 11%)
        # Shopping: 60 (60/660 = 9.09% -> 9%)
        # Entertainment: 50 (50/660 = 7.57% -> 8%)
        # Sum: 23+20+17+14+11+9+8 = 102. Diff = -2.
        # Largest (Health) gets -2 -> 21%.
        # Sum: 21+20+17+14+11+9+8 = 100.

        result = get_category_breakdown(self.user_with_id)

        self.assertEqual(len(result), 7)
        self.assertEqual(result[0]["category"], "Health")
        self.assertEqual(result[0]["amount"], 150.0)

        total_pct = sum(item["percentage"] for item in result)
        self.assertEqual(total_pct, 100)

    def test_get_category_breakdown_rounding_correction(self):
        """Verify percentages sum to 100% with tricky rounding."""
        # Use a separate user for this test to control data
        with get_db() as conn:
            conn.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                         ("Rounding User", "round@test.com", "hash"))
            round_user_id = conn.execute("SELECT id FROM users WHERE email = 'round@test.com'").fetchone()[0]

            # Total = 100. 33.34, 33.33, 33.33
            # Rounded: 33, 33, 33 = 99. Diff = 1.
            expenses = [
                (round_user_id, 33.34, "Food", "2023-01-01", "A"),
                (round_user_id, 33.33, "Transport", "2023-01-01", "B"),
                (round_user_id, 33.33, "Bills", "2023-01-01", "C"),
            ]
            conn.executemany(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                expenses
            )
            conn.commit()

        result = get_category_breakdown(round_user_id)
        total_pct = sum(item["percentage"] for item in result)
        self.assertEqual(total_pct, 100)
        # Food is largest, gets the +1
        self.assertEqual(result[0]["category"], "Food")
        self.assertEqual(result[0]["percentage"], 34)

if __name__ == "__main__":
    unittest.main()
