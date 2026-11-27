"""
Writes the per-week deliverable files into each repository folder, so a reader
on GitHub can find every item the project brief asks for without opening the
full report. All tables come from 08_Final_QA_Report/report_data.json, which
tools/build_artefacts.py builds from the real test results.

Run after build_artefacts.py:   python tools/build_folder_deliverables.py
"""

import json
import os

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, "08_Final_QA_Report", "report_data.json")))
M, ROWS = D["metrics"], D["rows"]
G, O = M["by_group"], M["overall"]
COV = M["coverage"]
PERF = M["performance"]
P = lambda *a: os.path.join(ROOT, *a)  # noqa: E731

TEMPLATE = ["Test Case ID", "Feature/Requirement", "Technique/Test Type", "Objective", "Preconditions", "Test Data",
            "Steps", "Expected Result", "Actual Result", "Status", "Evidence", "Defect ID"]
FILL = {"Pass": "E3F4E3", "Fail": "FBE3E3", "Not Run": "EEEEEE", "Blocked": "FFF3D6"}
thin = Side(style="thin", color="D0D0D0")


def write_sheet(ws, header, data, widths, status_col=None):
    ws.append(header)
    for r in data:
        ws.append(list(r))
    for i, w in enumerate(widths):
        ws.column_dimensions[chr(65 + i)].width = w
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1B3A5C")
        c.alignment = Alignment(wrap_text=True, vertical="center")
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
            c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
        if status_col and row[status_col - 1].value in FILL:
            row[status_col - 1].fill = PatternFill("solid", fgColor=FILL[row[status_col - 1].value])
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = ws.dimensions


def tc_rows(group):
    return [(r["id"], r["feature"], r["technique"], r["objective"], r["pre"], r["data"], r["steps"], r["expected"],
             r["actual"], r["status"], r["evidence"], r["defect"]) for r in ROWS if r["group"] == group]


TW = [12, 18, 24, 34, 22, 24, 30, 34, 38, 9, 34, 10]


def workbook(path, sheets):
    wb = Workbook()
    first = True
    for title, header, data, widths, sc in sheets:
        ws = wb.active if first else wb.create_sheet()
        ws.title = title
        first = False
        write_sheet(ws, header, data, widths, sc)
    wb.save(path)


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
    for r in rows:
        out.append("| " + " | ".join(str(x).replace("|", "/").replace("\n", " ") for x in r) + " |")
    return "\n".join(out)


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.strip() + "\n")


def counts(group):
    c = G[group]
    return f"{c['planned']} planned, {c['executed']} executed, **{c['passed']} passed, {c['failed']} failed**" + \
        (f", {c['not_run']} not run" if c["not_run"] else "")


def fails(group):
    return [(r["id"], r["objective"], r["actual"], r["defect"]) for r in ROWS if r["group"] == group and r["status"] == "Fail"]


DEF = {d["id"]: d for d in D["defects"]}

# =============================================================== 01 BLACK BOX
workbook(P("01_Black_Box", "Black_Box_Test_Cases.xlsx"),
         [("Black-box test cases", TEMPLATE, tc_rows("Black-box (Wk 1)"), TW, 10)])
