"""
Week 1 - Black-box tests executed through the WEB FORMS (HTTP level).

Techniques: Equivalence Partitioning, Boundary Value Analysis (3-value),
Decision tables and State transitions. Expected results come from the README
and the helpers.py specification, written BEFORE execution.

Each test name / parameter id carries its Test Case ID (TC-BB-xxx) so results
can be traced back to the master test repository and the RTM.
"""

import re

import pytest

from conftest import VALID_PASSWORD, day

pytestmark = pytest.mark.blackbox


# ----------------------------------------------------------------- helpers
def register(c, username, password=VALID_PASSWORD):
    return c.post("/register", data={"username": username, "password": password})


def login(c, username, password=VALID_PASSWORD):
    return c.post("/login", data={"username": username, "password": password})


def new_task(c, title="Task", category_id="", due_date=""):
    return c.post("/tasks/new", data={"title": title, "description": "",
                                      "category_id": category_id, "due_date": due_date})


def page(c, url="/"):
    r = c.get(url)
    return r.status_code, r.get_data(as_text=True)


def badge_for(html, title):
    """Return the urgency badge text in the table row that contains `title`."""
    for row in re.findall(r"<tr.*?</tr>", html, flags=re.S):
        if title in row:
            m = re.search(r'class="badge[^"]*">([^<]+)</span>', row)
            return m.group(1).strip() if m else None
    return None


def accepted(resp):
    return resp.status_code == 302 and resp.headers["Location"].endswith("/")


@pytest.fixture
def web_user(client):
    assert accepted(register(client, "qa_user1"))
    return client


def ids_of(c):
    return [t["id"] for t in c.get("/api/tasks?per_page=100").get_json()]


# ------------------------------------------- F01 username: 3-value BVA + EP
@pytest.mark.parametrize("username,should_accept", [
    pytest.param("ab", False, id="TC-BB-001"),
    pytest.param("abc", True, id="TC-BB-002"),
    pytest.param("abcd", True, id="TC-BB-003"),
    pytest.param("u" * 19, True, id="TC-BB-004"),
    pytest.param("u" * 20, True, id="TC-BB-005"),
    pytest.param("u" * 21, False, id="TC-BB-006"),
    pytest.param("qa user!", False, id="TC-BB-007"),
    pytest.param("qa_user_01", True, id="TC-BB-008"),
])
def test_username_rules(client, username, should_accept):
    r = register(client, username)
    if should_accept:
        assert accepted(r), f"Actual: registration refused (HTTP {r.status_code})"
    else:
        assert not accepted(r) and "Username must be 3-20" in r.get_data(as_text=True), \
            "Actual: account was created"


# ------------------------------------------- F01 password: 3-value BVA + EP
@pytest.mark.regression
@pytest.mark.parametrize("password,should_accept", [
    pytest.param("abcdefg", False, id="TC-BB-009"),
    pytest.param("abcdefgh", True, id="TC-BB-010"),
    pytest.param("abcdefghi", True, id="TC-BB-011"),
    pytest.param("", False, id="TC-BB-012"),
])
def test_password_rules(client, password, should_accept):
    r = register(client, f"pw_user{len(password)}", password)
    if should_accept:
        assert accepted(r), (f"Actual: {len(password)}-character password refused with "
                             f"'Password must be at least 8 characters.'")
    else:
        assert not accepted(r) and "Password must be at least 8" in r.get_data(as_text=True)


# ------------------------------------------- F01 registration decision table
def test_TC_BB_013_dt_r1_all_valid(client):
    r = register(client, "dt_new")
    assert accepted(r)
    status, html = page(client)
    assert status == 200 and "dt_new" in html


@pytest.mark.regression
def test_TC_BB_014_dt_r2_username_taken(client):
    register(client, "dt_taken")
    client.get("/logout")
    r = register(client, "dt_taken", "Another123")
    assert not accepted(r), "Actual: duplicate username 'dt_taken' was registered again (HTTP 302 to /)"


def test_TC_BB_015_dt_r3_bad_password(client):
    r = register(client, "dt_pw", "short")
    assert "Password must be at least 8" in r.get_data(as_text=True)


def test_TC_BB_016_dt_r4_bad_username(client):
    r = register(client, "x")
    assert "Username must be 3-20" in r.get_data(as_text=True)


# ------------------------------------------- F02 login decision table
def test_TC_BB_017_login_r1_valid(client):
    register(client, "qa_user1"); client.get("/logout")
    r = login(client, "qa_user1")
    assert accepted(r)
    assert "qa_user1" in page(client)[1]


def test_TC_BB_018_login_r2_wrong_password(client):
    register(client, "qa_user1"); client.get("/logout")
    r = login(client, "qa_user1", "WrongPass1")
    assert "Invalid username or password." in r.get_data(as_text=True)


