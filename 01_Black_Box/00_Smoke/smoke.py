"""
00_Smoke/smoke.py - QA Lead exploratory smoke test for PyTodo Pro.

Re-checks the candidate defects (CD-01 .. CD-17) listed in the QA Test Lead Pack.
Uses Flask's built-in test client, so the server does NOT need to be running,
and uses a throw-away database so your real pytodo_pro.db is untouched.

Usage (from the repository root):
    python 00_Smoke/smoke.py path/to/pytodo_pro_app_folder

Output: one line per check -> "CONFIRMED" (spec violated) or "not reproduced".
These are candidates only. Reproduce manually and send to Member 4 for a DEF-ID.
"""

import os
import sys
import tempfile
from datetime import date, datetime

APP_DIR = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
sys.path.insert(0, APP_DIR)

import app as pytodo  # noqa: E402
from helpers import compute_urgency, completed_in_last_n_days, is_valid_password  # noqa: E402

pytodo.DATABASE = os.path.join(tempfile.mkdtemp(), "smoke.db")
pytodo.init_db()
pytodo.app.config["TESTING"] = False      # we want real 500 responses, not exceptions
pytodo.app.config["PROPAGATE_EXCEPTIONS"] = False

results = []


def check(cand_id, title, violated):
    results.append((cand_id, title, violated))
    print(f"{cand_id:6} {'CONFIRMED     ' if violated else 'not reproduced'}  {title}")


def client_for(username, password="password123"):
    c = pytodo.app.test_client()
    c.post("/api/register", json={"username": username, "password": password})
    return c


# ---- helpers.py business rules (fixed 'today' so results don't depend on the run date)
today = date(2026, 11, 15)
check("CD-01", "Task due today is labelled 'Due Today'",
      compute_urgency("2026-11-15", today) != "Due Today")
check("CD-02", "8-character password is accepted",
      is_valid_password("abcdefgh") is not True)
check("CD-03", "Completion exactly 7 days ago counts toward last-7-days",
      completed_in_last_n_days("2026-11-08 12:00:00", 7, datetime(2026, 11, 15, 12)) is not True)

# ---- registration / login
a = client_for("alice")
dup = pytodo.app.test_client().post("/api/register", json={"username": "alice", "password": "different123"})
check("CD-04", "Duplicate username is rejected", dup.status_code == 201)

# ---- authorisation: cross-user delete
b = client_for("bob_1")
bob_task = b.post("/api/tasks", json={"title": "bob private"}).get_json()["id"]
a.delete(f"/api/tasks/{bob_task}")
check("CD-05", "User A cannot delete User B's task",
      b.get(f"/api/tasks/{bob_task}").status_code == 404)

# ---- search input reaches SQL
check("CD-06", "A single quote in search does not cause HTTP 500",
      a.get("/api/tasks?q='").status_code == 500)

# ---- output encoding
a.post("/api/tasks", json={"title": "<i id='xss-probe'>hi</i>"})
check("CD-07", "HTML in a task title is escaped on the task list",
      b"<i id='xss-probe'>" in a.get("/").data)

# ---- invalid due date (use a separate user: this one breaks the account)
c = client_for("carol")
c.post("/api/tasks", json={"title": "bad date", "due_date": "2026-02-30"})
check("CD-08", "Invalid due date rejected and list still loads",
      c.get("/api/tasks").status_code == 500 or c.get("/dashboard").status_code == 500)

# ---- validation consistency
r = a.post("/tasks/new", data={"title": "   "})
blank_web = any(t["title"] == "" for t in a.get("/api/tasks?per_page=100").get_json())
tid = a.post("/api/tasks", json={"title": "valid"}).get_json()["id"]
blank_api = a.put(f"/api/tasks/{tid}", json={"title": ""}).status_code == 200
check("CD-09", "Blank title rejected in web form and API PUT", blank_web or blank_api)

check("CD-10", "done='false' (string) does not mark task done",
      a.put(f"/api/tasks/{tid}", json={"done": "false"}).get_json()["done"] is True)
check("CD-11", "Unknown category_id is rejected",
      a.post("/api/tasks", json={"title": "x", "category_id": 999}).status_code == 201)
check("CD-12", "page=-1 is rejected with 400",
      a.get("/api/tasks?page=-1").status_code == 200)
check("CD-13", "Very long title (5000 chars) is limited",
      a.post("/api/tasks", json={"title": "a" * 5000}).status_code == 201)

# ---- configuration (static observation)
src = open(os.path.join(APP_DIR, "app.py"), encoding="utf-8").read()
check("CD-14", "No hard-coded SECRET_KEY / debug=True",
      'SECRET_KEY"] = "' in src or "debug=True" in src)
check("CD-15", "Forms carry a CSRF token",
      "csrf" not in src.lower())
check("CD-16", "GET /api/categories requires login",
      pytodo.app.test_client().get("/api/categories").status_code == 200)
r = a.post("/api/tasks", data="not json", content_type="text/plain")
check("CD-17", "Non-JSON body gets a clear 400/415 message",
      r.status_code == 400 and "title" in (r.get_json() or {}).get("error", ""))

print(f"\n{sum(v for *_, v in results)} of {len(results)} candidates confirmed.")
