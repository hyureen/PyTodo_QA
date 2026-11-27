"""
Week 3 - GUI, configuration (screen size) and accessibility evidence collector.

What it does (app must be running on http://127.0.0.1:5000):
  1. Takes screenshots of every page at 3 screen sizes (desktop / tablet / phone).
  2. Runs the Axe accessibility engine (WCAG 2.1 A + AA rules) on every page.
  3. Checks keyboard (Tab) order on the login form and whether focus is visible.
  4. Checks if a server error shows the debugger/traceback (TC-SEC-013).
Results are written to 03_Special_Testing/audit_results.json and screenshots/.

Usage:  python 03_Special_Testing/gui_a11y_audit.py path/to/axe.min.js
        (axe.min.js comes from: npm install axe-core)
"""

import json
import os
import sys
import urllib.request
import uuid
from datetime import date

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE = "http://127.0.0.1:5000"
HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots")
AXE = open(sys.argv[1], encoding="utf-8").read()
SIZES = {"desktop_1366x768": (1366, 768), "tablet_768x1024": (768, 1024), "phone_375x812": (375, 812)}
os.makedirs(SHOTS, exist_ok=True)

opts = webdriver.ChromeOptions()
opts.add_argument("--headless=new")
opts.add_argument("--no-sandbox")
d = webdriver.Chrome(options=opts)
results = {"browser": d.capabilities["browserName"] + " " + d.capabilities["browserVersion"],
           "date": date.today().isoformat(), "pages": {}, "keyboard": {}, "error_page": {}}


def click_and_wait(selector):
    old = d.find_element(By.TAG_NAME, "html")
    d.find_element(By.CSS_SELECTOR, selector).click()
    WebDriverWait(d, 5).until(EC.staleness_of(old))


def run_axe():
    d.execute_script(AXE)
    res = d.execute_async_script(
        "const cb = arguments[arguments.length-1];"
        "axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a','wcag2aa','wcag21a','wcag21aa']}})"
        ".then(r => cb({violations: r.violations.map(v => ({id: v.id, impact: v.impact, help: v.help,"
        " wcag: v.tags.filter(t => t.startsWith('wcag') && /\\d/.test(t)), nodes: v.nodes.length,"
        " examples: v.nodes.slice(0,3).map(n => n.target.join(' '))})), passes: r.passes.length}))")
    return res


def capture(name, path, setup=None):
    d.set_window_size(1366, 768)
    d.get(BASE + path)
    if setup:
        setup()
    entry = {"title": d.title, "lang": d.find_element(By.TAG_NAME, "html").get_attribute("lang")}
    entry["axe"] = run_axe()
    for label, (w, h) in SIZES.items():
        d.set_window_size(w, h)
        d.get(d.current_url) if not setup else None
        overflow = d.execute_script("return document.documentElement.scrollWidth > window.innerWidth")
        entry.setdefault("horizontal_scroll", {})[label] = overflow
        d.save_screenshot(os.path.join(SHOTS, f"{name}_{label}.png"))
    results["pages"][name] = entry


# ---------- logged-out pages
d.get(BASE + "/logout")
capture("01_login", "/login")
capture("02_register", "/register")


def register_error():
    d.find_element(By.NAME, "username").send_keys("ab")
    d.find_element(By.NAME, "password").send_keys("Passw0rd123")
    click_and_wait("button[type=submit]")


capture("03_register_error", "/register", register_error)

# ---------- keyboard order on login form
d.set_window_size(1366, 768)
d.get(BASE + "/login")
body = d.find_element(By.TAG_NAME, "body")
order = []
for _ in range(7):
    body = d.switch_to.active_element
    body.send_keys(Keys.TAB)
    el = d.switch_to.active_element
    order.append((el.tag_name, el.get_attribute("name") or el.text.strip()[:20],
                  el.value_of_css_property("outline-style")))
results["keyboard"]["login_tab_order"] = order

# ---------- logged-in pages with sample data
user = "audit_" + uuid.uuid4().hex[:6]
d.get(BASE + "/register")
d.find_element(By.NAME, "username").send_keys(user)
d.find_element(By.NAME, "password").send_keys("Passw0rd123")
click_and_wait("button[type=submit]")
for title, offset in [("Finish STQA report", 6), ("Group meeting", 1), ("Pay hostel fee", -2), ("Submit lab", 0)]:
    d.get(BASE + "/tasks/new")
    d.find_element(By.NAME, "title").send_keys(title)
    el = d.find_element(By.NAME, "due_date")
    d.execute_script("arguments[0].value = arguments[1];", el,
                     date.fromordinal(date.today().toordinal() + offset).isoformat())
    click_and_wait("form.task-form button[type=submit]")
capture("04_task_list", "/")
capture("05_new_task_form", "/tasks/new")
capture("06_dashboard", "/dashboard")
capture("07_empty_search", "/?q=zzzz")

# ---------- TC-SEC-013: what does a server error show? (uses its own user)
d.get(BASE + "/logout")
d.get(BASE + "/register")
d.find_element(By.NAME, "username").send_keys("err_" + uuid.uuid4().hex[:6])
d.find_element(By.NAME, "password").send_keys("Passw0rd123")
click_and_wait("button[type=submit]")
cookie = d.get_cookie("session")["value"]
req = urllib.request.Request(BASE + "/tasks/new", data=b"title=Bad+date&due_date=2026-13-45",
                             headers={"Cookie": f"session={cookie}",
                                      "Content-Type": "application/x-www-form-urlencoded"})
try:
    urllib.request.urlopen(req)
except Exception:
    pass
d.set_window_size(1366, 768)
d.get(BASE + "/")
src = d.page_source
results["error_page"] = {"shows_traceback": "Traceback" in src, "shows_werkzeug_debugger": "Werkzeug Debugger" in src
                         or "debugger" in src.lower(), "title": d.title}
d.save_screenshot(os.path.join(SHOTS, "08_server_error_debugger.png"))
d.quit()

with open(os.path.join(HERE, "audit_results.json"), "w") as f:
    json.dump(results, f, indent=2)
print(json.dumps({k: (v if k != "pages" else {p: [x["id"] for x in e["axe"]["violations"]] for p, e in v.items()})
                  for k, v in results.items()}, indent=1))
