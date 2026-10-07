import os
import re
import secrets
import sqlite3
import time
from datetime import timedelta
from functools import wraps

import click
from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
DATABASE = os.path.join(INSTANCE_DIR, "tasks.db")
SECRET_KEY_FILE = os.path.join(INSTANCE_DIR, "secret_key")

USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,32}$")
PASSWORD_MIN_LENGTH = 10
PASSWORD_MAX_LENGTH = 128
TITLE_MAX_LENGTH = 200
DESCRIPTION_MAX_LENGTH = 5000
TASK_STATUSES = ("todo", "in_progress", "done")
STATUS_LABELS = {"todo": "To do", "in_progress": "In progress", "done": "Done"}

# Login throttling: failed attempts allowed within the window before lockout.
LOGIN_WINDOW_SECONDS = 15 * 60
MAX_FAILURES_PER_USERNAME = 5
MAX_FAILURES_PER_IP = 20

# Verified against when the username is unknown, so response time does not
# reveal whether an account exists.
DUMMY_PASSWORD_HASH = generate_password_hash(secrets.token_urlsafe(32))


def load_secret_key():
    """Read the session signing key from the environment, or generate one
    on first run and keep it in the (git-ignored) instance directory."""
    key = os.environ.get("SECRET_KEY")
    if key:
        return key
    os.makedirs(INSTANCE_DIR, mode=0o700, exist_ok=True)
    try:
        with open(SECRET_KEY_FILE, "r", encoding="utf-8") as f:
            key = f.read().strip()
        if key:
            return key
    except FileNotFoundError:
        pass
    key = secrets.token_hex(32)
    fd = os.open(SECRET_KEY_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(key)
    return key


def env_flag(name):
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


app = Flask(__name__)
app.config.update(
    SECRET_KEY=load_secret_key(),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    # Set SESSION_COOKIE_SECURE=1 when the app is served over HTTPS.
    SESSION_COOKIE_SECURE=env_flag("SESSION_COOKIE_SECURE"),
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    MAX_CONTENT_LENGTH=64 * 1024,
)
csrf = CSRFProtect(app)


# --- Database ---------------------------------------------------------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    os.makedirs(INSTANCE_DIR, mode=0o700, exist_ok=True)
    db = sqlite3.connect(DATABASE)
    with open(os.path.join(BASE_DIR, "schema.sql"), "r", encoding="utf-8") as f:
        db.executescript(f.read())
    db.commit()
    db.close()


# --- Authentication helpers -------------------------------------------------

@app.before_request
def load_current_user():
    g.user = None
    user_id = session.get("user_id")
    if user_id is not None:
        g.user = get_db().execute(
            "SELECT id, username, is_admin FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if g.user is None:
            session.clear()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not g.user["is_admin"]:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


def validate_username(username):
    if not USERNAME_RE.fullmatch(username):
        return "Username must be 3-32 characters: letters, digits, or underscores."
    return None


def validate_password(password, username):
    if len(password) < PASSWORD_MIN_LENGTH:
        return f"Password must be at least {PASSWORD_MIN_LENGTH} characters long."
    if len(password) > PASSWORD_MAX_LENGTH:
        return f"Password must be at most {PASSWORD_MAX_LENGTH} characters long."
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return "Password must contain at least one letter and one digit."
    if username and username.lower() in password.lower():
        return "Password must not contain the username."
    return None


def create_user(username, password, is_admin=False):
    """Insert a user. Returns False if the username is already taken."""
    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), 1 if is_admin else 0),
        )
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        return False
    return True


# --- Login throttling -------------------------------------------------------

def client_ip():
    return request.remote_addr or "unknown"


def login_is_throttled(username):
    cutoff = time.time() - LOGIN_WINDOW_SECONDS
    db = get_db()
    by_username = db.execute(
        "SELECT COUNT(*) FROM login_failures WHERE username = ? AND attempted_at > ?",
        (username.lower(), cutoff),
    ).fetchone()[0]
    by_ip = db.execute(
        "SELECT COUNT(*) FROM login_failures WHERE ip = ? AND attempted_at > ?",
        (client_ip(), cutoff),
    ).fetchone()[0]
    return by_username >= MAX_FAILURES_PER_USERNAME or by_ip >= MAX_FAILURES_PER_IP


def record_login_failure(username):
    db = get_db()
    now = time.time()
    db.execute(
        "DELETE FROM login_failures WHERE attempted_at <= ?",
        (now - LOGIN_WINDOW_SECONDS,),
    )
    db.execute(
        "INSERT INTO login_failures (username, ip, attempted_at) VALUES (?, ?, ?)",
        (username.lower()[:64], client_ip(), now),
    )
    db.commit()


# --- Security headers -------------------------------------------------------

@app.after_request
def set_security_headers(response):
    response.headers["Content-Security-Policy"] = (
        "default-src 'none'; style-src 'self'; img-src 'self'; "
        "form-action 'self'; base-uri 'none'; frame-ancestors 'none'"
    )
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "same-origin"
    if request.endpoint != "static":
        response.headers["Cache-Control"] = "no-store"
    return response


@app.context_processor
def inject_template_globals():
    return {"STATUS_LABELS": STATUS_LABELS, "TASK_STATUSES": TASK_STATUSES}


# --- Auth routes ------------------------------------------------------------

@app.route("/register", methods=("GET", "POST"))
def register():
    if g.user is not None:
        return redirect(url_for("task_list"))
    username = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        error = validate_username(username) or validate_password(password, username)
        if error is None and password != confirm:
            error = "Passwords do not match."
        if error is None and not create_user(username, password):
            error = "That username is not available."

        if error is None:
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))
        flash(error, "error")
    return render_template("register.html", username=username)


