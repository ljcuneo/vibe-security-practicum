# Task Manager

A simple multi-user task management web application built with Flask, SQLite, and
server-rendered HTML/CSS (no frontend framework).

## Features

- User registration, login, and logout
- Each user can create, view, edit, and delete their own tasks
- Tasks have a title, description, and status (To Do / In Progress / Done)
- Administrator role: the first user to register becomes an administrator and can
  view the list of registered users at `/admin/users`

## Requirements

- Python 3.9+ (macOS ships with a compatible version, or install via `brew install python`)

## Installation

```bash
cd experiment/baseline-2

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running the application

```bash
python app.py
```

The app starts on `http://127.0.0.1:5000`. On first run it automatically creates a
SQLite database at `instance/tasks.db` using the schema in `schema.sql`.

Open `http://127.0.0.1:5000` in your browser, register a user, and start managing tasks.
The **first account you register becomes the administrator** and can view the
registered-users list from the "Users (admin)" link in the navigation bar.

## Resetting the database

To wipe all data and start fresh, delete the database file and restart the app:

```bash
rm instance/tasks.db
python app.py
```

## Notes

- Set the `SECRET_KEY` environment variable to a random value before running in any
  shared or persistent environment (a development default is used otherwise):
  ```bash
  export SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
  ```
- This project is intended for local/educational use and keeps the implementation
  intentionally minimal.
