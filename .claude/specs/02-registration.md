# Spec: Registration

## Overview
The Registration feature allows new users to create an account by providing their full name, email address, and a password. This is a fundamental part of the Spendly roadmap, enabling personalized expense tracking and secure user data management.

## Depends on
- 01-database-setup: Requires the `users` table to be initialized.

## Routes
- POST /register — Handles user account creation, validates input, hashes passwords, and stores user data — public

## Database changes
No database changes. The `users` table already contains the necessary columns (`name`, `email`, `password_hash`).

## Templates
- Modify: `templates/register.html` — Ensure the form handles error messages and is correctly linked to the POST route.

## Files to change
- `app.py` — Implement the POST handler for the `/register` route.

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend base.html

## Definition of done
- [ ] User can successfully register with a valid name, email, and password (min 8 chars).
- [ ] Registration fails if the email is already taken, with a clear error message displayed on the page.
- [ ] Registration fails if the password is shorter than 8 characters.
- [ ] New users are correctly inserted into the `users` table with hashed passwords.
- [ ] After successful registration, the user is redirected to the login page.