write(P("01_Black_Box", "README.md"), f"""
# Week 1 – Application Analysis and Black-Box Testing

**Result:** {counts("Black-box (Wk 1)")}. Executed {M["run_date"]}.

| Brief deliverable | Where to find it |
| --- | --- |
| Application overview and feature inventory | [Black_Box_Design.md §1–2](Black_Box_Design.md) · Report §1.3–1.4 |
| Initial test scope / risk matrix | [Black_Box_Design.md §3](Black_Box_Design.md) |
| Black-box test scenarios and cases | [Black_Box_Test_Cases.xlsx](Black_Box_Test_Cases.xlsx) (lecturer's Test Case Template fields) |
| Test data and technique justification | [Black_Box_Design.md §4–8](Black_Box_Design.md) |
| Execution evidence and initial defect records | [test_blackbox_web.py](test_blackbox_web.py), log `07_Test_Management/results/pytest_core_log.txt`, defects in `07_Test_Management/PyTodo_Test_Management.xlsx` |

**Run:** `pytest 01_Black_Box -v`
""")
write(P("01_Black_Box", "Black_Box_Design.md"), f"""
# Black-box test design (Week 1)

## 1. Application overview
PyTodo Pro is a Flask + SQLite web app. A registered user creates, categorises, searches, completes and deletes
personal tasks with optional due dates. Each task gets an urgency label and a dashboard shows totals. The same
functions are offered as a JSON REST API. There is one user type (registered user); each user must only see and
change their own tasks.

## 2. Feature inventory
{md_table(["ID", "Feature", "Business rule"], [
    ["F01", "Registration", "Username 3–20 chars (letters, digits, _); password at least 8 chars"],
    ["F02", "Login / logout", "Correct credentials start a session; logout ends it"],
    ["F03", "Access control", "Logged out: redirect / 401; users reach only their own tasks"],
    ["F04", "Create task", "Title required; category and due date (YYYY-MM-DD) optional"],
    ["F05", "View / list", "Newest first; API pages with page, per_page"],
    ["F06", "Edit task", "Edit fields; API partial update"],
    ["F07", "Complete / reopen", "completed_at set when done, cleared when reopened"],
    ["F08", "Delete task", "Owner only"],
    ["F09", "Filter / search", "Category, status; search part of title"],
    ["F10", "Urgency", "No due date, Overdue, Due Today, Due Soon (1–2 days), Upcoming (3+), Done"],
    ["F11", "Dashboard", "Total, Open, Overdue, Due Soon, Completed last 7 days (inclusive)"],
    ["F12", "Categories", "Work, Personal, Study, Urgent"]])}

## 3. Initial test scope / risk matrix (before testing)
Risk score = likelihood × impact (1–3 each). High ≥ 6, Medium 3–4, Low ≤ 2.

{md_table(["Feature", "Likelihood", "Impact", "Score", "Priority", "Reason"], [
    ["F03 Access control / F08 Delete", 2, 3, 6, "High", "Privacy of every user"],
    ["F04 / F06 validation", 2, 3, 6, "High", "Bad data could corrupt tasks"],
    ["F09 Search / filter", 2, 3, 6, "High", "User text reaches database queries"],
    ["F10 Urgency / F11 Dashboard", 2, 2, 4, "Medium", "Date boundaries easy to get wrong"],
    ["F01 Registration / F02 Login", 2, 2, 4, "Medium", "Gate to the app"],
    ["F05 List, F07 Toggle", 1, 2, 2, "Low", "Simple display logic"],
    ["F12 Categories", 1, 1, 1, "Low", "Read-only seeded list"]])}

The final (after-testing) ratings are in the Risk Register sheet of `07_Test_Management/PyTodo_Test_Management.xlsx`.

## 4. Equivalence partitioning
{md_table(["Input", "Valid classes", "Invalid classes", "Test cases"], [
    ["Username length", "3–20", "< 3; > 20", "TC-BB-001..006"],
    ["Username characters", "letters, digits, _", "space, symbols", "TC-BB-007, 008"],
    ["Password length", "≥ 8", "< 8; empty", "TC-BB-009..012"],
    ["Task title", "text; special characters", "empty; spaces only", "TC-BB-021..024, 048"],
    ["Due date", "valid date; none", "impossible date", "TC-BB-021, 022, 049"],
    ["Search text", "partial match; no match; apostrophe", "–", "TC-BB-041, 042, 044"]])}

## 5. Boundary value analysis (3-value)
{md_table(["Step", "Username length", "Password length", "Days until due date"], [
    ["Partitions", "0–2 | 3–20 | 21+", "0–7 | 8+", "≤ −1 | 0 | 1–2 | 3+"],
    ["Boundaries", "3, 20", "8", "0, 1, 2, 3"],
    ["Coverage items", "2, 3, 4, 19, 20, 21", "7, 8, 9", "−1, 0, 1, 2, 3"],
    ["Test cases", "TC-BB-001..006", "TC-BB-009..011", "TC-BB-025..029"],
    ["Result", "All pass", "8 fails (DEF-002)", "0 fails (DEF-001)"]])}

## 6. Decision tables
**Registration** (C1 username valid, C2 password valid, C3 username not taken; 2³ = 8 rules simplified to 4):

{md_table(["", "R1", "R2", "R3", "R4"], [
    ["C1 Username valid", "Y", "Y", "Y", "N"], ["C2 Password valid", "Y", "Y", "N", "–"], ["C3 Not taken", "Y", "N", "–", "–"],
    ["Action", "Create account", "'Username taken'", "Password error", "Username error"],
    ["Test case", "TC-BB-013", "TC-BB-014", "TC-BB-015", "TC-BB-016"], ["Result", "Pass", "Fail (DEF-004)", "Pass", "Pass"]])}

**Login** (C1 user exists, C2 password correct; 2² = 4 rules simplified to 3): R1 Y/Y log in (TC-BB-017), R2 Y/N error
(TC-BB-018), R3 N/– same error (TC-BB-019). All pass.

## 7. State transitions
{md_table(["State", "toggle", "delete", "edit", "Tests"], [
    ["Open", "→ Done, set completed_at", "→ Deleted", "→ Open", "TC-BB-032, 034, 047"],
    ["Done", "→ Open, clear completed_at", "→ Deleted", "→ Done", "TC-BB-033"],
    ["Deleted", "invalid (refused)", "–", "invalid (refused)", "TC-BB-035, 036"]])}

Session states: logged out → protected page (TC-BB-037); logged in → log out → protected page (TC-BB-038).

## 8. Test data and technique justification
- EP keeps the number of tests small while covering every input class; BVA is used wherever there is a numeric limit
  (username, password, days to due date); decision tables where several conditions combine (registration, login);
  state transitions where the result depends on earlier events (task, session).
- Dates are calculated from the run date (today−1 … today+3), so the tests give the same result on any day.
- Some cases post form data directly (title of spaces, date 2026-13-45) to bypass browser checks and test the server.
- Execution: cases were executed through the web forms (HTTP form submissions recorded with PyTest so they can be
  repeated); key results were also confirmed in a real browser with Selenium screenshots (`06_Automation_Regression/evidence`).

## 9. Failed cases and defects
{md_table(["Test", "Objective", "Actual", "Defect"], fails("Black-box (Wk 1)"))}
""")

