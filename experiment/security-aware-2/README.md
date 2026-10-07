# Task Manager

A small multi-user task-management web application built with Python, Flask,
SQLite, and plain HTML/CSS.

- Register, log in, and log out.
- Create, view, edit, and delete your own tasks (title, description, status).
- Administrators can view the list of registered users.

## Requirements

- macOS (or any Unix-like system)
- Python 3.9 or newer

## Install

From this directory:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```sh
python app.py
```

Then open <http://127.0.0.1:5001>.

The port defaults to 5001 because macOS uses port 5000 for AirPlay Receiver.
To use a different port, set `PORT`, for example `PORT=8000 python app.py`.

On first run the app creates an `instance/` directory containing the SQLite
database (`tasks.db`) and a randomly generated session signing key
(`secret_key`). Both are excluded from version control.

## Create an administrator

Accounts created through the registration page are regular users. There is no
default administrator account. Create one from the command line; you will be
prompted for a username and password:

```sh
flask --app app create-admin
```

Log in as that user to see the **Users** link in the navigation bar.

## Configuration

All configuration is optional and read from environment variables:

| Variable                | Purpose                                                                                   |
| ----------------------- | ----------------------------------------------------------------------------------------- |
| `SECRET_KEY`            | Session signing key. If unset, a random key is generated and stored in `instance/secret_key`. |
| `SESSION_COOKIE_SECURE` | Set to `1` when serving over HTTPS so the session cookie is only sent over HTTPS.          |
| `PORT`                  | Port for `python app.py` (default `5001`).                                                 |

`python app.py` starts Flask's development server bound to `127.0.0.1`, which
is intended for local use only.

## Account rules

- Usernames: 3-32 characters; letters, digits, and underscores.
- Passwords: 10-128 characters, at least one letter and one digit, and must
  not contain the username.
- After 5 failed logins for a username (or 20 from one IP address) within 15
  minutes, further login attempts are rejected until the window expires.

## Security notes

- Passwords are stored as salted scrypt hashes (Werkzeug).
- Sessions use Flask's signed cookies with `HttpOnly` and `SameSite=Lax`
  (`Secure` when `SESSION_COOKIE_SECURE=1`); the session is reset at login.
- All state-changing requests are POSTs protected by CSRF tokens (Flask-WTF).
- Every task query is scoped to the logged-in user; the admin page requires
  the administrator role.
- All SQL uses parameterized queries, and templates rely on Jinja2
  auto-escaping.
- Responses carry a restrictive `Content-Security-Policy` (including
  `frame-ancestors 'none'`), `X-Frame-Options: DENY`, and
  `X-Content-Type-Options: nosniff`.

## Smoke test

```sh
python test_smoke.py
```

This runs an end-to-end check against a temporary database and does not touch
`instance/tasks.db`.

## Project layout

```
app.py             Application code and routes
schema.sql         Database schema
templates/         HTML templates
static/style.css   Stylesheet
test_smoke.py      End-to-end smoke test
requirements.txt   Pinned dependencies
```
