"""
Week 4 - REST API tests (functional, negative, security-at-API-level).

Run against the Flask test client: no server or Postman needed, and every test
starts from an empty database. Status codes are checked against the expected
values from the lecture (200, 201, 400, 401, 403, 404, 500).

A 500 Internal Server Error on bad input is always a failure: the server must
reject bad input with a 4xx code.
"""

import pytest

from conftest import VALID_PASSWORD, create_task, day, make_user

pytestmark = pytest.mark.api


def status_msg(r):
    body = r.get_json(silent=True)
    return f"Actual: HTTP {r.status_code}, body {body if body is not None else r.get_data(as_text=True)[:60]!r}"


# ------------------------------------------------------------------ F01 register
def test_TC_API_001_register_valid(client):
    r = client.post("/api/register", json={"username": "api_user", "password": VALID_PASSWORD})
    assert r.status_code == 201 and r.get_json()["username"] == "api_user" and "id" in r.get_json()


def test_TC_API_002_register_invalid_username(client):
    r = client.post("/api/register", json={"username": "a!", "password": VALID_PASSWORD})
    assert r.status_code == 400 and r.get_json()["error"] == "invalid username"


def test_TC_API_003_register_password_7(client):
    r = client.post("/api/register", json={"username": "api_user", "password": "abcdefg"})
    assert r.status_code == 400 and r.get_json()["error"] == "invalid password"


def test_TC_API_004_register_no_body(client):
    assert client.post("/api/register").status_code == 400


@pytest.mark.regression
def test_TC_API_005_register_duplicate(client):
    client.post("/api/register", json={"username": "api_dup", "password": VALID_PASSWORD})
    r = client.post("/api/register", json={"username": "api_dup", "password": "Another123"})
    assert r.status_code in (400, 409), status_msg(r)


def test_TC_API_006_register_wrong_type(client):
    r = client.post("/api/register", json={"username": 12345, "password": VALID_PASSWORD})
    assert r.status_code == 400, status_msg(r)


# ------------------------------------------------------------------ F02 login
def test_TC_API_007_login_valid(fresh_app):
    make_user(fresh_app, "qa_user1")
    r = fresh_app.app.test_client().post("/api/login", json={"username": "qa_user1", "password": VALID_PASSWORD})
    assert r.status_code == 200 and r.get_json()["username"] == "qa_user1"


def test_TC_API_008_login_wrong_password(fresh_app):
    make_user(fresh_app, "qa_user1")
    r = fresh_app.app.test_client().post("/api/login", json={"username": "qa_user1", "password": "wrong"})
    assert r.status_code == 401 and r.get_json()["error"] == "invalid credentials"


def test_TC_API_009_login_unknown(client):
    assert client.post("/api/login", json={"username": "nobody", "password": VALID_PASSWORD}).status_code == 401


# ------------------------------------------------------------------ F03 / F12
@pytest.mark.regression
def test_TC_API_010_tasks_need_login(client):
    r = client.get("/api/tasks")
    assert r.status_code == 401 and r.get_json()["error"] == "authentication required"


def test_TC_API_011_categories_need_login(client):
    r = client.get("/api/categories")
    assert r.status_code == 401, status_msg(r)


def test_TC_API_012_categories(user_a):
    r = user_a.get("/api/categories")
    assert r.status_code == 200 and [c["name"] for c in r.get_json()] == ["Personal", "Study", "Urgent", "Work"]


# ------------------------------------------------------------------ F04 create
@pytest.mark.regression
def test_TC_API_013_create_full(user_a):
    r = create_task(user_a, title="API task", description="d", category_id=1, due_date=day(5))
    t = r.get_json()
    assert r.status_code == 201
    assert (t["title"], t["category"], t["urgency"], t["done"]) == ("API task", "Work", "Upcoming", False)


def test_TC_API_014_create_missing_title(user_a):
    r = user_a.post("/api/tasks", json={"description": "x"})
    assert r.status_code == 400 and r.get_json()["error"] == "title is required"


def test_TC_API_015_create_whitespace_title(user_a):
    assert user_a.post("/api/tasks", json={"title": "   "}).status_code == 400


