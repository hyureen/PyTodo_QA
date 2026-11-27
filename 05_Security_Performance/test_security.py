"""
Week 5 - Safe, course-appropriate security tests derived from the STRIDE table.

All tests run ONLY against a temporary local database through the Flask test
client. Nothing is sent to any other system. These are controlled tests that
check a defence exists; they are not penetration testing.
"""

import sqlite3

import pytest
from flask.sessions import SecureCookieSessionInterface

from conftest import VALID_PASSWORD, create_task, make_user

pytestmark = pytest.mark.security


def forge_session(app, secret, data):
    """Sign a session cookie the same way Flask does, using a given secret."""
    original = app.secret_key
    app.secret_key = secret
    try:
        serializer = SecureCookieSessionInterface().get_signing_serializer(app)
        return serializer.dumps(data)
    finally:
        app.secret_key = original


# ---------------------------------------------------------------- Spoofing
def test_TC_SEC_001_cookie_httponly(fresh_app):
    c = fresh_app.app.test_client()
    r = c.post("/api/register", json={"username": "qa_user1", "password": VALID_PASSWORD})
    assert "HttpOnly" in r.headers.get("Set-Cookie", "")


def test_TC_SEC_002_wrong_key_rejected(fresh_app, user_b):
    cookie = forge_session(fresh_app.app, "wrong-key", {"user_id": 2, "username": "qa_user2"})
    c = fresh_app.app.test_client()
    c.set_cookie("session", cookie)
    assert c.get("/api/dashboard").status_code == 401


@pytest.mark.regression
def test_TC_SEC_003_forge_with_source_code_secret(fresh_app, user_a, user_b):
    create_task(user_b, title="qa_user2 secret plan")
    secret_from_source = "pytodo-pro-dev-secret"   # copied from app.py line: app.config["SECRET_KEY"]
    cookie = forge_session(fresh_app.app, secret_from_source, {"user_id": 2, "username": "qa_user2"})
    attacker = fresh_app.app.test_client()
    attacker.set_cookie("session", cookie)
    r = attacker.get("/api/tasks")
    assert r.status_code == 401, (f"Actual: HTTP {r.status_code}; forged cookie accepted and attacker read "
                                  f"{[t['title'] for t in r.get_json()]}")


def test_TC_SEC_004_no_login_attempt_limit(fresh_app):
    make_user(fresh_app, "qa_user1")
    c = fresh_app.app.test_client()
    codes = [c.post("/api/login", json={"username": "qa_user1", "password": f"guess{i}"}).status_code for i in range(10)]
    final = c.post("/api/login", json={"username": "qa_user1", "password": VALID_PASSWORD}).status_code
    limited = 429 in codes or final != 200
    assert limited, f"Actual: 10 wrong attempts all returned {set(codes)}; 11th (correct) returned {final}; no limit"


def test_TC_SEC_005_cookie_after_logout(fresh_app):
    c = make_user(fresh_app, "qa_user1")
    saved = c.get_cookie("session").value
    c.get("/logout")
    replay = fresh_app.app.test_client()
    replay.set_cookie("session", saved)
    r = replay.get("/api/dashboard")
    assert r.status_code == 401, f"Actual: HTTP {r.status_code}; old cookie still works after logout"


# ---------------------------------------------------------------- Tampering / Elevation
def test_TC_SEC_006_csrf_cross_site_delete(user_a):
    tid = create_task(user_a, title="Important").get_json()["id"]
    r = user_a.post(f"/tasks/{tid}/delete", headers={"Origin": "http://evil.example",
                                                     "Referer": "http://evil.example/page"})
    kept = user_a.get(f"/api/tasks/{tid}").status_code == 200
    assert kept, f"Actual: HTTP {r.status_code}; cross-site request without token deleted the task"


def test_TC_SEC_007_cross_user_update(user_a, user_b):
    tid = create_task(user_b, title="B task").get_json()["id"]
    assert user_a.put(f"/api/tasks/{tid}", json={"title": "changed by A"}).status_code == 404


@pytest.mark.regression
def test_TC_SEC_008_cross_user_delete(user_a, user_b):
    tid = create_task(user_b, title="B task").get_json()["id"]
    user_a.delete(f"/api/tasks/{tid}")
    assert user_b.get(f"/api/tasks/{tid}").status_code == 200, "Actual: qa_user1 deleted qa_user2's task"


# ---------------------------------------------------------------- Information disclosure
def test_TC_SEC_009_cross_user_read(user_a, user_b):
    tid = create_task(user_b, title="B task").get_json()["id"]
    assert user_a.get(f"/api/tasks/{tid}").status_code == 404


@pytest.mark.regression
def test_TC_SEC_010_search_injection(user_a, user_b):
    create_task(user_a, title="A task")
    create_task(user_b, title="B confidential")
    payload = "x%' OR user_id != 0 OR title LIKE '%"
    r = user_a.get("/api/tasks", query_string={"q": payload})
    titles = [t["title"] for t in r.get_json()] if r.status_code == 200 else []
    assert r.status_code in (200, 400) and "B confidential" not in titles, \
        f"Actual: HTTP {r.status_code}; injected condition returned other user's data: {titles}"


def test_TC_SEC_011_password_hashed(fresh_app):
    make_user(fresh_app, "qa_user1")
    row = sqlite3.connect(fresh_app.DATABASE).execute("SELECT password_hash FROM users").fetchone()
    assert VALID_PASSWORD not in row[0] and row[0].split(":")[0] in ("scrypt", "pbkdf2")


@pytest.mark.regression
def test_TC_SEC_012_stored_xss(user_a):
    create_task(user_a, title="<img src=x onerror=alert(1)>")
    html = user_a.get("/").get_data(as_text=True)
    assert "<img src=x onerror=alert(1)>" not in html, "Actual: title rendered as live HTML (script would run)"


def test_TC_SEC_014_cross_user_edit_page(user_a, user_b):
    tid = create_task(user_b, title="B task").get_json()["id"]
    r = user_a.get(f"/tasks/{tid}/edit")
    assert r.status_code == 302
