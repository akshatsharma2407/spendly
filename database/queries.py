from database.db import get_db
from datetime import datetime

def get_user_by_id(user_id):
    """
    Fetches user profile information.
    Returns a dictionary with name, email, and member_since (formatted as 'Month YYYY').
    """
    with get_db() as conn:
        row = conn.execute(
            "SELECT name, email, created_at FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

        if not row:
            return None

        # Format created_at to 'Month YYYY'
        created_at_dt = datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S')
        member_since = created_at_dt.strftime("%B %Y")

        return {
            "name": row['name'],
            "email": row['email'],
            "member_since": member_since
        }

def get_category_breakdown(user_id):

    """
    Calculates the spend breakdown by category for a given user.
    Returns a list of dictionaries with category, amount, and percentage,
    ordered by amount descending.
    """
    with get_db() as conn:
        # Get total spend first for percentage calculations
        total_row = conn.execute(
            "SELECT SUM(amount) as total FROM expenses WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        total_amount = total_row['total'] if total_row and total_row['total'] else 0

        if total_amount == 0:
            return []

        # Get sum per category
        rows = conn.execute(
            "SELECT category, SUM(amount) as amount FROM expenses WHERE user_id = ? GROUP BY category ORDER BY amount DESC",
            (user_id,)
        ).fetchall()

        breakdown = []
        total_percentage = 0

        for row in rows:
            category = row['category']
            amount = row['amount']
            percentage = round((amount / total_amount) * 100)
            breakdown.append({
                "category": category,
                "amount": amount,
                "percentage": percentage
            })
            total_percentage += percentage

        # Rounding Correction: Ensure percentages sum to exactly 100%
        diff = 100 - total_percentage
        if diff != 0 and breakdown:
            # Add/subtract difference to the category with the largest amount
            # breakdown is already sorted by amount DESC
            breakdown[0]["percentage"] += diff

        return breakdown

def get_summary_stats(user_id):
    """
    Calculates total spent, total transaction count, and the top spending category for a user.
    Returns a dictionary: {"total_spent": float, "transaction_count": int, "top_category": str}
    """
    with get_db() as conn:
        # Query 1: Totals
        totals = conn.execute(
            "SELECT SUM(amount) as total_spent, COUNT(*) as transaction_count FROM expenses WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        total_spent = totals["total_spent"] if totals["total_spent"] is not None else 0.0
        transaction_count = totals["transaction_count"] if totals["transaction_count"] is not None else 0

        # Query 2: Top Category
        # Order by SUM(ABS(amount)) to handle potential negative values if they exist,
        # though usually expenses are positive.
        top_cat_row = conn.execute(
            "SELECT category FROM expenses WHERE user_id = ? GROUP BY category ORDER BY SUM(ABS(amount)) DESC LIMIT 1",
            (user_id,)
        ).fetchone()

        top_category = top_cat_row["category"] if top_cat_row else "—"

        return {
            "total_spent": float(total_spent),
            "transaction_count": int(transaction_count),
            "top_category": top_category
        }

def get_recent_transactions(user_id, limit=10):
    """
    Retrieves the most recent transactions for a given user.
    Returns a list of dictionaries containing date, description, category, and amount.
    """
    query = "SELECT date, description, category, amount FROM expenses WHERE user_id = ? ORDER BY date DESC LIMIT ?"

    with get_db() as conn:
        cursor = conn.execute(query, (user_id, limit))
        rows = cursor.fetchall()

        # Convert sqlite3.Row objects to dictionaries
        return [dict(row) for row in rows]
