"""End-to-end smoke test. Run with: .venv/bin/python test_smoke.py

Uses a throwaway database, so it does not touch instance/tasks.db.
"""
import os
import re
import tempfile

import app as app_module

tmpdir = tempfile.mkdtemp()
app_module.DATABASE = os.path.join(tmpdir, "test.db")
app_module.init_db()
app = app_module.app

PASSWORD = "correct-horse-42"


def token(client, path):
    html = client.get(path).get_data(as_text=True)
    return re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)


def post(client, path, data, token_path=None):
    data = dict(data, csrf_token=token(client, token_path or path))
    return client.post(path, data=data)


def register(client, username, password=PASSWORD):
    return post(
        client,
        "/register",
        {"username": username, "password": password, "confirm": password},
    )


def login(client, username, password=PASSWORD):
    return post(client, "/login", {"username": username, "password": password})


alice, bob, anon = app.test_client(), app.test_client(), app.test_client()

# Authentication is required.
assert anon.get("/").status_code == 302
assert anon.get("/tasks/new").status_code == 302
assert anon.get("/admin/users").status_code == 302

# Security headers and cookie flags.
r = anon.get("/login")
assert "frame-ancestors 'none'" in r.headers["Content-Security-Policy"]
assert r.headers["X-Content-Type-Options"] == "nosniff"
cookie = r.headers["Set-Cookie"]
assert "HttpOnly" in cookie and "SameSite=Lax" in cookie

# Password policy.
assert b"at least 10" in register(anon, "weak", "short1").data
assert b"letter and one digit" in register(anon, "weak", "onlyletters").data
assert b"contain the username" in register(anon, "weakuser", "weakuser123").data

# Registration, duplicate usernames (case-insensitive), login.
assert register(alice, "alice").status_code == 302
assert b"not available" in register(anon, "ALICE").data
assert register(bob, "bob").status_code == 302
assert login(alice, "alice").status_code == 302
assert login(bob, "bob").status_code == 302

# Passwords are hashed.
with app.app_context():
    stored = app_module.get_db().execute(
        "SELECT password_hash FROM users WHERE username = 'alice'"
    ).fetchone()[0]
assert PASSWORD not in stored and stored.startswith("scrypt:")

# CSRF: a POST without a token is rejected.
assert alice.post("/tasks/new", data={"title": "x", "status": "todo"}).status_code == 400

# Input validation.
bad = {"title": "", "description": "", "status": "todo"}
assert b"Title is required" in post(alice, "/tasks/new", bad).data
bad = {"title": "t", "description": "", "status": "bogus"}
assert b"Invalid status" in post(alice, "/tasks/new", bad).data

# Create, with output escaping and an injection-shaped title stored verbatim.
xss = "<script>alert(1)</script>' OR 1=1 --"
r = post(alice, "/tasks/new", {"title": xss, "description": "d", "status": "todo"})
assert r.status_code == 302
page = alice.get("/").get_data(as_text=True)
assert "<script>alert(1)</script>" not in page
assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page

# Object-level authorization: bob cannot see, edit, or delete alice's task.
assert "alert(1)" not in bob.get("/").get_data(as_text=True)
assert bob.get("/tasks/1/edit").status_code == 404
edit = {"title": "hacked", "description": "", "status": "done"}
assert post(bob, "/tasks/1/edit", edit, token_path="/tasks/new").status_code == 404
assert post(bob, "/tasks/1/delete", {}, token_path="/tasks/new").status_code == 404
assert "alert(1)" in alice.get("/").get_data(as_text=True)

# Owner can edit and delete.
edit = {"title": "renamed", "description": "new", "status": "done"}
assert post(alice, "/tasks/1/edit", edit).status_code == 302
assert "renamed" in alice.get("/").get_data(as_text=True)
assert post(alice, "/tasks/1/delete", {}, token_path="/tasks/new").status_code == 302
assert "renamed" not in alice.get("/").get_data(as_text=True)

# Admin authorization.
assert alice.get("/admin/users").status_code == 403
result = app.test_cli_runner().invoke(
    args=["create-admin", "--username", "root_admin", "--password", PASSWORD]
)
assert result.exit_code == 0, result.output
admin = app.test_client()
assert login(admin, "root_admin").status_code == 302
users_page = admin.get("/admin/users").get_data(as_text=True)
assert "alice" in users_page and "bob" in users_page and "scrypt" not in users_page

# Logout ends the session.
assert post(alice, "/logout", {}, token_path="/tasks/new").status_code == 302
assert alice.get("/").status_code == 302

# Login throttling: lockout after repeated failures, even with the right password.
for _ in range(app_module.MAX_FAILURES_PER_USERNAME):
    assert b"Invalid username or password" in login(anon, "bob", "wrong-password-1").data
assert login(anon, "bob", "wrong-password-1").status_code == 429
assert login(anon, "bob").status_code == 429

print("All smoke tests passed.")
