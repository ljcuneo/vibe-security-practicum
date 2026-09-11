# Task Manager Prototype

A minimal Flask + SQLite task management app, built as a disposable prototype
for security research. Plain HTML/CSS, no frontend framework, no build step.

## Features

- User registration, login, logout (multi-user)
- Persistent SQLite database (`app.db`, created automatically)
- Each user can create, view, edit, and delete their own tasks
  (title, description, status)
- Users can only see/modify their own tasks
- Simple admin role: **the first account registered becomes the admin**
- Admin-only page listing all registered users (`/admin/users`)

## Requirements

- macOS with Python 3.9+ (check with `python3 --version`)

## Setup

```bash
cd /Users/luciano/vibe-security-practicum/prototype

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Run

```bash
python3 app.py
```

The app will:
- Create `app.db` in this directory on first run (if it doesn't already exist)
- Start a local dev server at http://127.0.0.1:5000

Open http://127.0.0.1:5000 in your browser.

1. Register the first account — it automatically becomes the admin.
2. Register additional accounts from a different browser/incognito window
   (or after logging out) to test multi-user behavior.
3. Log in as the admin and visit http://127.0.0.1:5000/admin/users to see
   all registered users.

## Stopping / resetting

- Stop the server with `Ctrl+C`.
- To reset all data, stop the server and delete `app.db`, then restart —
  it will be recreated empty (and the next registered user becomes admin
  again).

## Notes

This is intentionally minimal and meant to run locally only:

- Flask's built-in dev server (`debug=True`) is used — not for production use.
- `SECRET_KEY` defaults to a hardcoded dev value; set the `SECRET_KEY`
  environment variable to override it if needed.
- No rate limiting, email verification, or password reset flow — out of
  scope for this prototype.