# =============================================================== 02 WHITE BOX
ch, ca = COV["helpers.py (unit tests only)"], COV["app.py (all suites)"]
workbook(P("02_White_Box_Coverage", "White_Box_Test_Cases.xlsx"),
         [("White-box test cases", TEMPLATE, tc_rows("White-box (Wk 2)"), TW, 10)])
write(P("02_White_Box_Coverage", "README.md"), f"""
# Week 2 – White-Box Testing and Coverage

**Result:** {counts("White-box (Wk 2)")}. helpers.py **{ch["stmt_pct"]}% statement / {ch["branch_pct"]}% branch** coverage;
app.py {ca["stmt_pct"]}% / {ca["branch_pct"]}% (all suites).

| Brief deliverable | Where to find it |
| --- | --- |
| Selected code units and justification | [White_Box_Analysis.md §1](White_Box_Analysis.md) |
| Control-flow analysis | [White_Box_Analysis.md §2](White_Box_Analysis.md), [cfg/](cfg/) (CFG diagrams + .dot sources) |
| White-box test cases | [White_Box_Test_Cases.xlsx](White_Box_Test_Cases.xlsx) |
| Automated/unit test file | [test_whitebox_helpers.py](test_whitebox_helpers.py) |
| Coverage report and interpretation | [htmlcov_helpers/index.html](htmlcov_helpers/index.html), [htmlcov_full/index.html](htmlcov_full/index.html), [White_Box_Analysis.md §4](White_Box_Analysis.md) |

**Run:** `pytest -m unit --cov=app --cov-branch --cov-report=html`
""")
write(P("02_White_Box_Coverage", "White_Box_Analysis.md"), f"""
# White-box analysis (Week 2)

## 1. Units selected and why
{md_table(["Unit", "Why", "V(G)"], [
    ["helpers.compute_urgency", "Most important business rule; 4 decisions; drives badges and dashboard", 5],
    ["helpers.is_valid_password", "Registration gate; boundary at 8", 3],
    ["helpers.is_valid_username", "Registration gate; range + character rules", 4],
    ["helpers.completed_in_last_n_days", "Dashboard counter; inclusive boundary; compound condition", 4],
    ["app.api_update_task (completed_at)", "if / elif / else that sets or clears completion time", 3]])}

We did not attempt structural testing of the whole app (brief): helpers.py holds the business rules and is testable
without a server.

## 2. Control-flow analysis
![CFG compute_urgency](cfg/compute_urgency_cfg.png)

V(G) of compute_urgency, three ways: E − N + 2 = 13 − 10 + 2 = **5**; predicates + 1 = 4 + 1 = **5**; regions = **5**.

![CFG completed_in_last_n_days](cfg/completed_cfg.png)

## 3. Basis paths (compute_urgency)
{md_table(["Path", "Meaning", "Test"], [
    ["1-3-4-10", "no due date", "TC-WB-001"], ["1-2-3-5-7-9-10", "today defaulted, far date", "TC-WB-002"],
    ["1-3-5-6-10", "past date → Overdue", "TC-WB-003"], ["1-3-5-7-8-10", "1–2 days → Due Soon", "TC-WB-005"],
    ["1-3-5-7-9-10", "3+ days → Upcoming", "TC-WB-007"]])}

Plus boundary tests on each decision (TC-WB-004 due today, TC-WB-006 two days). **Path/data-flow notes:** no infeasible
paths; the compound condition `age > 0 and age.days < n` is tested both ways (TC-WB-021/023); `due_date` is defined by
the user, stored without validation and only used in compute_urgency where `strptime` raises (TC-WB-008) — the
root of DEF-008.

## 4. Coverage and interpretation
{md_table(["Scope", "Statements", "Stmt %", "Branches", "Branch %"], [
    ["helpers.py (unit tests)", f"{ch['covered']}/{ch['statements']}", ch["stmt_pct"], f"{ch['branches_covered']}/{ch['branches']}", ch["branch_pct"]],
    ["app.py (all suites)", f"{ca['covered']}/{ca['statements']}", ca["stmt_pct"], f"{ca['branches_covered']}/{ca['branches']}", ca["branch_pct"]]])}

- helpers.py is 100% covered yet 3 tests fail: coverage shows what ran, not that it is correct, and it cannot find a
  missing branch (there is no "Due Today" branch at all).
- app.py uncovered lines {", ".join(map(str, ca["missing_lines"]))}: 242/266 render empty forms on GET (exercised only by
  Selenium, which is not measured); 375 is the API `status=open` filter (**not tested – a gap**); 481–482 is the
  `__main__` start-up block.

## 5. Failed cases
{md_table(["Test", "Objective", "Actual", "Defect"], fails("White-box (Wk 2)"))}
""")

