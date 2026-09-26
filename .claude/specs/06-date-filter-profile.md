---
# Spec: Date Filter for Profile Page

## Overview
This feature introduces date filtering to the user's profile page. Currently, the profile page shows summary statistics and transactions without any time-based constraints. This feature will allow users to filter their spending data by a specific date range (Start Date and End Date), enabling them to analyze their expenses for a particular month, week, or custom period.

## Depends on
- 05-profile-backend-routes

## Routes
- `GET /profile` — Modified to accept optional `start_date` and `end_date` query parameters. It will filter the statistics and transactions based on these dates. — logged-in

## Database changes
No database changes. Filtering will be handled via `WHERE` clauses in the existing queries in `database/queries.py` (using the `date` column in the `expenses` table).

## Templates
- **Modify:** `templates/profile.html` — Add a date filter form (containing two date inputs and a submit button) at the top of the profile page. Ensure the form uses `GET` to pass parameters to the `/profile` route.

## Files to change
- `app.py` — Update the `profile` route to extract `start_date` and `end_date` from `request.args` and pass them to the query helpers.
- `database/queries.py` — Update `get_summary_stats`, `get_recent_transactions`, and `get_category_breakdown` to accept optional date range parameters and apply them to the SQL queries.
- `templates/profile.html` — Add the date filter UI.

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Handle missing or invalid date formats gracefully (default to all-time if not provided).

## Definition of done
- [ ] A date filter form is visible on the `/profile` page.
- [ ] Selecting a date range and submitting the form updates the summary stats to reflect only expenses within that range.
- [ ] The transaction list only shows expenses between the selected start and end dates.
- [ ] The category breakdown chart/list updates based on the filtered date range.
- [ ] Clearing the dates or submitting an empty filter returns the view to "all-time" data.
---
