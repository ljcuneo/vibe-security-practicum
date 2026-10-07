import os
import sqlite3
from functools import wraps

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

import db

STATUS_CHOICES = ["todo", "in_progress", "done"]
STATUS_LABELS = {"todo": "To Do", "in_progress": "In Progress", "done": "Done"}


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production"),
        DATABASE=os.path.join(app.instance_path, "tasks.db"),
    )
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

    if not os.path.exists(app.config["DATABASE"]):
        with app.app_context():
            db.init_db()

    app.jinja_env.globals["STATUS_LABELS"] = STATUS_LABELS

    register_routes(app)
    return app


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login"))
        if not g.user["is_admin"]:
            flash("Administrator access required.")
            return redirect(url_for("tasks_list"))
        return view(*args, **kwargs)

    return wrapped_view


def register_routes(app):
    @app.before_request
    def load_logged_in_user():
        user_id = session.get("user_id")
        if user_id is None:
            g.user = None
        else:
            g.user = (
                db.get_db()
                .execute("SELECT * FROM users WHERE id = ?", (user_id,))
                .fetchone()
            )

    @app.route("/")
    def index():
        if g.user is None:
            return redirect(url_for("login"))
        return redirect(url_for("tasks_list"))

    @app.route("/register", methods=("GET", "POST"))
    def register():
        if g.user is not None:
            return redirect(url_for("tasks_list"))

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            error = None

            if not username:
                error = "Username is required."
            elif not password:
                error = "Password is required."
            elif len(password) < 8:
                error = "Password must be at least 8 characters long."

            database = db.get_db()
            if error is None:
                try:
                    is_first_user = (
                        database.execute("SELECT COUNT(*) AS count FROM users").fetchone()["count"]
                        == 0
                    )
                    database.execute(
                        "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                        (username, generate_password_hash(password), 1 if is_first_user else 0),
                    )
                    database.commit()
                except sqlite3.IntegrityError:
                    error = f"Username '{username}' is already taken."
                else:
                    flash("Registration successful. Please log in.")
                    return redirect(url_for("login"))

            flash(error)

        return render_template("register.html")

    @app.route("/login", methods=("GET", "POST"))
    def login():
        if g.user is not None:
            return redirect(url_for("tasks_list"))

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            error = None

            user = (
                db.get_db()
                .execute("SELECT * FROM users WHERE username = ?", (username,))
                .fetchone()
            )

            if user is None or not check_password_hash(user["password_hash"], password):
                error = "Incorrect username or password."

            if error is None:
                session.clear()
                session["user_id"] = user["id"]
                return redirect(url_for("tasks_list"))

            flash(error)

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/tasks")
    @login_required
    def tasks_list():
        user_tasks = (
            db.get_db()
            .execute(
                "SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC",
                (g.user["id"],),
            )
            .fetchall()
        )
        return render_template("tasks.html", tasks=user_tasks)

    @app.route("/tasks/new", methods=("GET", "POST"))
    @login_required
    def task_new():
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            description = request.form.get("description", "").strip()
            status = request.form.get("status", STATUS_CHOICES[0])
            error = None

            if not title:
                error = "Title is required."
            elif status not in STATUS_CHOICES:
                error = "Invalid status."

            if error is None:
                db.get_db().execute(
                    "INSERT INTO tasks (user_id, title, description, status) VALUES (?, ?, ?, ?)",
                    (g.user["id"], title, description, status),
                )
                db.get_db().commit()
                return redirect(url_for("tasks_list"))

            flash(error)

        return render_template(
            "task_form.html", task=None, statuses=STATUS_CHOICES, form_action=url_for("task_new")
        )

    def get_owned_task(task_id):
        task = (
            db.get_db()
            .execute(
                "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
                (task_id, g.user["id"]),
            )
            .fetchone()
        )
        if task is None:
            flash("Task not found.")
        return task

    @app.route("/tasks/<int:task_id>/edit", methods=("GET", "POST"))
    @login_required
    def task_edit(task_id):
        task = get_owned_task(task_id)
        if task is None:
            return redirect(url_for("tasks_list"))

        if request.method == "POST":
            title = request.form.get("title", "").strip()
            description = request.form.get("description", "").strip()
            status = request.form.get("status", STATUS_CHOICES[0])
            error = None

            if not title:
                error = "Title is required."
            elif status not in STATUS_CHOICES:
                error = "Invalid status."

            if error is None:
                db.get_db().execute(
                    "UPDATE tasks SET title = ?, description = ?, status = ? WHERE id = ? AND user_id = ?",
                    (title, description, status, task_id, g.user["id"]),
                )
                db.get_db().commit()
                return redirect(url_for("tasks_list"))

            flash(error)

        return render_template(
            "task_form.html",
            task=task,
            statuses=STATUS_CHOICES,
            form_action=url_for("task_edit", task_id=task_id),
        )

    @app.route("/tasks/<int:task_id>/delete", methods=("POST",))
    @login_required
    def task_delete(task_id):
        task = get_owned_task(task_id)
        if task is not None:
            db.get_db().execute(
                "DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, g.user["id"])
            )
            db.get_db().commit()
        return redirect(url_for("tasks_list"))

    @app.route("/admin/users")
    @admin_required
    def admin_users():
        users = (
            db.get_db()
            .execute("SELECT id, username, is_admin, created_at FROM users ORDER BY id")
            .fetchall()
        )
        return render_template("admin_users.html", users=users)


app = create_app()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