# =============================================================== 03 SPECIAL
gui = [r for r in ROWS if r["group"] == "GUI & config (Wk 3)"]
workbook(P("03_Special_Testing", "Special_Testing_Results.xlsx"), [
    ("GUI checklist", TEMPLATE, tc_rows("GUI & config (Wk 3)"), TW, 10),
    ("Accessibility", TEMPLATE, tc_rows("Accessibility (Wk 3)"), TW, 10),
    ("Compatibility", TEMPLATE, tc_rows("Compatibility (Wk 3)"), TW, 10),
    ("Usability (LEMES)", ["Dimension", "Type", "Observation"], D["usability"], [16, 10, 100], None),
])
write(P("03_Special_Testing", "README.md"), f"""
# Week 3 – GUI, Compatibility, Usability and Accessibility

**Result:** GUI {counts("GUI & config (Wk 3)")}; accessibility {counts("Accessibility (Wk 3)")};
compatibility {counts("Compatibility (Wk 3)")}.

| Brief deliverable | Where to find it |
| --- | --- |
| GUI testing checklist / results | [Special_Testing_Results.xlsx](Special_Testing_Results.xlsx) sheet *GUI checklist* |
| Compatibility / configuration matrix | sheet *Compatibility*; [compatibility_checklist.md](compatibility_checklist.md) for manual runs |
| Usability observations | sheet *Usability (LEMES)*; [Special_Testing_Findings.md](Special_Testing_Findings.md) |
| Basic accessibility findings | sheet *Accessibility*; Axe output [audit_results.json](audit_results.json) |
| Defects and improvement recommendations | [Special_Testing_Findings.md](Special_Testing_Findings.md) |
| Screenshots (7 pages × 3 screen sizes) | [screenshots/](screenshots/) |

**Re-run the audit** (app running, `npm install axe-core`): `python 03_Special_Testing/gui_a11y_audit.py node_modules/axe-core/axe.min.js`
""")
write(P("03_Special_Testing", "Special_Testing_Findings.md"), f"""
# Week 3 findings and recommendations

Method: Selenium opened every page in Chrome at desktop (1366×768), tablet (768×1024) and phone (375×812) sizes
and saved screenshots; the Axe engine checked WCAG 2.1 A/AA rules; keyboard order was checked; screens were reviewed
against a GUI checklist and Nielsen's LEMES dimensions.

## Compatibility / configuration matrix
{md_table(["Browser / OS", "Desktop", "Tablet", "Phone", "Test"], [
    ["Chrome 153 / Linux", "Pass", "Pass", "Fail (DEF-023)", "TC-COMP-001, TC-GUI-012..014"],
    ["Chrome / Windows 11", "Not Run", "Not Run", "Not Run", "TC-COMP-002"],
    ["Edge / Windows 11", "Not Run", "Not Run", "Not Run", "TC-COMP-003"],
    ["Firefox / Windows 11", "Not Run", "Not Run", "Not Run", "TC-COMP-004"],
    ["Safari / macOS", "Not Run", "Not Run", "Not Run", "TC-COMP-005 (no Mac in group)"]])}

## Failed checks
{md_table(["Test", "Check", "Actual", "Defect"], fails("GUI & config (Wk 3)") + fails("Accessibility (Wk 3)"))}

## Usability (LEMES)
{md_table(["Dimension", "Type", "Observation"], D["usability"])}

## Recommendations
1. Link every `<label>` to its input (`for`/`id`); add `aria-label` to the filter dropdowns and the ○/✓ button.
2. Darken grey text to at least #767676 (4.5:1 contrast).
3. Make the task table responsive below 600 px.
4. Show success messages after create/edit/delete; keep typed values after a validation error.
5. Make search apply on Enter like the dropdowns; allow sorting by due date.
""")

