"""
Week 6 - Selenium UI automation (top of the test pyramid: few, critical flows).

Needs the app running first:   cd app && python app.py
Run:                           pytest 06_Automation_Regression -m ui -v
Other browsers (Windows CMD):  set BROWSER=edge     then the same pytest command
                               set BROWSER=firefox
Watch the browser:             set HEADED=1

Each automated test (AT-xxx) is mapped to the manual test case it automates
(see 07_Test_Management/PyTodo_Test_Management.xlsx, sheet 'Automation Map').
Screenshots are saved to 06_Automation_Regression/evidence/.
"""

import os
import urllib.request
import uuid
from datetime import date, timedelta

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

from pages import BASE, DashboardPage, LoginPage, RegisterPage, TaskFormPage, TaskListPage

pytestmark = pytest.mark.ui
# Choose the browser with the BROWSER environment variable: chrome (default), edge, firefox, safari
BROWSER = os.environ.get("BROWSER", "chrome").lower()
_BASE_EVIDENCE = os.path.join(os.path.dirname(__file__), "evidence")
EVIDENCE = _BASE_EVIDENCE if BROWSER == "chrome" else os.path.join(_BASE_EVIDENCE, BROWSER)
PASSWORD = "Passw0rd123"


def server_up():
    try:
        urllib.request.urlopen(BASE + "/login", timeout=2)
        return True
    except Exception:
        return False


@pytest.fixture(scope="module")
def driver():
    if not server_up():
        pytest.skip("PyTodo Pro is not running on http://127.0.0.1:5000")
    headed = os.environ.get("HEADED") == "1"
    if BROWSER == "firefox":
        opts = webdriver.FirefoxOptions()
        if not headed:
            opts.add_argument("-headless")
        d = webdriver.Firefox(options=opts)
    elif BROWSER == "edge":
        opts = webdriver.EdgeOptions()
        if not headed:
            opts.add_argument("--headless=new")
        d = webdriver.Edge(options=opts)
    elif BROWSER == "safari":
        d = webdriver.Safari()          # macOS: run 'safaridriver --enable' once first
    else:
        opts = webdriver.ChromeOptions()
        if not headed:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        d = webdriver.Chrome(options=opts)
    d.set_window_size(1366, 900)
    os.makedirs(EVIDENCE, exist_ok=True)
    print(f"\nBrowser under test: {d.capabilities.get('browserName')} {d.capabilities.get('browserVersion')}")
    yield d
    d.quit()


@pytest.fixture
def fresh_user(driver):
    """Register a unique user so tests never clash (the live DB is shared)."""
    for attempt in range(3):                       # retry: avoids rare browser timing glitches
        try:
            driver.get("about:blank")
            driver.delete_all_cookies()
            name = "ui_" + uuid.uuid4().hex[:8]
            RegisterPage(driver).open().submit(name, PASSWORD)
            return name
        except Exception:
            if attempt == 2:
                raise


def iso(offset):
    return (date.today() + timedelta(days=offset)).isoformat()


def snap(driver, name):
    driver.save_screenshot(os.path.join(EVIDENCE, name))


# AT-001 -> TC-BB-002 / TC-BB-013
@pytest.mark.regression
def test_AT_001_register_lands_on_tasks(driver, fresh_user):
    assert TaskListPage(driver).heading() == "My Tasks"
    assert fresh_user in driver.find_element(By.CSS_SELECTOR, ".nav-user").text
    snap(driver, "AT-001_register_ok.png")


# AT-002 -> TC-BB-010 (DEF-002)
@pytest.mark.regression
def test_AT_002_eight_char_password(driver):
    driver.delete_all_cookies()
    page = RegisterPage(driver).open()
    page.submit("ui_" + uuid.uuid4().hex[:8], "abcdefgh")
    snap(driver, "AT-002_password_8_chars.png")
    assert page.heading() == "My Tasks", f"Actual: stayed on register page, message '{page.error()}'"


# AT-003 -> TC-BB-017 / TC-BB-038
@pytest.mark.regression
def test_AT_003_login_logout(driver, fresh_user):
    TaskListPage(driver).logout()
    LoginPage(driver).open().submit(fresh_user, PASSWORD)
    assert TaskListPage(driver).heading() == "My Tasks"
    TaskListPage(driver).logout()
    driver.get(BASE + "/dashboard")
    assert "/login" in driver.current_url


# AT-004 -> TC-BB-026 (DEF-001)
@pytest.mark.regression
def test_AT_004_due_today_badge(driver, fresh_user):
    page = TaskListPage(driver)
    page.new_task("Submit lab report", due_iso=iso(0))
    snap(driver, "AT-004_due_today_badge.png")
    assert page.badge("Submit lab report") == "Due Today", f"Actual: '{page.badge('Submit lab report')}'"


# AT-005 -> TC-BB-032 / TC-BB-033
@pytest.mark.regression
def test_AT_005_complete_and_reopen(driver, fresh_user):
    page = TaskListPage(driver)
    page.new_task("Read chapter 5", due_iso=iso(1))
    page.toggle("Read chapter 5")
    assert page.badge("Read chapter 5") == "Done"
    page.toggle("Read chapter 5")
    assert page.badge("Read chapter 5") == "Due Soon"


# AT-006 -> TC-BB-034
def test_AT_006_delete_with_confirm(driver, fresh_user):
    page = TaskListPage(driver)
    page.new_task("Temporary task")
    page.delete("Temporary task")
    assert page.row("Temporary task") is None


# AT-007 -> TC-BB-039
def test_AT_007_category_filter(driver, fresh_user):
    page = TaskListPage(driver)
    page.new_task("Team meeting", category="Work")
    page.new_task("Gym", category="Personal")
    page.filter_category("Work")
    titles = [r.text for r in page.rows()]
    assert any("Team meeting" in t for t in titles) and not any("Gym" in t for t in titles)


# AT-008 -> TC-BB-024 / TC-SEC-012 (DEF-007) - harmless markup only
@pytest.mark.regression
def test_AT_008_title_markup_not_rendered(driver, fresh_user):
    page = TaskListPage(driver)
    page.new_task('<b id="xss-probe">Bold title</b>')
    snap(driver, "AT-008_html_in_title.png")
    rendered = driver.find_elements(By.ID, "xss-probe")
    assert not rendered, "Actual: the <b> tag in the title was rendered as real HTML"


# AT-009 -> TC-BB-045
def test_AT_009_dashboard_counts(driver, fresh_user):
    page = TaskListPage(driver)
    page.new_task("Late", due_iso=iso(-2))
    page.new_task("Soon", due_iso=iso(1))
    page.new_task("Later", due_iso=iso(6))
    page.new_task("Finished")
    page.toggle("Finished")
    dash = DashboardPage(driver).open()
    snap(driver, "AT-009_dashboard.png")
    assert dash.stats() == {"Total Tasks": 4, "Open": 3, "Overdue": 1, "Due Soon": 1, "Completed (last 7 days)": 1}


# AT-010 -> client-side check for TC-BB-023 (browser 'required')
def test_AT_010_empty_title_blocked_in_browser(driver, fresh_user):
    driver.find_element(By.LINK_TEXT, "+ New Task").click()
    TaskFormPage(driver).save()                    # title left empty
    valid = driver.execute_script("return document.querySelector('[name=title]').checkValidity()")
    assert driver.current_url.endswith("/tasks/new") and valid is False
