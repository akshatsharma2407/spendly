# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

- **Run App**: `python app.py` (runs on port 5001 by default)
- **Install Dependencies**: `pip install -r requirements.txt`

## Architecture

The project is a Flask-based web application for expense tracking.

### High-Level Structure
- `app.py`: Main application entry point. Contains all route definitions and Flask configuration.
- `database/`: Database layer.
    - `db.py`: Intended for SQLite connection management (`get_db`), database initialization (`init_db`), and seeding (`seed_db`).
- `templates/`: Jinja2 HTML templates.
    - `base.html`: The primary layout file used by all other pages via template inheritance.
    - `landing.html`: The landing page with a redesigned hero section and video demonstration modal.
    - `login.html`, `register.html`, `terms.html`, `privacy.html`: Standard application pages.
- `static/`: Static assets.
    - `css/style.css`: Main stylesheet containing global variables, responsive design, and component styles.
    - `js/main.js`: Frontend logic, including the video modal interaction.

### Design Patterns
- **Templating**: Uses Jinja2 blocks (`{% block content %}`) for content injection into a base layout.
- **Frontend**: Vanilla CSS and JavaScript. The UI uses a modern, clean aesthetic with a focus on fluid typography (`clamp()`) and a mobile-first responsive approach.
- **Database**: Planned SQLite implementation with a dedicated helper module in `database/`.

## Interaction Rules
- When bash commands (prefixed with `!`) are executed, do not generate explanatory commentary or follow-up suggestions unless an explicit error code occurs.
- Never enter plan mode automatically; execute direct steps unless `/plan` is explicitly called.