# =============================================================== 04 API
api = [r for r in ROWS if r["group"] == "Web & API (Wk 4)"]
workbook(P("04_Web_API", "API_Test_Cases.xlsx"), [("API test cases", TEMPLATE, tc_rows("Web & API (Wk 4)"), TW, 10)])
write(P("04_Web_API", "README.md"), f"""
# Week 4 – Web and API Testing

**Result:** {counts("Web & API (Wk 4)")}.

| Brief deliverable | Where to find it |
| --- | --- |
| Web test scenarios | [Web_and_API_Testing.md §1](Web_and_API_Testing.md) (+ black-box and Selenium suites) |
| API test suite | [test_api.py](test_api.py) |
| Request / test data | [API_Test_Cases.xlsx](API_Test_Cases.xlsx) column *Test Data* |
| Expected versus actual status / response | [API_Test_Cases.xlsx](API_Test_Cases.xlsx); [Web_and_API_Testing.md §3](Web_and_API_Testing.md) |
| Execution evidence and defects | log `07_Test_Management/results/pytest_core_log.txt`; [Web_and_API_Testing.md §4](Web_and_API_Testing.md) |

**Run:** `pytest 04_Web_API -v` (no server needed – Flask test client, fresh database per test)
""")
write(P("04_Web_API", "Web_and_API_Testing.md"), f"""
# Web and API testing (Week 4)

## 1. Web scenarios
1. Register → log in → create task → complete → filter → dashboard → log out (TC-BB-013..045, AT-001..009).
2. Logged-out user opens a protected page → redirect to /login (TC-BB-037); after logout the dashboard is closed (TC-BB-038).
3. Client vs server validation: same bad data through the browser and directly to the server (§3).

## 2. Endpoints
{md_table(["Endpoint", "Auth", "Tests"], [
    ["POST /api/register", "No", "TC-API-001..006"], ["POST /api/login", "No", "TC-API-007..009"],
    ["GET /api/categories", "Yes (README)", "TC-API-011, 012"], ["GET /api/tasks", "Yes", "TC-API-010, 025..033"],
    ["POST /api/tasks", "Yes", "TC-API-013..021"], ["GET /api/tasks/{id}", "Yes", "TC-API-022..024"],
    ["PUT /api/tasks/{id}", "Yes", "TC-API-034..039"], ["DELETE /api/tasks/{id}", "Yes", "TC-API-040..043"],
    ["GET /api/dashboard", "Yes", "TC-API-044..046"]])}

## 3. UI versus server behaviour
{md_table(["Input", "Browser", "Server / API", "Verdict"], [
    ["Empty title", "Blocked by `required` (AT-010)", "Saved via form post / API PUT (TC-BB-023, TC-API-035)", "DEF-009"],
    ["Impossible date", "Date picker prevents it", "Saved, then 500 on every list (TC-BB-049, TC-API-017)", "DEF-008"],
    ["Apostrophe in search", "Works (TC-BB-044)", "500 (TC-API-033)", "DEF-006"],
    ["Delete other user's task", "Not possible", "Possible (TC-API-042)", "DEF-005"]])}

## 4. Failed cases (expected vs actual)
{md_table(["Test", "Objective", "Actual", "Defect"], fails("Web & API (Wk 4)"))}
""")

# =============================================================== 05 SEC/PERF
workbook(P("05_Security_Performance", "Security_Performance_Test_Cases.xlsx"), [
    ("Security", TEMPLATE, tc_rows("Security (Wk 5)"), TW, 10),
    ("Performance", TEMPLATE, tc_rows("Performance (Wk 5)"), TW, 10),
    ("STRIDE", ["Asset / function", "STRIDE", "Threat", "Property", "Test(s)", "Result", "Mitigation"], D["stride"],
     [22, 20, 44, 16, 22, 26, 34], None)])
