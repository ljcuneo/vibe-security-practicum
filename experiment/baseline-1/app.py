import os
import sqlite3
from functools import wraps

from flask import Flask, g, redirect, render_template, request, session, url_for, flash, abort
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "tasks.db")
SCHEMA = os.path.join(BASE_DIR, "schema.sql")

STATUS_CHOICES = ["pending", "in_progress", "done"]

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
    return db


@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    db_exists = os.path.exists(DATABASE)
    db = sqlite3.connect(DATABASE)
    with open(SCHEMA) as f:
        db.executescript(f.read())
    db.commit()
    db.close()
    if not db_exists:
        print("Initialized new database at", DATABASE)


def current_user():
    if "user_id" not in session:
        return None
    if "_user" not in g.__dict__:
        db = get_db()
        g._user = db.execute(
            "SELECT * FROM users WHERE id = ?", (session["user_id"],)
        ).fetchone()
    return g._user


@app.context_processor
def inject_user():
    return {"current_user": current_user()}


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user() is None:
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = current_user()
        if user is None:
            return redirect(url_for("login", next=request.path))
        if not user["is_admin"]:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


@app.route("/")
def index():
    if current_user() is not None:
        return redirect(url_for("list_tasks"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user() is not None:
        return redirect(url_for("list_tasks"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        error = None
        if not username or not password:
            error = "Username and password are required."
        elif len(password) < 6:
            error = "Password must be at least 6 characters long."
        elif password != confirm:
            error = "Passwords do not match."

        db = get_db()
        if error is None:
            existing = db.execute(
                "SELECT id FROM users WHERE username = ?", (username,)
            ).fetchone()
            if existing is not None:
                error = f"Username '{username}' is already taken."

        if error is None:
            user_count = db.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
            is_admin = 1 if user_count == 0 else 0
            db.execute(
                "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                (username, generate_password_hash(password), is_admin),
            )
            db.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))

        flash(error, "error")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user() is not None:
        return redirect(url_for("list_tasks"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.", "error")
        else:
            session.clear()
            session["user_id"] = user["id"]
            next_url = request.args.get("next")
            return redirect(next_url or url_for("list_tasks"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/tasks")
@login_required
def list_tasks():
    db = get_db()
    tasks = db.execute(
        "SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC",
        (current_user()["id"],),
    ).fetchall()
    return render_template("tasks.html", tasks=tasks)


@app.route("/tasks/new", methods=["GET", "POST"])
@login_required
def new_task():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "pending")

        error = None
        if not title:
            error = "Title is required."
        elif status not in STATUS_CHOICES:
            error = "Invalid status."

        if error is None:
            db = get_db()
            db.execute(
                "INSERT INTO tasks (user_id, title, description, status) VALUES (?, ?, ?, ?)",
                (current_user()["id"], title, description, status),
            )
            db.commit()
            flash("Task created.", "success")
            return redirect(url_for("list_tasks"))

        flash(error, "error")
        return render_template(
            "task_form.html",
            task={"title": title, "description": description, "status": status},
            statuses=STATUS_CHOICES,
            form_action=url_for("new_task"),
            heading="New Task",
        )

    return render_template(
        "task_form.html",
        task=None,
        statuses=STATUS_CHOICES,
        form_action=url_for("new_task"),
        heading="New Task",
    )


def get_owned_task(task_id):
    db = get_db()
    task = db.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, current_user()["id"]),
    ).fetchone()
    if task is None:
        abort(404)
    return task


@app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = get_owned_task(task_id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "pending")

        error = None
        if not title:
            error = "Title is required."
        elif status not in STATUS_CHOICES:
            error = "Invalid status."

        if error is None:
            db = get_db()
            db.execute(
                "UPDATE tasks SET title = ?, description = ?, status = ? WHERE id = ? AND user_id = ?",
                (title, description, status, task_id, current_user()["id"]),
            )
            db.commit()
            flash("Task updated.", "success")
            return redirect(url_for("list_tasks"))

        flash(error, "error")
        return render_template(
            "task_form.html",
            task={"title": title, "description": description, "status": status},
            statuses=STATUS_CHOICES,
            form_action=url_for("edit_task", task_id=task_id),
            heading="Edit Task",
        )

    return render_template(
        "task_form.html",
        task=task,
        statuses=STATUS_CHOICES,
        form_action=url_for("edit_task", task_id=task_id),
        heading="Edit Task",
    )


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    get_owned_task(task_id)
    db = get_db()
    db.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, current_user()["id"]),
    )
    db.commit()
    flash("Task deleted.", "success")
    return redirect(url_for("list_tasks"))


@app.route("/admin/users")
@admin_required
def admin_users():
    db = get_db()
    users = db.execute(
        "SELECT id, username, is_admin, created_at FROM users ORDER BY created_at ASC"
    ).fetchall()
    return render_template("admin_users.html", users=users)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
else:
    init_db()
