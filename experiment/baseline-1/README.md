# Task Manager

A simple multi-user task management web app built with Python, Flask, and SQLite.

## Features

- User registration, login, and logout
- Multiple user accounts, each with their own private list of tasks
- Create, view, edit, and delete tasks (title, description, status)
- Simple administrator role
- Admin page listing all registered users

The **first account you register becomes an administrator automatically**.
All accounts registered after that are regular users.

## Requirements

- macOS with Python 3.9 or later installed (check with `python3 --version`)

## Installation

Open Terminal, navigate to the project directory, and run:

```bash
cd /path/to/baseline-1

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running the app

With the virtual environment activated:

```bash
python app.py
```

The database file (`tasks.db`) is created automatically on first run in the
project directory.

The app will start on http://127.0.0.1:5000/. Open that address in your
browser.

To stop the server, press `Ctrl+C` in the terminal.

## Usage

1. Go to **Register** and create an account. The first account created is
   automatically given administrator privileges.
2. Log in and use **My Tasks** to create, edit, and delete your tasks.
3. If logged in as an administrator, use the **Admin: Users** link in the
   navigation bar to view all registered users.
4. Each user can only see and manage their own tasks.

## Notes

- This app is intended for local, single-machine use (e.g. `localhost`).
  It is not configured for production deployment.
- The database is a single SQLite file (`tasks.db`) stored in the project
  directory. Delete this file to reset the app to a clean state.
- Set the `SECRET_KEY` environment variable to a random value if you want a
  non-default Flask session secret:

  ```bash
  export SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
  ```