write(P("05_Security_Performance", "README.md"), f"""
# Week 5 – Security and Performance Testing

**Result:** security {counts("Security (Wk 5)")}; performance {counts("Performance (Wk 5)")}.
All security tests run only against a temporary local database (no uncontrolled penetration testing).

| Brief deliverable | Where to find it |
| --- | --- |
| Threat / STRIDE table | [STRIDE_Threat_Table.md](STRIDE_Threat_Table.md) |
| Security test cases and findings | [test_security.py](test_security.py), [Security_Performance_Test_Cases.xlsx](Security_Performance_Test_Cases.xlsx) |
| Performance objective and workload | [Performance_Report.md §1](Performance_Report.md), [locustfile.py](locustfile.py) |
| Performance results and interpretation | [Performance_Report.md §2–3](Performance_Report.md), raw data [perf_results/](perf_results/) |
| Limitations and recommendations | [Performance_Report.md §4](Performance_Report.md), [STRIDE_Threat_Table.md](STRIDE_Threat_Table.md) |

**Run:** `pytest 05_Security_Performance -v` · load test (app running): `bash 05_Security_Performance/run_perf.sh`
""")
write(P("05_Security_Performance", "STRIDE_Threat_Table.md"), f"""
# STRIDE threat table (Week 5)

Steps: decompose the app into assets and data flows → apply STRIDE → decide mitigations → derive safe tests.

{md_table(["Asset / function", "STRIDE", "Threat", "Property", "Test(s)", "Result", "Mitigation"], D["stride"])}

## Security failures
{md_table(["Test", "Objective", "Actual", "Defect"], fails("Security (Wk 5)"))}
""")
pr = lambda u, n: PERF.get(u, {}).get(n, {})  # noqa: E731
write(P("05_Security_Performance", "Performance_Report.md"), f"""
# Performance experiment (Week 5)

## 1. Objective, workload and environment (defined before execution)
- **Objective:** measure response time, throughput and error rate as simulated users increase; find where it degrades.
- **Workload (Locust):** each user logs in once as `perf_user` (100 seeded tasks), then with 1–2 s think time:
  60% GET /api/tasks, 30% GET /api/dashboard, 10% POST /api/tasks.
- **Levels:** 1, 10, 25, 50 users (40 s each, all start together) + stress step of 100 users added 10/s.
- **Criterion:** every request type 95th percentile < 1,000 ms and 0% errors.
- **Environment:** Flask development server (debug on), SQLite, load generator on the same 2-vCPU / 8 GB Linux machine.

## 2. Results
{md_table(["Users", "Task list avg/p95 ms", "Dashboard avg/p95 ms", "Login avg/p95 ms", "Req/s", "Errors"],
          [[u.replace("_stress", " (stress)"),
            f"{pr(u, 'GET /api/tasks').get('avg')}/{pr(u, 'GET /api/tasks').get('p95')}",
            f"{pr(u, 'GET /api/dashboard').get('avg')}/{pr(u, 'GET /api/dashboard').get('p95')}",
            f"{pr(u, '/api/login').get('avg')}/{pr(u, '/api/login').get('p95')}",
            pr(u, "Aggregated").get("rps"), pr(u, "Aggregated").get("fail")] for u in PERF])}

![p95 chart](../08_Final_QA_Report/charts/performance_p95.png)

## 3. Interpretation
- Task list and dashboard stay below 15 ms (p95) up to 50 users with 0 errors; throughput grows with users.
- Login is the bottleneck when many users log in in the same second (CPU-heavy password hashing): p95 1,200 ms at
  25 users and 2,500 ms at 50 (DEF-026). With a gradual ramp, 100 users logged in at about 483 ms average.
- The stress step did not reach a breaking point (0 errors).

## 4. Limitations and recommendations
Dev server, shared CPU with the load generator, SQLite, short runs, no CPU/memory monitoring: results show trends,
not production capacity. Recommend a production WSGI server with debug off, login rate limiting, and a repeat test
on a production-like machine with resource monitoring.
""")

# =============================================================== 06 AUTOMATION
reg = [r for r in ROWS if r["id"] in M["regression_ids"]]
workbook(P("06_Automation_Regression", "Automation_Traceability.xlsx"), [
    ("Manual to automated", ["Script", "What it automates", "Manual test(s)", "Why chosen", "Result"],
     D["automation"], [10, 32, 26, 40, 10], 5),
    ("Regression suite", ["Test ID", "Phase", "What it checks", "Last result", "Defect"],
     [(r["id"], r["group"], r["objective"], r["status"], r["defect"]) for r in reg], [12, 20, 50, 10, 10], 4)])
