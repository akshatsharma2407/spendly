# Spec: Edit Expense

## Overview
This feature allows logged-in users to modify the details of an existing expense. Users can correct mistakes in the amount, category, date, or description of a transaction they previously added, ensuring their financial tracking remains accurate.

## Depends on
- 07-add-expense (must be able to create expenses before editing them)

## Routes
- `GET /expenses/<int:id>/edit` — Display the edit form populated with the expense's current data — logged-in
- `POST /expenses/<int:id>/edit` — Process the updated expense data and save to database — logged-in

## Database changes
No database changes.

## Templates
- **Create:** `templates/edit_expense.html` (an edit form similar to `add_expense.html`)
- **Modify:** No existing templates need modification.

## Files to change
- `app.py` (implement the GET and POST logic for the edit routes)

## Files to create
- `templates/edit_expense.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Verify that the expense being edited belongs to the currently logged-in user before allowing access or updates.

## Definition of done
- Clicking "Edit" on a transaction in the profile page leads to the edit form.
- The edit form is pre-populated with the correct current data for that expense.
- Updating the expense and submitting the form successfully updates the record in the database.
- The user is redirected back to the profile page after a successful update.
- Attempting to edit an expense that doesn't exist or belongs to another user results in a 404 or error message.
- Validation prevents negative amounts or missing required fields (amount, category, date).
