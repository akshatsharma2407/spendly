# Spec: Login and Logout

## Overview
The Login and Logout feature enables users to securely access their accounts and end their sessions. This ensures that expense data is private and associated with the correct user, moving the application from a static prototype to a functional authenticated system.

## Depends on
- 01-database-setup: Requires the `users` table.
- 02-registration: Requires the ability for users to create accounts.

## Routes
- `POST /login` — Validates user credentials, establishes a session, flashes a success message, and redirects to the landing page — public
- `GET /logout` — Terminates the user session and redirects to the landing page — logged-in

## Database changes
No database changes.

## Templates
- **Create:** No new templates.
- **Modify:** 
    - `templates/login.html` — Ensure the form submits via POST to `/login` and handles error messages.
    - `templates/base.html` — Implement dynamic navbar links (Sign in/Register vs Profile/Sign out) and a flash message container for notifications.

## Files to change
- `app.py` — Implement logic for `/login` and `/logout` routes, session management, `SECRET_KEY` configuration, and a `@login_required` decorator for route protection.
- `static/css/style.css` — Add styles for the flash message popups/toasts.

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`

## Definition of done
- [ ] User can log in with a valid email and password.
- [ ] Upon successful login, user is redirected to the landing page and sees a "Successfully logged in!" popup.
- [ ] Login fails with an invalid password or non-existent email, displaying a clear error message.
- [ ] Navbar updates to show "Profile" and "Sign out" when the user is authenticated.
- [ ] User can log out, which destroys the session and redirects to the landing page.
- [ ] Accessing protected routes (e.g., `/profile`) while logged out redirects the user to the login page.