write(P("06_Automation_Regression", "README.md"), f"""
# Week 6 – Test Automation and Regression

**Result:** Selenium {counts("UI automation (Wk 6)")}. {M["automated_cases"]} of {O["planned"]} test cases automated
({M["automation_rate"]}%). Regression suite: {M["regression_suite_size"]} tests.

| Brief deliverable | Where to find it |
| --- | --- |
| Automation candidate justification | [Automation_Reflection.md §1](Automation_Reflection.md) |
| Automated scripts | [test_ui_selenium.py](test_ui_selenium.py), [pages.py](pages.py) (Page Object Model) + PyTest suites in 01, 02, 04, 05 |
| Manual-to-automated traceability | [Automation_Traceability.xlsx](Automation_Traceability.xlsx) |
| Execution report / logs | `07_Test_Management/results/pytest_ui_log.txt`, `pytest_regression_log.txt`, `junit_*.xml`; screenshots [evidence/](evidence/) |
| Regression suite and automation reflection | `pytest -m regression`; [Automation_Reflection.md §2–3](Automation_Reflection.md) |

**Run UI tests** (app running): `pytest -m ui -v` · other browsers: `set BROWSER=edge` / `firefox` · watch: `set HEADED=1`
""")
write(P("06_Automation_Regression", "Automation_Reflection.md"), f"""
# Automation candidates, regression suite and reflection (Week 6)

## 1. Candidate selection
Criteria: **repetition, stability, criticality, regression value**. Not automated: exploratory checks, visual/usability
judgement, accessibility judgement, one-off cross-browser checks on members' laptops.

{md_table(["Layer (pyramid)", "Tool", "Tests"], [
    ["UI / end-to-end (few)", "Selenium + Page Object Model", G["UI automation (Wk 6)"]["planned"]],
    ["API / integration", "PyTest + Flask test client", G["Black-box (Wk 1)"]["planned"] + G["Web & API (Wk 4)"]["planned"] + G["Security (Wk 5)"]["planned"] - 1],
    ["Unit (many)", "PyTest parametrize", G["White-box (Wk 2)"]["planned"]]])}

## 2. Regression suite
{M["regression_suite_size"]} tests tagged `@pytest.mark.regression` (high-risk areas, frequently used features, critical
rules, every failed boundary). Failing ones are known defects and act as **confirmation tests** after a fix; the rest
check that the fix broke nothing.

## 3. Reflection
- **Benefits:** the non-UI suite runs in about 13 s, so it was re-run many times with identical results; documents are
  generated from results, keeping IDs consistent.
- **Limitations:** writing scripts took longer than one manual run; one Selenium test was flaky until waits and a
  retry were added; automation cannot judge usability or visual quality.
""")