@app.route("/login", methods=("GET", "POST"))
def login():
    if g.user is not None:
        return redirect(url_for("task_list"))
    username = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()[:64]
        password = request.form.get("password", "")[:PASSWORD_MAX_LENGTH]

        if login_is_throttled(username):
            flash("Too many failed login attempts. Please try again later.", "error")
            return render_template("login.html", username=username), 429

        user = get_db().execute(
            "SELECT id, password_hash FROM users WHERE username = ?", (username,)
        ).fetchone()
        password_ok = check_password_hash(
            user["password_hash"] if user else DUMMY_PASSWORD_HASH, password
        )
        if user is not None and password_ok:
            db = get_db()
            db.execute(
                "DELETE FROM login_failures WHERE username = ?", (username.lower(),)
            )
            db.commit()
            # Start from a fresh session to prevent session fixation.
            session.clear()
            session["user_id"] = user["id"]
            session.permanent = True
            return redirect(url_for("task_list"))

        record_login_failure(username)
        flash("Invalid username or password.", "error")
    return render_template("login.html", username=username)


@app.route("/logout", methods=("POST",))
def logout():
    session.clear()
    return redirect(url_for("login"))


# --- Task routes ------------------------------------------------------------

def get_own_task_or_404(task_id):
    """Fetch a task only if it belongs to the current user."""
    task = get_db().execute(
        "SELECT id, title, description, status FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, g.user["id"]),
    ).fetchone()
    if task is None:
        abort(404)
    return task


def read_task_form():
    """Return (form values, error message or None) from the submitted form."""
    values = {
        "title": request.form.get("title", "").strip(),
        "description": request.form.get("description", "").strip(),
        "status": request.form.get("status", ""),
    }
    error = None
    if not values["title"]:
        error = "Title is required."
    elif len(values["title"]) > TITLE_MAX_LENGTH:
        error = f"Title must be at most {TITLE_MAX_LENGTH} characters."
    elif len(values["description"]) > DESCRIPTION_MAX_LENGTH:
        error = f"Description must be at most {DESCRIPTION_MAX_LENGTH} characters."
    elif values["status"] not in TASK_STATUSES:
        error = "Invalid status."
    return values, error


@app.route("/")
@login_required
def task_list():
    tasks = get_db().execute(
        "SELECT id, title, description, status FROM tasks "
        "WHERE user_id = ? ORDER BY id DESC",
        (g.user["id"],),
    ).fetchall()
    return render_template("tasks.html", tasks=tasks)


@app.route("/tasks/new", methods=("GET", "POST"))
@login_required
def task_create():
    task = {"title": "", "description": "", "status": TASK_STATUSES[0]}
    if request.method == "POST":
        task, error = read_task_form()
        if error is None:
            db = get_db()
            db.execute(
                "INSERT INTO tasks (user_id, title, description, status) "
                "VALUES (?, ?, ?, ?)",
                (g.user["id"], task["title"], task["description"], task["status"]),
            )
            db.commit()
            flash("Task created.", "success")
            return redirect(url_for("task_list"))
        flash(error, "error")
    return render_template(
        "task_form.html", task=task, heading="New task", action=url_for("task_create")
    )


@app.route("/tasks/<int:task_id>/edit", methods=("GET", "POST"))
@login_required
def task_edit(task_id):
    task = get_own_task_or_404(task_id)
    if request.method == "POST":
        task, error = read_task_form()
        if error is None:
            db = get_db()
            db.execute(
                "UPDATE tasks SET title = ?, description = ?, status = ? "
                "WHERE id = ? AND user_id = ?",
                (
                    task["title"],
                    task["description"],
                    task["status"],
                    task_id,
                    g.user["id"],
                ),
            )
            db.commit()
            flash("Task updated.", "success")
            return redirect(url_for("task_list"))
        flash(error, "error")
    return render_template(
        "task_form.html",
        task=task,
        heading="Edit task",
        action=url_for("task_edit", task_id=task_id),
    )


@app.route("/tasks/<int:task_id>/delete", methods=("POST",))
@login_required
def task_delete(task_id):
    get_own_task_or_404(task_id)
    db = get_db()
    db.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, g.user["id"])
    )
    db.commit()
    flash("Task deleted.", "success")
    return redirect(url_for("task_list"))


# --- Admin routes -----------------------------------------------------------

@app.route("/admin/users")
@admin_required
def admin_users():
    users = get_db().execute(
        "SELECT id, username, is_admin, created_at FROM users ORDER BY id"
    ).fetchall()
    return render_template("admin_users.html", users=users)


# --- Error handlers ---------------------------------------------------------

@app.errorhandler(400)
def bad_request(e):
    return render_template("error.html", code=400, message="Bad request."), 400


@app.errorhandler(403)
def forbidden(e):
    return render_template("error.html", code=403, message="Access denied."), 403


@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="Page not found."), 404


@app.errorhandler(413)
def too_large(e):
    return render_template("error.html", code=413, message="Request too large."), 413


# --- CLI --------------------------------------------------------------------

@app.cli.command("create-admin")
@click.option("--username", prompt=True)
@click.password_option()
def create_admin_command(username, password):
    """Create an administrator account."""
    username = username.strip()
    error = validate_username(username) or validate_password(password, username)
    if error:
        raise click.ClickException(error)
    if not create_user(username, password, is_admin=True):
        raise click.ClickException("That username is not available.")
    click.echo(f"Administrator '{username}' created.")


init_db()

if __name__ == "__main__":
    # Local development server; debug mode is intentionally off.
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5001")), debug=False)
