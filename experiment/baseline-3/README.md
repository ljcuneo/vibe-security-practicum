# Task Manager

A simple task management web app built with Python, Flask, SQLite and plain HTML/CSS.

## Features

- User registration, login and logout
- Multiple user accounts; each user can only see and manage their own tasks
- Create, view, edit and delete tasks (title, description, status)
- Administrator role with an admin page listing registered users
- Data stored in a local SQLite database (`tasks.db`)

## Requirements

- macOS with Python 3.9 or newer (`python3 --version` to check)

## Setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
```

## Running the app

```bash
python3 app.py
```

Then open <http://127.0.0.1:5001> in your browser.

(Port 5001 is used because macOS's AirPlay Receiver often occupies port 5000.
To use another port: `PORT=8000 python3 app.py`.)

The SQLite database file `tasks.db` is created automatically in the project
directory the first time the app starts.

## Administrator account

- **The first account registered becomes the administrator.**
- To promote another existing user to administrator:

  ```bash
  flask --app app make-admin <username>
  ```

Administrators see an **Admin** link in the navigation bar, which shows the list
of registered users.

## Configuration (optional)

| Environment variable | Purpose                                        | Default             |
|----------------------|------------------------------------------------|---------------------|
| `SECRET_KEY`         | Key used to sign session cookies               | random on each start |
| `DATABASE`           | Path to the SQLite database file               | `./tasks.db`        |
| `PORT`               | Port the development server listens on         | `5001`              |
| `FLASK_DEBUG`        | Set to `1` to enable Flask debug mode          | off                 |

If `SECRET_KEY` is not set, a random key is generated at startup, which means
everyone is logged out whenever the server restarts. Set a fixed value to keep
sessions across restarts:

```bash
export SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
python3 app.py
```

## Resetting the data

Stop the server and delete `tasks.db`. A fresh database is created on the next start.