def test_TC_BB_019_login_r3_unknown_user(client):
    r = login(client, "ghost_user")
    assert "Invalid username or password." in r.get_data(as_text=True)


def test_TC_BB_020_second_duplicate_account_login(client):
    register(client, "dup_user", "FirstPass1"); client.get("/logout")
    second = register(client, "dup_user", "SecondPass2"); client.get("/logout")
    if not accepted(second):
        return  # duplicate correctly refused: rule satisfied
    r = login(client, "dup_user", "SecondPass2")
    assert accepted(r), ("Actual: second 'dup_user' account was created but cannot log in "
                         "('Invalid username or password.')")


# ------------------------------------------- F04 create task EP
def test_TC_BB_021_create_all_fields(web_user):
    new_task(web_user, "Prepare STQA slides", category_id="3", due_date=day(5))  # 3 = Study
    _, html = page(web_user)
    assert "Prepare STQA slides" in html and "Study" in html
    assert badge_for(html, "Prepare STQA slides") == "Upcoming"


def test_TC_BB_022_create_title_only(web_user):
    new_task(web_user, "Call mum")
    _, html = page(web_user)
    assert badge_for(html, "Call mum") == "No due date"


@pytest.mark.regression
def test_TC_BB_023_whitespace_title_rejected(web_user):
    before = len(ids_of(web_user))
    new_task(web_user, "   ")
    after = len(ids_of(web_user))
    assert after == before, "Actual: task with an empty title was created (blank row in My Tasks)"


@pytest.mark.regression
def test_TC_BB_024_special_characters_shown(web_user):
    new_task(web_user, "Buy milk & eggs <urgent>")
    _, html = page(web_user)
    assert "Buy milk &amp; eggs &lt;urgent&gt;" in html, \
        "Actual: title inserted as raw HTML; '<urgent>' becomes an HTML tag and is not shown"


# ------------------------------------------- F10 urgency: 3-value BVA + EP
@pytest.mark.regression
@pytest.mark.parametrize("offset,expected", [
    pytest.param(-1, "Overdue", id="TC-BB-025"),
    pytest.param(0, "Due Today", id="TC-BB-026"),
    pytest.param(1, "Due Soon", id="TC-BB-027"),
    pytest.param(2, "Due Soon", id="TC-BB-028"),
    pytest.param(3, "Upcoming", id="TC-BB-029"),
])
def test_urgency_bva(web_user, offset, expected):
    title = f"Urgency check {offset}"
    new_task(web_user, title, due_date=day(offset))
    actual = badge_for(page(web_user)[1], title)
    assert actual == expected, f"Actual: badge '{actual}'"


def test_TC_BB_030_no_due_date(web_user):
    new_task(web_user, "No date task")
    assert badge_for(page(web_user)[1], "No date task") == "No due date"


def test_TC_BB_031_done_task_shows_done(web_user):
    new_task(web_user, "Old task", due_date=day(-3))
    tid = ids_of(web_user)[0]
    web_user.post(f"/tasks/{tid}/toggle")
    assert badge_for(page(web_user)[1], "Old task") == "Done"


# ------------------------------------------- F07/F08 state transitions
def test_TC_BB_032_open_to_done(web_user):
    new_task(web_user, "Toggle me")
    tid = ids_of(web_user)[0]
    web_user.post(f"/tasks/{tid}/toggle")
    t = web_user.get(f"/api/tasks/{tid}").get_json()
    assert t["done"] is True and t["completed_at"]


def test_TC_BB_033_done_to_open(web_user):
    new_task(web_user, "Toggle twice", due_date=day(1))
    tid = ids_of(web_user)[0]
    web_user.post(f"/tasks/{tid}/toggle"); web_user.post(f"/tasks/{tid}/toggle")
    t = web_user.get(f"/api/tasks/{tid}").get_json()
    assert t["done"] is False and t["completed_at"] is None and t["urgency"] == "Due Soon"


def test_TC_BB_034_open_to_deleted(web_user):
    new_task(web_user, "Delete me")
    tid = ids_of(web_user)[0]
    web_user.post(f"/tasks/{tid}/delete")
    assert "Delete me" not in page(web_user)[1]


def test_TC_BB_035_toggle_deleted_task(web_user):
    new_task(web_user, "Gone")
    tid = ids_of(web_user)[0]
    web_user.post(f"/tasks/{tid}/delete")
    r = web_user.post(f"/tasks/{tid}/toggle")
    assert r.status_code == 302 and page(web_user)[0] == 200


def test_TC_BB_036_edit_deleted_task(web_user):
    new_task(web_user, "Gone too")
    tid = ids_of(web_user)[0]
    web_user.post(f"/tasks/{tid}/delete")
    r = web_user.get(f"/tasks/{tid}/edit")
    assert r.status_code == 302 and r.headers["Location"].endswith("/")


