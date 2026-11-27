"""
Test case catalogue (part 3): GUI, accessibility, compatibility, performance and
TC-SEC-013. These are checklist/observation tests, so Actual Result and Status
are recorded here from the Week 3/5 evidence (screenshots, audit_results.json,
perf_results/*.csv).
"""

SHOT = "03_Special_Testing/screenshots/"


def m(id, feature, technique, objective, data, steps, expected, actual, status, evidence, defect="", priority="Medium",
      pre="Logged in (where needed); app running at http://127.0.0.1:5000; Chrome 153 headless"):
    return dict(id=id, feature=feature, technique=technique, objective=objective, pre=pre, data=data, steps=steps,
                expected=expected, actual=actual, status=status, evidence=evidence, defect=defect, priority=priority)


GUI = [
    m("TC-GUI-001", "NF3 GUI", "GUI checklist", "Every page has a clear, unique title", "-", "Open each page; read tab title",
      "Titles like 'Log in — PyTodo Pro', 'Tasks — PyTodo Pro'", "All 7 pages have unique, meaningful titles", "Pass",
      "audit_results.json (title)"),
    m("TC-GUI-002", "NF3 GUI", "GUI checklist (navigation)", "Navigation links show only when logged in", "-",
      "Compare top bar logged out vs logged in", "Logged out: brand only. Logged in: Tasks, Dashboard, username, Log out",
      "As expected", "Pass", SHOT + "01_login_desktop_1366x768.png, 04_task_list_desktop_1366x768.png"),
    m("TC-GUI-003", "NF3 GUI", "GUI checklist (navigation)", "Brand link goes to the right page", "-", "Click 'PyTodo Pro'",
      "Logged in: My Tasks. Logged out: Log in", "As expected", "Pass", "Manual check in Chrome"),
    m("TC-GUI-004", "NF3 GUI", "GUI checklist (labels)", "Buttons have clear action words", "-", "Read all buttons",
      "'+ New Task', 'Create Task', 'Save Changes', 'Filter', 'Log in', 'Register'", "As expected", "Pass",
      SHOT + "05_new_task_form_desktop_1366x768.png"),
    m("TC-GUI-005", "NF3 GUI", "GUI checklist (messages)", "Validation error is visible near the form", "username 'ab'",
      "Submit Register with invalid username", "Red error box above the form", "Red box: 'Username must be 3-20 characters...'",
      "Pass", SHOT + "03_register_error_desktop_1366x768.png"),
    m("TC-GUI-006", "NF3 GUI", "GUI checklist (client validation)", "Required fields are enforced by the browser", "empty title",
      "Click Create Task with empty title", "Browser blocks submit and highlights the field", "Blocked by HTML 'required'",
      "Pass", "AT-010 (automated)"),
    m("TC-GUI-007", "NF3 GUI", "GUI checklist (error prevention)", "Delete asks for confirmation", "-", "Click Delete",
      "Confirm dialog 'Delete this task?'", "Dialog shown; Cancel keeps task", "Pass", "AT-006 (automated)"),
    m("TC-GUI-008", "NF3 GUI", "GUI checklist (consistency)", "Each urgency label has its own badge style",
      "tasks due -2, 0, +1, +6, none", "View My Tasks", "Five distinct badges incl. 'Due Today' (style .badge-due-today exists in CSS)",
      "'Due Today' never appears; task due today shows red 'Overdue'", "Fail",
      SHOT + "04_task_list_desktop_1366x768.png; 06_Automation_Regression/evidence/AT-004_due_today_badge.png", "DEF-001",
      "High"),
    m("TC-GUI-009", "NF3 GUI", "GUI checklist (state display)", "Completed tasks look different", "1 done task", "Complete a task",
      "Strike-through title, ✓ icon, grey 'Done' badge", "As expected", "Pass", "AT-005 (automated)"),
    m("TC-GUI-010", "NF3 GUI", "GUI checklist (empty state)", "Empty result shows a helpful message", "q=zzzz", "Search",
      "'No tasks match your filters.'", "As expected", "Pass", SHOT + "07_empty_search_desktop_1366x768.png"),
    m("TC-GUI-011", "NF3 GUI", "GUI checklist (feedback)", "User gets a confirmation after create / edit / delete", "-",
      "Create, edit, delete a task", "Short success message (e.g. 'Task created')", "No message; page silently reloads",
      "Fail", "Manual check", "DEF-024", "Low"),
    m("TC-GUI-012", "NF5 Compatibility", "Configuration (screen size)", "Layout at desktop 1366x768", "-", "Open all pages",
      "No overlap, no horizontal scroll", "As expected on all pages", "Pass", SHOT + "*_desktop_1366x768.png"),
    m("TC-GUI-013", "NF5 Compatibility", "Configuration (screen size)", "Layout at tablet 768x1024", "-", "Open all pages",
      "No overlap, no horizontal scroll", "As expected on all pages", "Pass", SHOT + "*_tablet_768x1024.png"),
    m("TC-GUI-014", "NF5 Compatibility", "Configuration (screen size)", "Layout at phone 375x812", "-", "Open all pages",
      "Content fits the screen; all columns visible", "Task list, New Task and Dashboard scroll sideways; Urgency column cut off; "
      "username cut off in top bar", "Fail", SHOT + "04_task_list_phone_375x812.png", "DEF-023"),
    m("TC-GUI-015", "NF3 GUI", "GUI checklist (forms)", "Form keeps typed values after a validation error", "username 'ab'",
      "Submit invalid Register form", "Username field still shows 'ab' so the user can correct it", "Both fields are emptied",
      "Fail", SHOT + "03_register_error_desktop_1366x768.png", "DEF-025", "Low"),
]