def test_TC_API_016_create_number_title(user_a):
    r = user_a.post("/api/tasks", json={"title": 123})
    assert r.status_code in (201, 400), status_msg(r)


@pytest.mark.regression
@pytest.mark.parametrize("bad", [pytest.param("2026-02-30", id="TC-API-017"),
                                 pytest.param("21/11/2026", id="TC-API-018")])
def test_create_invalid_date(user_a, bad):
    r = create_task(user_a, title="x", due_date=bad)
    assert r.status_code == 400, status_msg(r)
    assert user_a.get("/api/tasks").status_code == 200


def test_TC_API_019_unknown_category(user_a):
    r = create_task(user_a, title="x", category_id=999)
    assert r.status_code == 400, status_msg(r)


def test_TC_API_020_non_json_body(user_a):
    r = user_a.post("/api/tasks", data="not json", content_type="text/plain")
    assert r.status_code in (400, 415) and "json" in str(r.get_json()).lower(), status_msg(r)


def test_TC_API_021_very_long_title(user_a):
    r = create_task(user_a, title="a" * 5000)
    assert r.status_code == 400, status_msg(r) + f" (title of 5,000 characters stored)"


# ------------------------------------------------------------------ F05 get / list
def test_TC_API_022_get_own(user_a):
    tid = create_task(user_a, title="Mine").get_json()["id"]
    r = user_a.get(f"/api/tasks/{tid}")
    assert r.status_code == 200 and r.get_json()["title"] == "Mine"


def test_TC_API_023_get_unknown(user_a):
    r = user_a.get("/api/tasks/99999")
    assert r.status_code == 404 and r.get_json()["error"] == "not found"


@pytest.mark.regression
def test_TC_API_024_get_other_users_task(user_a, user_b):
    tid = create_task(user_b, title="B private").get_json()["id"]
    assert user_a.get(f"/api/tasks/{tid}").status_code == 404


def test_TC_API_025_default_page(user_a):
    for i in range(12):
        create_task(user_a, title=f"T{i}")
    items = user_a.get("/api/tasks").get_json()
    ids = [t["id"] for t in items]
    assert len(items) == 10 and ids == sorted(ids, reverse=True)


def test_TC_API_026_pages_do_not_overlap(user_a):
    for i in range(5):
        create_task(user_a, title=f"T{i}")
    p0 = {t["id"] for t in user_a.get("/api/tasks?page=0&per_page=2").get_json()}
    p1 = {t["id"] for t in user_a.get("/api/tasks?page=1&per_page=2").get_json()}
    assert len(p0) == 2 and len(p1) == 2 and not (p0 & p1)


@pytest.mark.parametrize("query", [pytest.param("page=-1", id="TC-API-027"),
                                   pytest.param("per_page=0", id="TC-API-028")])
def test_invalid_paging(user_a, query):
    create_task(user_a)
    r = user_a.get(f"/api/tasks?{query}")
    assert r.status_code == 400, status_msg(r)


def test_TC_API_029_page_not_a_number(user_a):
    create_task(user_a)
    assert user_a.get("/api/tasks?page=abc").status_code in (200, 400)


def test_TC_API_030_filter_status(user_a):
    create_task(user_a, title="open one")
    tid = create_task(user_a, title="done one").get_json()["id"]
    user_a.put(f"/api/tasks/{tid}", json={"done": True})
    assert [t["title"] for t in user_a.get("/api/tasks?status=done").get_json()] == ["done one"]


def test_TC_API_031_filter_category(user_a):
    create_task(user_a, title="work one", category_id=1)
    create_task(user_a, title="home one", category_id=2)
    assert [t["title"] for t in user_a.get("/api/tasks?category=Work").get_json()] == ["work one"]


def test_TC_API_032_search(user_a):
    create_task(user_a, title="Buy milk"); create_task(user_a, title="Read book")
    assert [t["title"] for t in user_a.get("/api/tasks?q=milk").get_json()] == ["Buy milk"]


