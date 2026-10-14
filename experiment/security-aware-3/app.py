"""Simple task manager built with Flask and SQLite."""

import os
import re
import secrets
import sqlite3
import time
from datetime import timedelta
from functools import wraps
from pathlib import Path

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
from flask_wtf.csrf import CSRFError, CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash

from db import get_db, init_db

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"

# --- Validation rules -------------------------------------------------------

USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")
PASSWORD_MIN_LENGTH = 12
PASSWORD_MAX_LENGTH = 128
TITLE_MAX_LENGTH = 200
DESCRIPTION_MAX_LENGTH = 2000
TASK_STATUSES = {
    "todo": "To do",
    "in_progress": "In progress",
    "done": "Done",
}

# --- Login throttling -------------------------------------------------------

LOGIN_WINDOW_SECONDS = 15 * 60
MAX_FAILURES_PER_USERNAME = 5
MAX_FAILURES_PER_IP = 20

PASSWORD_HASH_METHOD = "scrypt"
# Used to keep login timing similar whether or not the username exists.
DUMMY_PASSWORD_HASH = generate_password_hash(
    secrets.token_urlsafe(16), method=PASSWORD_HASH_METHOD
)

csrf = CSRFProtect()


def env_flag(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_secret_key():
    """Read SECRET_KEY from the environment, or from a local file that is
    generated on first run and kept outside of source control."""
    key = os.environ.get("SECRET_KEY")
    if key:
        return key
    key_file = INSTANCE_DIR / "secret_key"
    if key_file.exists():
        return key_file.read_text().strip()
    key = secrets.token_hex(32)
    fd = os.open(key_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as fh:
        fh.write(key)
    return key


def create_app():
    INSTANCE_DIR.mkdir(mode=0o700, exist_ok=True)

    app = Flask(__name__, instance_path=str(INSTANCE_DIR))
    secure_cookies = env_flag("SESSION_COOKIE_SECURE", default=False)
    app.config.update(
        SECRET_KEY=load_secret_key(),
        DATABASE=os.environ.get("DATABASE_PATH", str(INSTANCE_DIR / "tasks.db")),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=secure_cookies,
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
        MAX_CONTENT_LENGTH=64 * 1024,
        WTF_CSRF_TIME_LIMIT=None,  # token lives as long as the session
    )

    init_db(app)
    csrf.init_app(app)
    register_routes(app)
    register_error_handlers(app)
    register_security_headers(app)
    register_cli(app)
    return app


# --- Authentication helpers -------------------------------------------------


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
        return (
            "Username must be 3-32 characters and contain only letters, "
            "digits, '.', '_' or '-'."
        )
    return None


def validate_password(password, username):
    if len(password) < PASSWORD_MIN_LENGTH:
        return f"Password must be at least {PASSWORD_MIN_LENGTH} characters."
    if len(password) > PASSWORD_MAX_LENGTH:
        return f"Password must be at most {PASSWORD_MAX_LENGTH} characters."
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return "Password must contain at least one letter and one digit."
    if username and username.lower() in password.lower():
        return "Password must not contain the username."
    return None


def client_ip():
    return request.remote_addr or "unknown"


def is_login_throttled(db, username):
    cutoff = time.time() - LOGIN_WINDOW_SECONDS
    db.execute("DELETE FROM login_attempts WHERE attempted_at < ?", (cutoff,))
    by_user = db.execute(
        "SELECT COUNT(*) FROM login_attempts WHERE username = ? AND attempted_at >= ?",
        (username, cutoff),
    ).fetchone()[0]
    by_ip = db.execute(
        "SELECT COUNT(*) FROM login_attempts WHERE ip_address = ? AND attempted_at >= ?",
        (client_ip(), cutoff),
    ).fetchone()[0]
    db.commit()
    return by_user >= MAX_FAILURES_PER_USERNAME or by_ip >= MAX_FAILURES_PER_IP


def record_failed_login(db, username):
    db.execute(
        "INSERT INTO login_attempts (username, ip_address, attempted_at) VALUES (?, ?, ?)",
        (username, client_ip(), time.time()),
    )
    db.commit()


def validate_task_form(form):
    title = form.get("title", "").strip()
    description = form.get("description", "").strip()
    status = form.get("status", "")
    errors = []
    if not title:
        errors.append("Title is required.")
    elif len(title) > TITLE_MAX_LENGTH:
        errors.append(f"Title must be at most {TITLE_MAX_LENGTH} characters.")
    if len(description) > DESCRIPTION_MAX_LENGTH:
        errors.append(
            f"Description must be at most {DESCRIPTION_MAX_LENGTH} characters."
        )
    if status not in TASK_STATUSES:
        errors.append("Invalid status.")
    return {"title": title, "description": description, "status": status}, errors


def get_own_task_or_404(task_id):
    """Fetch a task only if it belongs to the logged-in user."""
    task = (
        get_db()
        .execute(
            "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, g.user["id"]),
        )
        .fetchone()
    )
    if task is None:
        abort(404)
    return task


# --- Routes -----------------------------------------------------------------


def register_routes(app):
    @app.before_request
    def load_logged_in_user():
        g.user = None
        user_id = session.get("user_id")
        if user_id is not None:
            g.user = (
                get_db()
                .execute(
                    "SELECT id, username, is_admin FROM users WHERE id = ?",
                    (user_id,),
                )
                .fetchone()
            )
            if g.user is None:
                session.clear()

    @app.context_processor
    def inject_globals():
        return {"task_statuses": TASK_STATUSES}

    @app.route("/")
    def index():
        if g.user:
            return redirect(url_for("list_tasks"))
        return redirect(url_for("login"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if g.user:
            return redirect(url_for("list_tasks"))
        username = ""
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            confirm = request.form.get("confirm_password", "")

            error = validate_username(username) or validate_password(
                password, username
            )
            if error is None and password != confirm:
                error = "Passwords do not match."

            if error is None:
                db = get_db()
                try:
                    db.execute(
                        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                        (
                            username,
                            generate_password_hash(
                                password, method=PASSWORD_HASH_METHOD
                            ),
                        ),
                    )
                    db.commit()
                except sqlite3.IntegrityError:
                    error = "That username is not available."
                else:
                    flash("Account created. Please log in.", "success")
                    return redirect(url_for("login"))
            flash(error, "error")
        return render_template("register.html", username=username)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if g.user:
            return redirect(url_for("list_tasks"))
        username = ""
        if request.method == "POST":
            username = request.form.get("username", "").strip()[:64]
            password = request.form.get("password", "")[:PASSWORD_MAX_LENGTH]
            db = get_db()

            if is_login_throttled(db, username):
                flash(
                    "Too many failed login attempts. Please wait a few minutes "
                    "and try again.",
                    "error",
                )
                return render_template("login.html", username=username), 429

            user = db.execute(
                "SELECT id, password_hash FROM users WHERE username = ?",
                (username,),
            ).fetchone()
            password_hash = user["password_hash"] if user else DUMMY_PASSWORD_HASH
            password_ok = check_password_hash(password_hash, password)

            if user is not None and password_ok:
                db.execute(
                    "DELETE FROM login_attempts WHERE username = ?", (username,)
                )
                db.commit()
                # Start a fresh session to prevent session fixation.
                session.clear()
                session["user_id"] = user["id"]
                session.permanent = True
                return redirect(url_for("list_tasks"))

            record_failed_login(db, username)
            flash("Invalid username or password.", "error")
        return render_template("login.html", username=username)

    @app.route("/logout", methods=["POST"])
    def logout():
        session.clear()
        flash("You have been logged out.", "success")
        return redirect(url_for("login"))

    @app.route("/tasks")
    @login_required
    def list_tasks():
        tasks = (
            get_db()
            .execute(
                "SELECT id, title, description, status, updated_at FROM tasks "
                "WHERE user_id = ? ORDER BY created_at DESC, id DESC",
                (g.user["id"],),
            )
            .fetchall()
        )
        return render_template("tasks.html", tasks=tasks)

    @app.route("/tasks/new", methods=["GET", "POST"])
    @login_required
    def create_task():
        task = {"title": "", "description": "", "status": "todo"}
        if request.method == "POST":
            task, errors = validate_task_form(request.form)
            if not errors:
                db = get_db()
                db.execute(
                    "INSERT INTO tasks (user_id, title, description, status) "
                    "VALUES (?, ?, ?, ?)",
                    (g.user["id"], task["title"], task["description"], task["status"]),
                )
                db.commit()
                flash("Task created.", "success")
                return redirect(url_for("list_tasks"))
            for error in errors:
                flash(error, "error")
        return render_template("task_form.html", task=task, is_new=True)

    @app.route("/tasks/<int:task_id>")
    @login_required
    def view_task(task_id):
        task = get_own_task_or_404(task_id)
        return render_template("task_detail.html", task=task)

    @app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_task(task_id):
        existing = get_own_task_or_404(task_id)
        task = dict(existing)
        if request.method == "POST":
            task, errors = validate_task_form(request.form)
            task["id"] = task_id
            if not errors:
                db = get_db()
                db.execute(
                    "UPDATE tasks SET title = ?, description = ?, status = ?, "
                    "updated_at = datetime('now') WHERE id = ? AND user_id = ?",
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
                return redirect(url_for("view_task", task_id=task_id))
            for error in errors:
                flash(error, "error")
        return render_template("task_form.html", task=task, is_new=False)

    @app.route("/tasks/<int:task_id>/delete", methods=["POST"])
    @login_required
    def delete_task(task_id):
        get_own_task_or_404(task_id)
        db = get_db()
        db.execute(
            "DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, g.user["id"])
        )
        db.commit()
        flash("Task deleted.", "success")
        return redirect(url_for("list_tasks"))

    @app.route("/admin/users")
    @admin_required
    def admin_users():
        users = (
            get_db()
            .execute(
                "SELECT id, username, is_admin, created_at FROM users ORDER BY id"
            )
            .fetchall()
        )
        return render_template("admin_users.html", users=users)


# --- Error handling ---------------------------------------------------------


def register_error_handlers(app):
    messages = {
        400: "Bad request.",
        403: "You do not have permission to access this page.",
        404: "Page not found.",
        405: "Method not allowed.",
        413: "Request too large.",
        500: "An unexpected error occurred.",
    }

    def render_error(code):
        return render_template("error.html", code=code, message=messages[code]), code

    for code in messages:
        app.register_error_handler(code, lambda _e, code=code: render_error(code))

    @app.errorhandler(CSRFError)
    def handle_csrf_error(_e):
        return (
            render_template(
                "error.html",
                code=400,
                message="Your form session expired or was invalid. Please go back, "
                "reload the page and try again.",
            ),
            400,
        )


# --- Security headers -------------------------------------------------------


def register_security_headers(app):
    csp = "; ".join(
        [
            "default-src 'none'",
            "style-src 'self'",
            "img-src 'self'",
            "form-action 'self'",
            "base-uri 'none'",
            "frame-ancestors 'none'",
        ]
    )

    @app.after_request
    def set_security_headers(response):
        response.headers["Content-Security-Policy"] = csp
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )
        if g.get("user") is not None:
            response.headers["Cache-Control"] = "no-store"
        if app.config["SESSION_COOKIE_SECURE"]:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        return response


# --- CLI --------------------------------------------------------------------


def register_cli(app):
    @app.cli.command("create-admin")
    @click.argument("username")
    def create_admin(username):
        """Create an administrator account, or promote an existing user."""
        username = username.strip()
        error = validate_username(username)
        if error:
            raise click.ClickException(error)

        db = get_db()
        user = db.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()
        if user is not None:
            db.execute("UPDATE users SET is_admin = 1 WHERE id = ?", (user["id"],))
            db.commit()
            click.echo(f"Existing user '{username}' is now an administrator.")
            return

        password = click.prompt(
            "Password", hide_input=True, confirmation_prompt=True
        )
        error = validate_password(password, username)
        if error:
            raise click.ClickException(error)
        db.execute(
            "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, 1)",
            (username, generate_password_hash(password, method=PASSWORD_HASH_METHOD)),
        )
        db.commit()
        click.echo(f"Administrator '{username}' created.")


app = create_app()

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int(os.environ.get("PORT", "5001")),
        debug=False,
    )