@pytest.mark.regression
def test_TC_BB_037_logged_out_redirect(client):
    r = client.get("/")
    assert r.status_code == 302 and "/login" in r.headers["Location"]


def test_TC_BB_038_logout_then_dashboard(web_user):
    web_user.get("/logout")
    r = web_user.get("/dashboard")
    assert r.status_code == 302 and "/login" in r.headers["Location"]


# ------------------------------------------- F09 filters and search (EP)
def _cat_ids(c):
    return {x["name"]: x["id"] for x in c.get("/api/categories").get_json()}


def test_TC_BB_039_category_filter(web_user):
    cats = _cat_ids(web_user)
    new_task(web_user, "Work item", category_id=str(cats["Work"]))
    new_task(web_user, "Home item", category_id=str(cats["Personal"]))
    _, html = page(web_user, "/?category=Work")
    assert "Work item" in html and "Home item" not in html


def test_TC_BB_040_status_filter(web_user):
    new_task(web_user, "Still open"); new_task(web_user, "Finished")
    web_user.post(f"/tasks/{ids_of(web_user)[0]}/toggle")
    _, html = page(web_user, "/?status=done")
    assert "Finished" in html and "Still open" not in html


def test_TC_BB_041_search_partial_case_insensitive(web_user):
    new_task(web_user, "Buy milk")
    _, html = page(web_user, "/?q=MILK")
    assert "Buy milk" in html


def test_TC_BB_042_search_no_match(web_user):
    new_task(web_user, "Buy milk")
    _, html = page(web_user, "/?q=zzzz")
    assert "No tasks match your filters." in html


def test_TC_BB_043_combined_filters(web_user):
    cats = _cat_ids(web_user)
    new_task(web_user, "Monthly report", category_id=str(cats["Work"]))
    new_task(web_user, "Closed report", category_id=str(cats["Work"]))
    web_user.post(f"/tasks/{ids_of(web_user)[0]}/toggle")
    new_task(web_user, "Personal report", category_id=str(cats["Personal"]))
    _, html = page(web_user, "/?category=Work&status=open&q=report")
    assert "Monthly report" in html and "Closed report" not in html and "Personal report" not in html


def test_TC_BB_044_web_search_apostrophe(web_user):
    new_task(web_user, "Mum's birthday")
    status, html = page(web_user, "/?q=mum's")
    assert status == 200 and "Mum" in html


# ------------------------------------------- F11 dashboard
def _stat(html, label):
    m = re.search(r'stat-value">(\d+)</div>\s*<div class="stat-label">' + re.escape(label), html)
    return int(m.group(1)) if m else None


def test_TC_BB_045_dashboard_counts(web_user):
    new_task(web_user, "Late", due_date=day(-2))
    new_task(web_user, "Soon", due_date=day(1))
    new_task(web_user, "Later", due_date=day(6))
    new_task(web_user, "Finished now")
    web_user.post(f"/tasks/{ids_of(web_user)[0]}/toggle")
    _, html = page(web_user, "/dashboard")
    got = {k: _stat(html, k) for k in ["Total Tasks", "Open", "Overdue", "Due Soon", "Completed (last 7 days)"]}
    assert got == {"Total Tasks": 4, "Open": 3, "Overdue": 1, "Due Soon": 1, "Completed (last 7 days)": 1}, f"Actual: {got}"


@pytest.mark.regression
def test_TC_BB_046_due_today_not_overdue(web_user):
    new_task(web_user, "Due today", due_date=day(0))
    _, html = page(web_user, "/dashboard")
    assert _stat(html, "Overdue") == 0, f"Actual: Overdue = {_stat(html, 'Overdue')}"


# ------------------------------------------- F06 edit
def test_TC_BB_047_edit_valid(web_user):
    new_task(web_user, "Original")
    tid = ids_of(web_user)[0]
    web_user.post(f"/tasks/{tid}/edit", data={"title": "Edited title", "description": "",
                                             "category_id": "", "due_date": day(10)})
    html = page(web_user)[1]
    assert "Edited title" in html and badge_for(html, "Edited title") == "Upcoming"


def test_TC_BB_048_edit_whitespace_title(web_user):
    new_task(web_user, "Keep me")
    tid = ids_of(web_user)[0]
    web_user.post(f"/tasks/{tid}/edit", data={"title": "   ", "description": "", "category_id": "", "due_date": ""})
    t = web_user.get(f"/api/tasks/{tid}").get_json()
    assert t["title"] == "Keep me", f"Actual: title changed to '{t['title']}' (empty)"


@pytest.mark.regression
def test_TC_BB_049_invalid_date_from_form(web_user):
    new_task(web_user, "Bad date", due_date="2026-13-45")
    status, _ = page(web_user)
    assert status == 200, f"Actual: task was saved and My Tasks now returns HTTP {status} (Internal Server Error)"