@pytest.mark.regression
def test_TC_API_033_search_apostrophe(user_a):
    create_task(user_a, title="Mum's birthday")
    r = user_a.get("/api/tasks?q=mum's")
    assert r.status_code == 200, status_msg(r)


# ------------------------------------------------------------------ F06 / F07 update
def test_TC_API_034_partial_update(user_a):
    tid = create_task(user_a, title="Old", category_id=3, due_date=day(4)).get_json()["id"]
    t = user_a.put(f"/api/tasks/{tid}", json={"title": "Renamed"}).get_json()
    assert (t["title"], t["category"], t["due_date"]) == ("Renamed", "Study", day(4))


@pytest.mark.regression
def test_TC_API_035_put_empty_title(user_a):
    tid = create_task(user_a, title="Keep").get_json()["id"]
    r = user_a.put(f"/api/tasks/{tid}", json={"title": ""})
    assert r.status_code == 400, status_msg(r)


def test_TC_API_036_done_string_false(user_a):
    tid = create_task(user_a).get_json()["id"]
    r = user_a.put(f"/api/tasks/{tid}", json={"done": "false"})
    assert r.status_code == 400 or r.get_json()["done"] is False, \
        f"Actual: HTTP {r.status_code}, done = {r.get_json()['done']} (task marked complete)"


@pytest.mark.regression
def test_TC_API_037_put_other_users_task(user_a, user_b):
    tid = create_task(user_b, title="B task").get_json()["id"]
    r = user_a.put(f"/api/tasks/{tid}", json={"title": "hacked"})
    assert r.status_code == 404 and user_b.get(f"/api/tasks/{tid}").get_json()["title"] == "B task"


def test_TC_API_038_put_unknown(user_a):
    assert user_a.put("/api/tasks/99999", json={"title": "x"}).status_code == 404


def test_TC_API_039_put_invalid_date(user_a):
    tid = create_task(user_a).get_json()["id"]
    r = user_a.put(f"/api/tasks/{tid}", json={"due_date": "bad"})
    assert r.status_code == 400 and user_a.get(f"/api/tasks/{tid}").status_code == 200, status_msg(r)


# ------------------------------------------------------------------ F08 delete
def test_TC_API_040_delete_own(user_a):
    tid = create_task(user_a).get_json()["id"]
    assert user_a.delete(f"/api/tasks/{tid}").status_code == 200
    assert user_a.get(f"/api/tasks/{tid}").status_code == 404


def test_TC_API_041_delete_unknown(user_a):
    r = user_a.delete("/api/tasks/99999")
    assert r.status_code == 404, status_msg(r)


@pytest.mark.regression
def test_TC_API_042_delete_other_users_task(user_a, user_b):
    tid = create_task(user_b, title="B private").get_json()["id"]
    r = user_a.delete(f"/api/tasks/{tid}")
    still_there = user_b.get(f"/api/tasks/{tid}").status_code == 200
    assert still_there, f"Actual: HTTP {r.status_code} {r.get_json()} and qa_user2's task was deleted"


def test_TC_API_043_delete_needs_login(client):
    assert client.delete("/api/tasks/1").status_code == 401


# ------------------------------------------------------------------ F11 dashboard
def test_TC_API_044_dashboard_counts(user_a):
    create_task(user_a, title="late", due_date=day(-2))
    create_task(user_a, title="soon", due_date=day(1))
    create_task(user_a, title="later", due_date=day(6))
    tid = create_task(user_a, title="finished").get_json()["id"]
    user_a.put(f"/api/tasks/{tid}", json={"done": True})
    assert user_a.get("/api/dashboard").get_json() == {
        "total": 4, "open": 3, "overdue": 1, "due_soon": 1, "completed_this_week": 1}


@pytest.mark.regression
def test_TC_API_045_due_today_not_overdue(user_a):
    create_task(user_a, title="today", due_date=day(0))
    got = user_a.get("/api/dashboard").get_json()
    assert got["overdue"] == 0, f"Actual: {got}"


def test_TC_API_046_dashboard_needs_login(client):
    assert client.get("/api/dashboard").status_code == 401
