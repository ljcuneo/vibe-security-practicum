# Task Manager

A simple multi-user task manager built with Python, Flask, SQLite and plain
HTML/CSS. Users register, log in, and create, view, edit and delete their own
tasks (title, description, status). Administrators can view a list of all
registered users.

## Requirements

- macOS with Python 3.9 or newer (`python3 --version`)

## Install

```bash
cd security-aware-3
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Open <http://127.0.0.1:5001> in your browser. (Port 5001 is used by default
because macOS's AirPlay Receiver often occupies port 5000. Set `PORT` to use a
different port.)

The SQLite database is created automatically at `instance/tasks.db` on first
run.

## Create an administrator

Administrator accounts are created from the command line (there is no way to
become an administrator through the web interface):

```bash
flask --app app create-admin alice
```

You will be prompted for a password. If the user `alice` already exists, the
account is promoted to administrator instead. Administrators see an **Admin**
link in the navigation bar that lists all registered users.

## Configuration

All settings are optional and read from environment variables:

| Variable                | Default              | Purpose                                                                 |
|-------------------------|----------------------|-------------------------------------------------------------------------|
| `SECRET_KEY`            | auto-generated       | Key used to sign session cookies. If unset, a random key is generated on first run and stored in `instance/secret_key` (mode 0600). |
| `DATABASE_PATH`         | `instance/tasks.db`  | Location of the SQLite database.                                        |
| `SESSION_COOKIE_SECURE` | `false`              | Set to `true` when serving over HTTPS so cookies are only sent over TLS (also enables HSTS). |
| `PORT`                  | `5001`               | Port used by `python app.py`.                                           |

The `instance/` directory holds the database and secret key and is excluded
from version control.

## Security notes

- Passwords are hashed with scrypt (Werkzeug). Passwords must be 12–128
  characters, include a letter and a digit, and must not contain the username.
- Failed logins are throttled: 5 failures per username or 20 per IP address
  within 15 minutes temporarily block further attempts.
- All forms, including logout and delete, are POST requests protected by CSRF
  tokens (Flask-WTF).
- Users can only access their own tasks; requests for another user's task return
  404. The admin page returns 403 for non-administrators.
- All SQL uses parameterized queries; templates are auto-escaped by Jinja2.
- Session cookies are `HttpOnly` with `SameSite=Lax` (and `Secure` when
  `SESSION_COOKIE_SECURE=true`). The session is reset on login.
- Responses include a strict Content-Security-Policy (with
  `frame-ancestors 'none'`), `X-Content-Type-Options: nosniff`,
  `X-Frame-Options: DENY` and `Referrer-Policy` headers.
- The built-in server is for local use only. For any deployment, run behind a
  production WSGI server and HTTPS.
