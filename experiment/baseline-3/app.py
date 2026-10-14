import os
import secrets
import sqlite3
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
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config["DATABASE"] = os.environ.get("DATABASE", os.path.join(BASE_DIR, "tasks.db"))
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

STATUSES = ["To Do", "In Progress", "Done"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'To Do',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
"""


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(app.config["DATABASE"])
    db.executescript(SCHEMA)
    db.commit()
    db.close()


@app.cli.command("init-db")
def init_db_command():
    """Create the database tables."""
    init_db()
    click.echo("Initialized the database.")


@app.cli.command("make-admin")
@click.argument("username")
def make_admin_command(username):
    """Grant the administrator role to an existing user."""
    init_db()
    with app.app_context():
        db = get_db()
        cur = db.execute("UPDATE users SET is_admin = 1 WHERE username = ?", (username,))
        db.commit()
        if cur.rowcount:
            click.echo(f"User '{username}' is now an administrator.")
        else:
            click.echo(f"No user named '{username}' was found.")


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

@app.before_request
def load_user():
    user_id = session.get("user_id")
    g.user = None
    if user_id is not None:
        g.user = get_db().execute(
            "SELECT id, username, is_admin FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if g.user is None:
            session.clear()


@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.get("csrf_token")
        if not token or not secrets.compare_digest(token, request.form.get("csrf_token", "")):
            abort(400, description="Invalid or missing CSRF token.")


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]


app.jinja_env.globals["csrf_token"] = csrf_token


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            flash("Please log in first.")
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


def get_own_task(task_id):
    """Fetch a task belonging to the current user, or return 404."""
    task = get_db().execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, g.user["id"])
    ).fetchone()
    if task is None:
        abort(404)
    return task


def read_task_form():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    status = request.form.get("status", STATUSES[0])
    errors = []
    if not title:
        errors.append("Title is required.")
    elif len(title) > 200:
        errors.append("Title must be 200 characters or fewer.")
    if len(description) > 5000:
        errors.append("Description must be 5000 characters or fewer.")
    if status not in STATUSES:
        errors.append("Invalid status.")
    return title, description, status, errors


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if g.user:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")
        error = None
        if not username or not password:
            error = "Username and password are required."
        elif len(username) > 50:
            error = "Username must be 50 characters or fewer."
        elif len(password) < 8:
            error = "Password must be at least 8 characters."
        elif password != confirm:
            error = "Passwords do not match."

        if error is None:
            db = get_db()
            # The very first account becomes the administrator.
            is_first = db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0
            try:
                db.execute(
                    "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                    (username, generate_password_hash(password), 1 if is_first else 0),
                )
                db.commit()
            except sqlite3.IntegrityError:
                error = "That username is already taken."
            else:
                flash("Registration successful. Please log in.")
                return redirect(url_for("login"))
        flash(error)
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_db().execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.")
        else:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Task routes
# ---------------------------------------------------------------------------

@app.route("/")
@login_required
def index():
    tasks = get_db().execute(
        "SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC, id DESC",
        (g.user["id"],),
    ).fetchall()
    return render_template("index.html", tasks=tasks)


@app.route("/tasks/new", methods=["GET", "POST"])
@login_required
def create_task():
    if request.method == "POST":
        title, description, status, errors = read_task_form()
        if not errors:
            db = get_db()
            db.execute(
                "INSERT INTO tasks (user_id, title, description, status) VALUES (?, ?, ?, ?)",
                (g.user["id"], title, description, status),
            )
            db.commit()
            flash("Task created.")
            return redirect(url_for("index"))
        for e in errors:
            flash(e)
        task = {"title": title, "description": description, "status": status}
        return render_template("task_form.html", task=task, statuses=STATUSES, action="Create")
    return render_template("task_form.html", task=None, statuses=STATUSES, action="Create")


@app.route("/tasks/<int:task_id>")
@login_required
def view_task(task_id):
    return render_template("task_view.html", task=get_own_task(task_id))


@app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = get_own_task(task_id)
    if request.method == "POST":
        title, description, status, errors = read_task_form()
        if not errors:
            db = get_db()
            db.execute(
                "UPDATE tasks SET title = ?, description = ?, status = ? WHERE id = ? AND user_id = ?",
                (title, description, status, task_id, g.user["id"]),
            )
            db.commit()
            flash("Task updated.")
            return redirect(url_for("view_task", task_id=task_id))
        for e in errors:
            flash(e)
        task = {"id": task_id, "title": title, "description": description, "status": status}
    return render_template("task_form.html", task=task, statuses=STATUSES, action="Save")


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    get_own_task(task_id)
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, g.user["id"]))
    db.commit()
    flash("Task deleted.")
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Admin routes
# ---------------------------------------------------------------------------

@app.route("/admin")
@admin_required
def admin():
    users = get_db().execute(
        """
        SELECT u.id, u.username, u.is_admin, u.created_at, COUNT(t.id) AS task_count
        FROM users u LEFT JOIN tasks t ON t.user_id = u.id
        GROUP BY u.id ORDER BY u.id
        """
    ).fetchall()
    return render_template("admin.html", users=users)


@app.errorhandler(403)
def forbidden(e):
    return render_template("error.html", code=403, message="You do not have permission to view this page."), 403


@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="Page not found."), 404


init_db()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", port=int(os.environ.get("PORT", 5001)))
