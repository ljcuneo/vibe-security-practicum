# Task Manager

A simple multi-user task management web application built with Python, Flask,
and SQLite.

## Features

- User registration and login
- Each user can create, view, edit, and delete their own tasks (title,
  description, status)
- Users can only access their own tasks
- Simple administrator role with an admin page listing all registered users
- The **first account registered** automatically becomes the administrator;
  every subsequent registration is a regular user

## Requirements

- Python 3.9+ (tested with Python 3.12)
- macOS (should also run on Linux/Windows, but instructions below are for
  local macOS use)

## Setup

1. Clone or copy this project, then open a terminal in the project
   directory.

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Set a persistent secret key for signing sessions. If you skip
   this, the app will generate one automatically on first run and store it
   in `instance/secret_key` (not checked into version control):

   ```bash
   export SECRET_KEY="$(python3 -c 'import os; print(os.urandom(32).hex())')"
   ```

5. Run the application:

   ```bash
   python app.py
   ```

6. Open your browser to <http://127.0.0.1:5000>.

The SQLite database is created automatically at `instance/app.db` the first
time the app runs.

## Usage notes

- Register an account at `/register`. The very first account created becomes
  the admin and can view the registered-user list at `/admin/users`.
- Passwords must be at least 8 characters and contain at least one letter
  and one number.
- After 5 consecutive failed login attempts for an account, that account is
  temporarily locked for 15 minutes.

## Running over HTTPS

By default the session cookie is not marked `Secure`, since the app is
intended to run locally over plain HTTP. If you deploy this behind HTTPS,
set the `FORCE_HTTPS` environment variable before starting the app so the
session cookie is only sent over encrypted connections:

```bash
export FORCE_HTTPS=true
python app.py
```

## Project layout

```
app.py              Application code (routes, models, security config)
requirements.txt    Python dependencies
templates/           Jinja2 HTML templates
static/style.css     Stylesheet
instance/            Created at runtime: SQLite database and secret key (gitignored)
```