# =============================================================== 07 TEST MANAGEMENT
write(P("07_Test_Management", "README.md"), f"""
# Week 7 – Test Planning, Traceability and Defect Management

| Brief deliverable | Where to find it |
| --- | --- |
| Formal Software Test Plan | [Test_Plan_and_Strategy.md](Test_Plan_and_Strategy.md) (PYTODO-STP v2.0) · Report §8 |
| Test Strategy | [Test_Plan_and_Strategy.md §2](Test_Plan_and_Strategy.md) |
| Updated RTM | [PyTodo_Test_Management.xlsx](PyTodo_Test_Management.xlsx) sheet *RTM* |
| Master test-case repository | same workbook, sheet *Test Cases* ({O["planned"]} cases, template fields) |
| Consolidated defect log | same workbook, sheet *Defect Log* ({M["defects_total"]} defects, Defect Report Template fields) |
| Test execution / regression status | sheets *Summary*, *Regression Suite*; raw logs in [results/](results/) |

Also in the workbook: Risk Register (Week 1 vs final), STRIDE, Automation Map, Coverage, Performance, Usability,
Compatibility Matrix. The workbook is rebuilt from the real results by `bash tools/run_all.sh`.
""")
write(P("07_Test_Management", "Test_Plan_and_Strategy.md"), f"""
# Software Test Plan and Test Strategy – PYTODO-STP v2.0

Structure follows IEEE 829. Version 2.0 updated in Week 7 with evidence from Weeks 1–6.

## 1. Test Plan
**Objectives:** verify F01–F12 against the README/helpers.py; find reproducible defects (auth, authorisation,
validation, urgency); measure coverage of selected units; evaluate security, performance, usability, accessibility,
compatibility; build a regression suite; give an evidence-based quality judgement.

**Scope:** test items = PyTodo Pro as issued + its SQLite database. In scope: F01–F12 (UI and API), NF2–NF5.
Out of scope: production deployment/HTTPS, load beyond one machine, attacks on other systems, real assistive-technology users.

**Environment and tools:** Python 3.13, Flask 3.0.3, Chrome 153 (Linux) + members' laptops for TC-COMP-002..005;
PyTest, pytest-cov, Selenium (POM), axe-core, Locust; workbook + GitHub for test management.

**Test data:** qa_user1/qa_user2; usernames of 2, 3, 4, 19, 20, 21 chars; passwords of 7, 8, 9; dates today−1 … today+3;
titles empty / spaces / HTML / 5,000 chars; apostrophes; impossible dates.

**Roles:** Member 1 QA/Test Lead (plan, integration); Member 2 Test Design (black-box, GUI, RTM); Member 3
Automation/Tools (white-box, API, Selenium); Member 4 Defects & Metrics (defects, STRIDE, performance, metrics).

**Pass/fail:** Pass = actual matches expected written before execution; Fail = differs, linked to a DEF; Blocked =
precondition not met; Not Run = planned, not executed (reason recorded).

**Entry criteria:** app runs from requirements.txt; cases have IDs, data, expected results; fresh DB per run.

**Exit criteria (status):**
{md_table(["Criterion", "Target", "Actual"], [
    ["High-priority cases executed", "100%", f"{sum(1 for r in ROWS if r['priority'] == 'High' and r['status'] != 'Not Run')}/{sum(1 for r in ROWS if r['priority'] == 'High')}"],
    ["All cases executed", "≥ 90%", f"{O['execution_rate']}%"],
    ["Failed cases linked to defects", "100%", "100%"],
    ["helpers.py branch coverage", "≥ 90%", f"{ch['branch_pct']}%"],
    ["app.py statement coverage", "≥ 70%", f"{ca['stmt_pct']}%"],
    ["Every feature has an executed test", "100%", "100%"],
    ["Release: open Critical defects", "0", f"{M['severity']['Critical']} (not ready to release)"]])}

**Suspension/resumption:** suspend if the app cannot start, the DB is corrupted (DEF-008) or > 30% of a suite is
blocked; resume after resetting the DB.

**Project risks:** missed deadlines (weekly check-in, support member takes over); machine differences (injected dates,
environment recorded); blocking defect (fresh DB per test); inconsistent IDs (one catalogue, build script refuses
mismatches); demo failure (recorded backup).

## 2. Test Strategy
- **Risk-based:** likelihood × impact per feature, updated as evidence arrived (Risk Register, Week 1 vs final).
- **Levels:** unit (PyTest on helpers.py) → integration/API (Flask client) → system (Selenium, manual GUI) →
  acceptance-style scenarios; static code review found root causes of 8 defects.
- **Techniques:** EP, BVA, decision tables, state transitions, basis paths, API negative testing, STRIDE, load testing,
  WCAG/LEMES review.
- **Automation:** test pyramid; automate repeated, stable, critical, regression-valuable tests.
- **Defects:** one central log; severity = impact, priority = urgency; lifecycle New → Confirmed (→ Retest → Closed after fixes).
- **Metrics:** execution and pass rates per phase, defects by severity/area, density, coverage, automation rate,
  response time/throughput/error rate.
""")

# =============================================================== 08
write(P("08_Final_QA_Report", "README.md"), f"""
# Week 8 – Final QA Report, Metrics and Quality Evaluation

| Brief deliverable | Where to find it |
| --- | --- |
| Final integrated QA evaluation report | [PyTodo_Pro_Final_QA_Report.docx](PyTodo_Pro_Final_QA_Report.docx) |
| Metrics tables / charts | Report §11; [charts/](charts/); [metrics.json](metrics.json) |
| Residual risk assessment | Report §11.5; workbook sheet *Risk Register* |
| Quality findings and limitations | Report §11.6–11.7 |
| Prioritised recommendations and future testing | Report §12.4 |

**Headline:** {O["planned"]} test cases, {O["executed"]} executed ({O["execution_rate"]}%), {O["passed"]} passed,
{O["failed"]} failed; {M["defects_total"]} confirmed defects ({M["severity"]["Critical"]} Critical, {M["severity"]["Major"]} Major,
{M["severity"]["Moderate"]} Moderate, {M["severity"]["Minor"]} Minor). Verdict: not ready for release until Critical/Major
defects are fixed and the regression suite passes.
""")
write(P("09_Presentation", "README.md"), """
# Week 9 – Standards Integration and Final Presentation

| Brief deliverable | Where to find it |
| --- | --- |
| ISO/IEC 25010 characteristics evaluated / not evaluated | Report §12.1 |
| Regression tests in CI/CD and continuous testing | Report §12.2; pipeline [../.github/workflows/qa.yml](../.github/workflows/qa.yml) |
| QA/process improvements for Agile/DevOps | Report §12.3 |
| Final presentation and live demonstration | Slides: *add file here*; demo plan [demo_script.md](demo_script.md) |
""")
write(P("00_Smoke", "README.md"), """
# 00 – Lead's first smoke test

`smoke.py` was the QA Lead's quick exploratory check at the start of the project. It found 17 candidate defects
(CD-01..17), which were later reproduced by the phase owners and became DEF-001..017.

Run: `python 00_Smoke/smoke.py app`
""")
print("folder deliverables written")
