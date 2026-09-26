import sqlite3
import random
from datetime import datetime, timedelta
from database.db import get_db

def seed_expenses(user_id, count, months):
    # Categories and their (min_amount, max_amount, weight)
    # Weights: Food most common, Health/Entertainment least
    CATEGORIES = {
        "Food": (50, 800, 30),
        "Transport": (20, 500, 20),
        "Bills": (200, 3000, 15),
        "Health": (100, 2000, 5),
        "Entertainment": (100, 1500, 5),
        "Shopping": (200, 5000, 15),
        "Other": (50, 1000, 10),
    }

    DESCRIPTIONS = {
        "Food": ["Lunch at Zomato", "Dinner at Swiggy", "Grocery from Blinkit", "Street Food", "Cafe Coffee Day", "Family Dinner", "Breakfast at Home"],
        "Transport": ["Auto Rickshaw", "Ola Cab", "Uber Ride", "Petrol Fill-up", "Metro Recharge", "Bus Fare"],
        "Bills": ["Electricity Bill", "Water Bill", "WiFi Bill", "Mobile Recharge", "Rent Payment", "Insurance Premium"],
        "Health": ["Apollo Pharmacy", "Doctor Consultation", "Medical Checkup", "Health Insurance"],
        "Entertainment": ["Movie Ticket", "Netflix Subscription", "Game Center", "Bowling", "Concert Ticket"],
        "Shopping": ["Amazon Shopping", "Flipkart Order", "Myntra Clothes", "Local Market", "Electronics"],
        "Other": ["Gift", "Donation", "Parking Fee", "Miscellaneous"],
    }

    try:
        conn = get_db()
        
        # Verify user exists
        user = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            print(f"No user found with id {user_id}.")
            return False

        # Generate expenses
        expenses = []
        start_date = datetime.now() - timedelta(days=months * 30)
        end_date = datetime.now()
        
        cat_list = list(CATEGORIES.keys())
        weights = [CATEGORIES[c][2] for c in cat_list]

        for _ in range(count):
            category = random.choices(cat_list, weights=weights)[0]
            min_amt, max_amt, _ = CATEGORIES[category]
            amount = round(random.uniform(min_amt, max_amt), 2)
            
            # Random date within the range
            random_days = random.randint(0, months * 30)
            date_obj = start_date + timedelta(days=random_days)
            date_str = date_obj.strftime("%Y-%m-%d")
            
            description = random.choice(DESCRIPTIONS[category])
            expenses.append((user_id, amount, category, date_str, description))

        # Insert in a single transaction
        try:
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                expenses
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Transaction failed: {e}")
            return False
        finally:
            conn.close()

        # Confirmation
        inserted_count = len(expenses)
        dates = [e[3] for e in expenses]
        date_range = f"{min(dates)} to {max(dates)}"
        
        print(f"Successfully inserted {inserted_count} expenses.")
        print(f"Date range: {date_range}")
        print("\nSample records:")
        for i in range(min(5, inserted_count)):
            e = expenses[i]
            print(f"Date: {e[3]} | Category: {e[2]} | Amount: Rs {e[1]} | Desc: {e[4]}")
        
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python seed_expenses_script.py <user_id> <count> <months>")
        sys.exit(1)
    
    try:
        uid = int(sys.argv[1])
        cnt = int(sys.argv[2])
        mths = int(sys.argv[3])
        if not seed_expenses(uid, cnt, mths):
            sys.exit(1)
    except ValueError:
        print("Usage: python seed_expenses_script.py <user_id> <count> <months>")
        sys.exit(1)
