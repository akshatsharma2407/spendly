---
# Spec: Add Expense

## Overview
This feature allows authenticated users to record new expenses. It is a core functional requirement of the Spendly app, moving the application from a read-only profile view to an interactive expense tracker. Users will be able to specify the amount, category, date, and an optional description for each expense.

## Depends on
- 03-login-and-logout: User must be authenticated.
- 05-profile-backend-routes: Database schema for expenses must exist.

## Routes
- `GET /expenses/add` — Render the add expense form — logged-in
- `POST /expenses/add` — Process the form submission and save the expense to the database — logged-in

## Database changes
No database changes. The `expenses` table already exists with columns: `user_id`, `amount`, `category`, `date`, `description`.

## Templates
- **Create:** `templates/add_expense.html` (Form for adding expenses)
- **Modify:** `templates/base.html` (Add a link to "Add Expense" in the navigation)

## Files to change
- `app.py`: Implement the GET and POST handlers for `/expenses/add`.

## Files to create
- `templates/add_expense.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Validate that `amount`, `category`, and `date` are provided before inserting into the database.
- Ensure the `user_id` is taken from the session.

## Definition of done
- [ ] Navigating to `/expenses/add` while logged in renders a form with fields for Amount, Category, Date, and Description.
- [ ] Submitting the form with valid data creates a new record in the `expenses` table associated with the current user.
- [ ] Submitting the form redirects the user back to the profile page.
- [ ] New expenses appear immediately in the "Recent Transactions" list on the profile page.
- [ ] Attempting to access `/expenses/add` while logged out redirects to the login page.
---
