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

def get_category_breakdown(user_id, start_date=None, end_date=None):

    """
    Calculates the spend breakdown by category for a given user.
    Returns a list of dictionaries with category, amount, and percentage,
    ordered by amount descending.
    """
    with get_db() as conn:
        # Build dynamic WHERE clause
        where_clause = "WHERE user_id = ?"
        params = [user_id]

        if start_date:
            where_clause += " AND date >= ?"
            params.append(start_date)
        if end_date:
            where_clause += " AND date <= ?"
            params.append(end_date)

        # Get total spend first for percentage calculations
        total_row = conn.execute(
            f"SELECT SUM(amount) as total FROM expenses {where_clause}",
            tuple(params)
        ).fetchone()

        total_amount = total_row['total'] if total_row and total_row['total'] else 0

        if total_amount == 0:
            return []

        # Get sum per category
        rows = conn.execute(
            f"SELECT category, SUM(amount) as amount FROM expenses {where_clause} GROUP BY category ORDER BY amount DESC",
            tuple(params)
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

def get_summary_stats(user_id, start_date=None, end_date=None):
    """
    Calculates total spent, total transaction count, and the top spending category for a user.
    Returns a dictionary: {"total_spent": float, "transaction_count": int, "top_category": str}
    """
    with get_db() as conn:
        # Build dynamic WHERE clause
        where_clause = "WHERE user_id = ?"
        params = [user_id]

        if start_date:
            where_clause += " AND date >= ?"
            params.append(start_date)
        if end_date:
            where_clause += " AND date <= ?"
            params.append(end_date)

        # Query 1: Totals
        totals = conn.execute(
            f"SELECT SUM(amount) as total_spent, COUNT(*) as transaction_count FROM expenses {where_clause}",
            tuple(params)
        ).fetchone()

        total_spent = totals["total_spent"] if totals["total_spent"] is not None else 0.0
        transaction_count = totals["transaction_count"] if totals["transaction_count"] is not None else 0

        # Query 2: Top Category
        top_cat_row = conn.execute(
            f"SELECT category FROM expenses {where_clause} GROUP BY category ORDER BY SUM(ABS(amount)) DESC LIMIT 1",
            tuple(params)
        ).fetchone()

        top_category = top_cat_row["category"] if top_cat_row else "—"

        return {
            "total_spent": float(total_spent),
            "transaction_count": int(transaction_count),
            "top_category": top_category
        }

def get_recent_transactions(user_id, limit=10, start_date=None, end_date=None):
    """
    Retrieves the most recent transactions for a given user.
    Returns a list of dictionaries containing date, description, category, and amount.
    """
    where_clause = "WHERE user_id = ?"
    params = [user_id]

    if start_date:
        where_clause += " AND date >= ?"
        params.append(start_date)
    if end_date:
        where_clause += " AND date <= ?"
        params.append(end_date)

    query = f"SELECT date, description, category, amount FROM expenses {where_clause} ORDER BY date DESC LIMIT ?"
    params.append(limit)

    with get_db() as conn:
        cursor = conn.execute(query, tuple(params))
        rows = cursor.fetchall()

        # Convert sqlite3.Row objects to dictionaries
        return [dict(row) for row in rows]
