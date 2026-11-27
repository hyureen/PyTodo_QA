"""
Shared PyTest fixtures for the PyTodo Pro QA project.

- Every test gets a brand-new temporary SQLite database, so tests never
  depend on each other or on your real pytodo_pro.db.
- The Flask test client is used for web-form and API tests (no server needed).
- Dates are always calculated relative to "today", so the suite gives the
  same result on any day it is run.
"""

import os
import sys
from datetime import date, timedelta

import pytest

ROOT = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(ROOT, "app")
sys.path.insert(0, APP_DIR)

import app as pytodo  # noqa: E402  (the application under test, unmodified)

VALID_PASSWORD = "Passw0rd123"   # 11 characters: clearly valid under the spec


def day(offset):
    """Return a YYYY-MM-DD string `offset` days from today (negative = past)."""
    return (date.today() + timedelta(days=offset)).isoformat()


@pytest.fixture
def fresh_app(tmp_path):
    pytodo.DATABASE = str(tmp_path / "test.db")
    pytodo.app.config.update(TESTING=False, PROPAGATE_EXCEPTIONS=False)
    pytodo.init_db()
    yield pytodo


@pytest.fixture
def client(fresh_app):
    """Anonymous (not logged in) client."""
    return fresh_app.app.test_client()


def make_user(fresh_app, username, password=VALID_PASSWORD):
    c = fresh_app.app.test_client()
    r = c.post("/api/register", json={"username": username, "password": password})
    assert r.status_code == 201, f"setup failed: could not register {username}"
    return c


@pytest.fixture
def user_a(fresh_app):
    """Logged-in client for qa_user1."""
    return make_user(fresh_app, "qa_user1")


@pytest.fixture
def user_b(fresh_app):
    """Logged-in client for qa_user2 (used for cross-user checks)."""
    return make_user(fresh_app, "qa_user2")


def create_task(c, **fields):
    body = {"title": "Sample task"}
    body.update(fields)
    r = c.post("/api/tasks", json=body)
    return r
