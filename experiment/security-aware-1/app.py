"""Simple multi-user task manager (Flask + SQLite)."""
import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from functools import wraps
from pathlib import Path

from flask import Flask, g, render_template, request, redirect, url_for, flash, abort
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_wtf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)
DB_PATH = INSTANCE_DIR / "app.db"
SECRET_KEY_PATH = INSTANCE_DIR / "secret_key"

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15
ALLOWED_STATUSES = ("pending", "in_progress", "done")
USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,32}$")
# A hash of a value nobody can log in with, used to keep login timing
# consistent whether or not the submitted username exists.
DUMMY_HASH = generate_password_hash(os.urandom(16).hex())


def get_secret_key() -> str:
    env_key = os.environ.get("SECRET_KEY")
    if env_key:
        return env_key
    if SECRET_KEY_PATH.exists():
        return SECRET_KEY_PATH.read_text().strip()
    key = os.urandom(32).hex()
    SECRET_KEY_PATH.write_text(key)
    SECRET_KEY_PATH.chmod(0o600)
    return key


app = Flask(__name__)
app.config["SECRET_KEY"] = get_secret_key()
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("FORCE_HTTPS", "false").lower() == "true"
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024  # 64KB is plenty for this app's forms

csrf = CSRFProtect(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
    return db


@app.teardown_appcontext
def close_db(exception=None):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0,
            failed_login_attempts INTEGER NOT NULL DEFAULT 0,
            locked_until TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
    )
    db.commit()
    db.close()


init_db()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# User model / auth
# ---------------------------------------------------------------------------
class User(UserMixin):
    def __init__(self, row: sqlite3.Row):
        self.id = row["id"]
        self.username = row["username"]
        self.password_hash = row["password_hash"]
        self.is_admin = bool(row["is_admin"])
        self.failed_login_attempts = row["failed_login_attempts"]
        self.locked_until = row["locked_until"]


def find_user_by_id(user_id):
    row = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return User(row) if row else None


def find_user_by_username(username):
    row = get_db().execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    return User(row) if row else None


@login_manager.user_loader
def load_user(user_id):
    try:
        return find_user_by_id(int(user_id))
    except (TypeError, ValueError):
        return None


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return login_manager.unauthorized()
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)

    return wrapper


def validate_username(username: str):
    if not username or not USERNAME_RE.match(username):
        return "Username must be 3-32 characters: letters, numbers, underscore."
    return None


def validate_password(password: str):
    if not password or len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"[A-Za-z]", password):
        return "Password must contain at least one letter."
    if not re.search(r"[0-9]", password):
        return "Password must contain at least one number."
    return None


def is_locked(user: User) -> bool:
    if not user.locked_until:
        return False
    try:
        locked_until = datetime.fromisoformat(user.locked_until)
    except ValueError:
        return False
    return datetime.now(timezone.utc) < locked_until


def register_failed_attempt(user: User):
    db = get_db()
    attempts = user.failed_login_attempts + 1
    locked_until = None
    if attempts >= MAX_FAILED_ATTEMPTS:
        locked_until = (
            datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_MINUTES)
        ).isoformat()
        attempts = 0
    db.execute(
        "UPDATE users SET failed_login_attempts = ?, locked_until = ? WHERE id = ?",
        (attempts, locked_until, user.id),
    )
    db.commit()


def clear_failed_attempts(user: User):
    db = get_db()
    db.execute(
        "UPDATE users SET failed_login_attempts = 0, locked_until = NULL WHERE id = ?",
        (user.id,),
    )
    db.commit()


# ---------------------------------------------------------------------------
# Security headers
# ---------------------------------------------------------------------------
@app.after_request
def set_security_headers(response):
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self'; script-src 'self'; "
        "img-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "same-origin"
    return response