ACC = [
    m("TC-ACC-001", "NF4 Accessibility", "WCAG 3.1.1 (A) Language of page", "Page language is declared", "-",
      "Check <html lang>", "lang='en'", "lang='en' on every page", "Pass", "audit_results.json"),
    m("TC-ACC-002", "NF4 Accessibility", "WCAG 2.4.2 (A) Page titled", "Pages have descriptive titles", "-", "Read titles",
      "Unique titles", "Unique titles", "Pass", "audit_results.json"),
    m("TC-ACC-003", "NF4 Accessibility", "WCAG 1.3.1 / 4.1.2 (A) Labels", "Form inputs have programmatic labels", "-",
      "Run Axe on Login, Register, New Task", "0 'label' violations",
      "Axe 'label' (critical): 2 inputs on Login, 2 on Register, 3 on New Task. <label> is not linked to its input (no for/id)",
      "Fail", "audit_results.json; templates/login.html", "DEF-021", "High"),
    m("TC-ACC-004", "NF4 Accessibility", "WCAG 4.1.2 (A) Name, role, value", "Filter dropdowns have an accessible name", "-",
      "Run Axe on My Tasks", "0 'select-name' violations", "Axe 'select-name' (critical): category and status <select> have no name",
      "Fail", "audit_results.json", "DEF-021", "High"),
    m("TC-ACC-005", "NF4 Accessibility", "WCAG 1.4.3 (AA) Contrast", "Text contrast at least 4.5:1", "-", "Run Axe; check CSS colours",
      "0 'color-contrast' violations", "Empty-state text #999 on white = 2.8:1 (also used for done-task titles)", "Fail",
      "audit_results.json; static/style.css lines 58, 61", "DEF-022", "Low"),
    m("TC-ACC-006", "NF4 Accessibility", "WCAG 2.1.1 / 2.4.3 (A) Keyboard, focus order", "All controls reachable by Tab in a logical order",
      "-", "Press Tab through the Login page", "Brand -> Username -> Password -> Log in -> Register",
      "Exactly that order; nothing unreachable", "Pass", "audit_results.json (keyboard)"),
    m("TC-ACC-007", "NF4 Accessibility", "WCAG 2.4.7 (AA) Focus visible", "Keyboard focus can be seen", "-", "Tab through pages",
      "A visible outline on the focused control", "Browser default outline visible (outline-style auto)", "Pass",
      "audit_results.json (keyboard)"),
    m("TC-ACC-008", "NF4 Accessibility", "WCAG 3.3.1 (A) Error identification", "Errors are described in text", "username 'ab'",
      "Submit invalid form", "Error explained in words", "Text message explains the rule", "Pass",
      SHOT + "03_register_error_desktop_1366x768.png"),
    m("TC-ACC-009", "NF4 Accessibility", "WCAG 1.4.1 (A) Use of colour", "Urgency is not shown by colour alone", "-", "View badges",
      "Badge has text plus colour", "Every badge has a text label", "Pass", SHOT + "04_task_list_desktop_1366x768.png"),
    m("TC-ACC-010", "NF4 Accessibility", "WCAG 1.4.10 (AA) Reflow", "Content reflows on a narrow screen without sideways scrolling",
      "375 px wide", "Open My Tasks on phone size", "No horizontal scroll", "Horizontal scroll; Urgency column hidden", "Fail",
      SHOT + "04_task_list_phone_375x812.png", "DEF-023"),
    m("TC-ACC-011", "NF4 Accessibility", "WCAG 4.1.2 / 2.4.6 (A/AA) Button names", "Complete/reopen button has a meaningful name",
      "-", "Inspect the ○ / ✓ button", "Name such as 'Mark task as done'", "Button text is only the symbol '○' or '✓'; a screen "
      "reader announces 'white circle'", "Fail", "templates/index.html line 41", "DEF-021"),
]

