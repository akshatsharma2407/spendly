import pytest
from app import app as flask_app
from database.db import init_db, get_db
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'DATABASE': ':memory:',  # isolated in-memory DB per test
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })

    # We need to override get_db to use the in-memory database for testing
    # Since get_db is imported in app.py, we might need to patch it or
    # ensure database/db.py supports a configurable path.
    # For this specific test suite, we'll monkeypatch the DATABASE_PATH.
    import database.db
    database.db.DATABASE_PATH = ':memory:'

    with flask_app.app_context():
        init_db()
        yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """A test client that is already logged in."""
    # Register a user
    client.post('/register', data={'name': 'testuser', 'email': 'test@test.com', 'password': 'testpassword'})
    # Login
    client.post('/login', data={'email': 'test@test.com', 'password': 'testpassword'})
    return client

@pytest.fixture
def seed_expenses(auth_client):
    """Seeds specific expenses for date filtering tests."""
    with get_db() as conn:
        user_id = conn.execute("SELECT id FROM users WHERE email = ?", ('test@test.com',)).fetchone()['id']

        expenses = [
            # 2023-01-01
            (user_id, 10.0, "Food", "2023-01-01", "Lunch 1"),
            # 2023-01-15
            (user_id, 20.0, "Transport", "2023-01-15", "Bus"),
            # 2023-02-01
            (user_id, 30.0, "Food", "2023-02-01", "Lunch 2"),
            # 2023-02-15
            (user_id, 40.0, "Bills", "2023-02-15", "Electric"),
        ]
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses
        )
        conn.commit()

class TestDateFilterProfile:
    def test_profile_auth_guard(self, client):
        """Ensure /profile is protected by @login_required."""
        response = client.get('/profile')
        assert response.status_code == 302
        assert '/login' in response.location

    def test_profile_all_time_data(self, auth_client, seed_expenses):
        """Verify that /profile without filters shows all data."""
        response = auth_client.get('/profile')
        assert response.status_code == 200
        # Total should be 10 + 20 + 30 + 40 = 100
        assert b'100' in response.data
        # Should see multiple transactions
        assert b'Lunch 1' in response.data
        assert b'Electric' in response.data

    def test_filter_start_date_only(self, auth_client, seed_expenses):
        """Filtering with only start_date provided."""
        # From 2023-02-01 onwards: Lunch 2 (30) + Electric (40) = 70
        response = auth_client.get('/profile?start_date=2023-02-01')
        assert response.status_code == 200
        assert b'70' in response.data
        assert b'Lunch 2' in response.data
        assert b'Electric' in response.data
        assert b'Lunch 1' not in response.data

    def test_filter_end_date_only(self, auth_client, seed_expenses):
        """Filtering with only end_date provided."""
        # Until 2023-01-15: Lunch 1 (10) + Bus (20) = 30
        response = auth_client.get('/profile?end_date=2023-01-15')
        assert response.status_code == 200
        assert b'30' in response.data
        assert b'Lunch 1' in response.data
        assert b'Bus' in response.data
        assert b'Lunch 2' not in response.data

    def test_filter_date_range(self, auth_client, seed_expenses):
        """Filtering with both start_date and end_date."""
        # Between 2023-01-05 and 2023-01-20: Bus (20)
        response = auth_client.get('/profile?start_date=2023-01-05&end_date=2023-01-20')
        assert response.status_code == 200
        assert b'20' in response.data
        assert b'Bus' in response.data
        assert b'Lunch 1' not in response.data
        assert b'Lunch 2' not in response.data

    def test_filter_exact_date(self, auth_client, seed_expenses):
        """Date range that exactly matches a single transaction's date."""
        # Exactly 2023-02-01: Lunch 2 (30)
        response = auth_client.get('/profile?start_date=2023-02-01&end_date=2023-02-01')
        assert response.status_code == 200
        assert b'30' in response.data
        assert b'Lunch 2' in response.data
        assert b'Electric' not in response.data

    def test_filter_no_results(self, auth_client, seed_expenses):
        """Date ranges with no matching transactions should not crash."""
        response = auth_client.get('/profile?start_date=2024-01-01&end_date=2024-01-31')
        assert response.status_code == 200
        # Summary stats should likely be 0 or empty
        assert b'0' in response.data or b'No transactions' in response.data

    def test_filter_invalid_date_format(self, auth_client, seed_expenses):
        """Invalid date formats should default to all-time data."""
        response = auth_client.get('/profile?start_date=invalid-date&end_date=not-a-date')
        assert response.status_code == 200
        # Should revert to all-time: 100
        assert b'100' in response.data

    def test_filter_empty_date_strings(self, auth_client, seed_expenses):
        """Empty date strings should default to all-time data."""
        response = auth_client.get('/profile?start_date=&end_date=')
        assert response.status_code == 200
        assert b'100' in response.data

    def test_filter_reset(self, auth_client, seed_expenses):
        """Removing query parameters returns the view to all-time data."""
        # First filter
        auth_client.get('/profile?start_date=2023-02-01')
        # Then reset
        response = auth_client.get('/profile')
        assert response.status_code == 200
        assert b'100' in response.data