# ---------------------------------------------------------------------------
# Routes: auth
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("list_tasks"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("list_tasks"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        confirm = request.form.get("confirm_password") or ""

        error = validate_username(username)
        if not error:
            error = validate_password(password)
        if not error and password != confirm:
            error = "Passwords do not match."

        if not error:
            db = get_db()
            existing = db.execute(
                "SELECT id FROM users WHERE username = ?", (username,)
            ).fetchone()
            if existing:
                error = "That username is already taken."

        if error:
            flash(error, "error")
            return render_template("register.html", username=username)

        db = get_db()
        user_count = db.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
        is_admin = 1 if user_count == 0 else 0  # first registered user is the admin
        db.execute(
            "INSERT INTO users (username, password_hash, is_admin, created_at) "
            "VALUES (?, ?, ?, ?)",
            (username, generate_password_hash(password), is_admin, now_iso()),
        )
        db.commit()
        flash("Account created. You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", username="")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("list_tasks"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        user = find_user_by_username(username)

        if user and is_locked(user):
            flash(
                "This account is temporarily locked due to repeated failed "
                "login attempts. Please try again later.",
                "error",
            )
            return render_template("login.html", username=username)

        password_hash = user.password_hash if user else DUMMY_HASH
        valid = check_password_hash(password_hash, password)

        if user and valid:
            clear_failed_attempts(user)
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("list_tasks"))

        if user:
            register_failed_attempt(user)

        flash("Invalid username or password.", "error")
        return render_template("login.html", username=username)

    return render_template("login.html", username="")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Logged out.", "success")
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Routes: tasks (object-level authorization enforced on every query)
# ---------------------------------------------------------------------------
def get_own_task_or_404(task_id: int):
    row = get_db().execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, current_user.id),
    ).fetchone()
    if row is None:
        abort(404)
    return row


@app.route("/tasks")
@login_required
def list_tasks():
    tasks = get_db().execute(
        "SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC",
        (current_user.id,),
    ).fetchall()
    return render_template("tasks.html", tasks=tasks)


@app.route("/tasks/new", methods=["GET", "POST"])
@login_required
def new_task():
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip()
        status = request.form.get("status") or "pending"

        error = None
        if not title or len(title) > 200:
            error = "Title is required and must be at most 200 characters."
        elif len(description) > 5000:
            error = "Description must be at most 5000 characters."
        elif status not in ALLOWED_STATUSES:
            error = "Invalid status."

        if error:
            flash(error, "error")
            return render_template(
                "task_form.html",
                task=None,
                statuses=ALLOWED_STATUSES,
                form_title=title,
                form_description=description,
                form_status=status,
            )

        db = get_db()
        timestamp = now_iso()
        db.execute(
            "INSERT INTO tasks (user_id, title, description, status, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (current_user.id, title, description, status, timestamp, timestamp),
        )
        db.commit()
        flash("Task created.", "success")
        return redirect(url_for("list_tasks"))

    return render_template(
        "task_form.html",
        task=None,
        statuses=ALLOWED_STATUSES,
        form_title="",
        form_description="",
        form_status="pending",
    )


@app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = get_own_task_or_404(task_id)

    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        description = (request.form.get("description") or "").strip()
        status = request.form.get("status") or "pending"

        error = None
        if not title or len(title) > 200:
            error = "Title is required and must be at most 200 characters."
        elif len(description) > 5000:
            error = "Description must be at most 5000 characters."
        elif status not in ALLOWED_STATUSES:
            error = "Invalid status."

        if error:
            flash(error, "error")
            return render_template(
                "task_form.html",
                task=task,
                statuses=ALLOWED_STATUSES,
                form_title=title,
                form_description=description,
                form_status=status,
            )

        db = get_db()
        db.execute(
            "UPDATE tasks SET title = ?, description = ?, status = ?, updated_at = ? "
            "WHERE id = ? AND user_id = ?",
            (title, description, status, now_iso(), task_id, current_user.id),
        )
        db.commit()
        flash("Task updated.", "success")
        return redirect(url_for("list_tasks"))

    return render_template(
        "task_form.html",
        task=task,
        statuses=ALLOWED_STATUSES,
        form_title=task["title"],
        form_description=task["description"],
        form_status=task["status"],
    )


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    get_own_task_or_404(task_id)
    db = get_db()
    db.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, current_user.id)
    )
    db.commit()
    flash("Task deleted.", "success")
    return redirect(url_for("list_tasks"))


# ---------------------------------------------------------------------------
# Routes: admin
# ---------------------------------------------------------------------------
@app.route("/admin/users")
@admin_required
def admin_users():
    users = get_db().execute(
        "SELECT id, username, is_admin, created_at FROM users ORDER BY created_at"
    ).fetchall()
    return render_template("admin_users.html", users=users)


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------
@app.errorhandler(403)
def forbidden(_e):
    return render_template("error.html", code=403, message="Forbidden"), 403


@app.errorhandler(404)
def not_found(_e):
    return render_template("error.html", code=404, message="Not found"), 404


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)