COMP = [
    m("TC-COMP-001", "NF5 Compatibility", "Compatibility matrix (smoke set)", "Smoke set on Chrome 153 / Linux, desktop",
      "Smoke set: register, login, create, complete, delete, filter, dashboard", "Run AT-001..AT-010", "All smoke steps work",
      "All work (failures only from known defects DEF-001/002/007)", "Pass", "06_Automation_Regression/evidence/", priority="High"),
    m("TC-COMP-002", "NF5 Compatibility", "Compatibility matrix (smoke set)", "Smoke set on Chrome / Windows 11", "same smoke set",
      "Run manually or HEADED=1 pytest -m ui", "All smoke steps work", "Not run yet (group laptop)", "Not Run", "-", priority="High"),
    m("TC-COMP-003", "NF5 Compatibility", "Compatibility matrix (smoke set)", "Smoke set on Microsoft Edge / Windows 11",
      "same smoke set", "Run manually", "All smoke steps work", "Not run yet (group laptop)", "Not Run", "-"),
    m("TC-COMP-004", "NF5 Compatibility", "Compatibility matrix (smoke set)", "Smoke set on Firefox / Windows 11", "same smoke set",
      "Run manually", "All smoke steps work; date picker usable", "Not run yet (group laptop)", "Not Run", "-"),
    m("TC-COMP-005", "NF5 Compatibility", "Compatibility matrix (smoke set)", "Smoke set on Safari / macOS", "same smoke set",
      "Run manually", "All smoke steps work; date picker usable", "Not run yet (group laptop, if a member has a Mac)", "Not Run", "-",
      priority="Low"),
]

PERF = [
    m(f"TC-PERF-00{i+1}", "NF2 Performance", f"Load test ({u} users)", f"Response time and errors at {u} concurrent users",
      "Workload in locustfile.py; 40 s; perf_user with 100 tasks", f"run_perf.sh (-u {u} -r {u})",
      "Every request type: 95th percentile < 1,000 ms; error rate 0%", actual, status,
      f"05_Security_Performance/perf_results/u{u}_stats.csv", defect, priority="Medium",
      pre="App running locally (Flask dev server, debug on); load generator on the same machine (2 vCPU, 8 GB)")
    for i, (u, actual, status, defect) in enumerate([
        (1, "Tasks p95 5 ms, dashboard p95 6 ms, login 117 ms; 0 errors", "Pass", ""),
        (10, "Tasks p95 6 ms, dashboard p95 11 ms, login p95 610 ms; 0 errors", "Pass", ""),
        (25, "Tasks p95 9 ms, dashboard p95 10 ms, but login p95 1,200 ms; 0 errors", "Fail", "DEF-026"),
        (50, "Tasks p95 9 ms, dashboard p95 12 ms, but login p95 2,500 ms; 0 errors", "Fail", "DEF-026"),
    ])
] + [
    m("TC-PERF-005", "NF2 Performance", "Stress step (100 users, gradual ramp 10/s)",
      "Behaviour beyond the planned load: does it fail, and how?", "Same workload; 100 users added 10 per second",
      "locust -u 100 -r 10 -t 40s", "No crash; error rate 0%; record slowest point",
      "0 errors in 2,396 requests; 61 req/s; aggregated p95 66 ms; login avg 483 ms. Breaking point not reached",
      "Pass", "05_Security_Performance/perf_results/u100_stress_stats.csv", "",
      pre="Same environment as TC-PERF-001..004"),
]

SEC_MANUAL = [
    m("TC-SEC-013", "F04 Create task", "Security (STRIDE: Information disclosure)",
      "Error pages do not show the stack trace or debugger", "invalid due date 2026-13-45 saved by form post",
      "1. Start app with 'python app.py' 2. Save task with the bad date 3. Open My Tasks",
      "Generic error page; no traceback or console", "Werkzeug Debugger page with full traceback, file paths and code",
      "Fail", SHOT + "08_server_error_debugger.png", "DEF-014",
      pre="App started with python app.py (debug=True, as documented in README)"),
]
