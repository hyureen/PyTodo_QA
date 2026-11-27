"""
Week 2 - White-box (structural) unit tests.

Units selected (see report Section 3 for the reasons):
  helpers.compute_urgency           V(G) = 5
  helpers.is_valid_password         V(G) = 3
  helpers.is_valid_username         V(G) = 4
  helpers.completed_in_last_n_days  V(G) = 4
  app.api_update_task (completed_at decision)

Tests are designed from the control flow graph (basis paths) and decision
boundaries, so that together they reach 100% statement and branch coverage
of helpers.py. Dates are injected (today / now) so results never depend on
the day the suite runs.
"""

from datetime import date, datetime, timedelta

import pytest

from conftest import create_task
from helpers import (completed_in_last_n_days, compute_urgency,
                     is_valid_password, is_valid_username)

TODAY = date(2026, 11, 21)
NOW = datetime(2026, 11, 21, 12, 0, 0)


def d(offset):
    return (TODAY + timedelta(days=offset)).isoformat()


def ts(delta):
    return (NOW - delta).strftime("%Y-%m-%d %H:%M:%S")


# ----------------------------------------------------- compute_urgency
@pytest.mark.unit
@pytest.mark.regression
@pytest.mark.parametrize("due,expected", [
    pytest.param(None, "No due date", id="TC-WB-001"),
    pytest.param(d(-1), "Overdue", id="TC-WB-003"),
    pytest.param(d(0), "Due Today", id="TC-WB-004"),
    pytest.param(d(1), "Due Soon", id="TC-WB-005"),
    pytest.param(d(2), "Due Soon", id="TC-WB-006"),
    pytest.param(d(3), "Upcoming", id="TC-WB-007"),
])
def test_compute_urgency_paths(due, expected):
    actual = compute_urgency(due, today=TODAY)
    assert actual == expected, f"Actual: '{actual}'"


@pytest.mark.unit
def test_TC_WB_002_today_defaults_to_system_date():
    far = (date.today() + timedelta(days=30)).isoformat()
    assert compute_urgency(far) == "Upcoming"


@pytest.mark.unit
def test_TC_WB_008_bad_format_raises():
    with pytest.raises(ValueError):
        compute_urgency("21/11/2026", today=TODAY)


# ----------------------------------------------------- is_valid_password
@pytest.mark.unit
@pytest.mark.regression
@pytest.mark.parametrize("pw,expected", [
    pytest.param(None, False, id="TC-WB-009"),
    pytest.param("abcdefgh", True, id="TC-WB-010"),
    pytest.param("abcdefghi", True, id="TC-WB-011"),
    pytest.param("abcdefg", False, id="TC-WB-012"),
])
def test_is_valid_password(pw, expected):
    actual = is_valid_password(pw)
    assert actual is expected, f"Actual: {actual}"


# ----------------------------------------------------- is_valid_username
@pytest.mark.unit
@pytest.mark.parametrize("name,expected", [
    pytest.param(12345, False, id="TC-WB-013"),
    pytest.param("ab", False, id="TC-WB-014"),
    pytest.param("u" * 21, False, id="TC-WB-015"),
    pytest.param("qa_user_1", True, id="TC-WB-016"),
    pytest.param("qa-user", False, id="TC-WB-017"),
    pytest.param("abc def", False, id="TC-WB-018"),
])
def test_is_valid_username(name, expected):
    assert is_valid_username(name) is expected


# ----------------------------------------------------- completed_in_last_n_days
@pytest.mark.unit
@pytest.mark.regression
@pytest.mark.parametrize("completed,expected", [
    pytest.param(None, False, id="TC-WB-019"),
    pytest.param(ts(timedelta(hours=1)), True, id="TC-WB-020"),
    pytest.param(ts(timedelta(days=7)), True, id="TC-WB-021"),
    pytest.param(ts(timedelta(days=8)), False, id="TC-WB-022"),
    pytest.param(ts(timedelta(hours=-1)), False, id="TC-WB-023"),
    pytest.param(ts(timedelta(days=6, hours=23)), True, id="TC-WB-025"),
])
def test_completed_in_last_n_days(completed, expected):
    actual = completed_in_last_n_days(completed, n=7, now=NOW)
    assert actual is expected, f"Actual: {actual}"


@pytest.mark.unit
def test_TC_WB_024_now_defaults_to_system_time():
    one_min_ago = (datetime.now() - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S")
    assert completed_in_last_n_days(one_min_ago) is True


# ----------------------------------------------------- app.api_update_task decisions
@pytest.mark.unit
def test_TC_WB_026_done_sets_completed_at(user_a):
    tid = create_task(user_a).get_json()["id"]
    t = user_a.put(f"/api/tasks/{tid}", json={"done": True}).get_json()
    assert t["done"] is True and t["completed_at"]


@pytest.mark.unit
def test_TC_WB_027_done_again_keeps_completed_at(user_a):
    tid = create_task(user_a).get_json()["id"]
    first = user_a.put(f"/api/tasks/{tid}", json={"done": True}).get_json()["completed_at"]
    second = user_a.put(f"/api/tasks/{tid}", json={"done": True}).get_json()["completed_at"]
    assert first == second


@pytest.mark.unit
def test_TC_WB_028_reopen_clears_completed_at(user_a):
    tid = create_task(user_a).get_json()["id"]
    user_a.put(f"/api/tasks/{tid}", json={"done": True})
    t = user_a.put(f"/api/tasks/{tid}", json={"done": False}).get_json()
    assert t["done"] is False and t["completed_at"] is None


@pytest.mark.unit
def test_TC_WB_029_other_field_keeps_done_state(user_a):
    tid = create_task(user_a).get_json()["id"]
    done_at = user_a.put(f"/api/tasks/{tid}", json={"done": True}).get_json()["completed_at"]
    t = user_a.put(f"/api/tasks/{tid}", json={"title": "New"}).get_json()
    assert t["done"] is True and t["completed_at"] == done_at
