"""
Builds the test-management artefacts from the REAL test results:

  07_Test_Management/PyTodo_Test_Management.xlsx   (master test repository, RTM,
       defect log, risk register, STRIDE, automation map, coverage, performance,
       usability, compatibility matrix, metrics)
  08_Final_QA_Report/metrics.json                  (numbers used in the report)
  08_Final_QA_Report/charts/*.png                  (charts used in the report)

It refuses to build if any failed test has no defect, or a defect has no test,
so IDs stay consistent across all artefacts.
"""

import csv
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, OrderedDict
from datetime import date

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from openpyxl import Workbook  # noqa: E402
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side  # noqa: E402
from openpyxl.utils import get_column_letter  # noqa: E402
from openpyxl.worksheet.table import Table, TableStyleInfo  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from catalog_api_sec import API, SEC  # noqa: E402
from catalog_bb_wb import BB, WB  # noqa: E402
from catalog_special import ACC, COMP, GUI, PERF, SEC_MANUAL  # noqa: E402
from defects import AUTOMATION_MAP, DEFECTS, RISKS, STRIDE, TEST_DEFECT, USABILITY  # noqa: E402

RES = os.path.join(ROOT, "07_Test_Management", "results")
OUT_XLSX = os.path.join(ROOT, "07_Test_Management", "PyTodo_Test_Management.xlsx")
REPORT = os.path.join(ROOT, "08_Final_QA_Report")
CHARTS = os.path.join(REPORT, "charts")
os.makedirs(CHARTS, exist_ok=True)
RUN_DATE = date.today().isoformat()

# ------------------------------------------------------------------ parse junit
ID_RE = re.compile(r"(TC[-_](?:BB|WB|API|SEC)[-_]\d{3}|AT[-_]\d{3})")


def parse_junit(path):
    out = {}
    if not os.path.exists(path):
        return out
    for tc in ET.parse(path).getroot().iter("testcase"):
        m = ID_RE.search(tc.get("name", ""))
        if not m:
            continue
        tid = m.group(1).replace("_", "-")
        fail = tc.find("failure") if tc.find("failure") is not None else tc.find("error")
        skip = tc.find("skipped")
        if fail is not None:
            msg = fail.get("message", "")
            act = re.search(r"Actual: (.*?)(?:\nassert|$)", msg, flags=re.S)
            actual = act.group(1).strip() if act else msg.split("\n")[0][:200]
            out[tid] = ("Fail", actual or "Assertion failed (see log)")
        elif skip is not None:
            out[tid] = ("Blocked", "Skipped: " + (skip.get("message") or "")[:120])
        else:
            out[tid] = ("Pass", "As expected")
    return out


core = parse_junit(os.path.join(RES, "junit_core.xml"))
ui = parse_junit(os.path.join(RES, "junit_ui.xml"))
regression_ids = sorted(parse_junit(os.path.join(RES, "junit_regression.xml")))

UI_CASES = [dict(id=a, feature=None, technique="UI automation (Selenium, POM)", objective=desc,
                 pre="App running; Chrome headless; new unique user", data="see script",
                 steps=f"pytest 06_Automation_Regression -m ui -k {a.replace('-', '_')}", expected="See mapped manual case(s)",
                 priority="High", maps=maps) for a, desc, maps, _ in AUTOMATION_MAP]
FEATURE_OF_MANUAL = {c["id"]: c["feature"] for c in BB + GUI}
for c in UI_CASES:
    c["feature"] = FEATURE_OF_MANUAL.get(c["maps"].split(",")[0].strip(), "F05 View/list")

SCRIPT_OF = {}
for prefix, script in [("TC-BB", "01_Black_Box/test_blackbox_web.py"), ("TC-WB", "02_White_Box_Coverage/test_whitebox_helpers.py"),
                       ("TC-API", "04_Web_API/test_api.py"), ("TC-SEC", "05_Security_Performance/test_security.py"),
                       ("AT", "06_Automation_Regression/test_ui_selenium.py")]:
    SCRIPT_OF[prefix] = script

GROUPS = OrderedDict([
    ("Black-box (Wk 1)", BB), ("White-box (Wk 2)", WB), ("GUI & config (Wk 3)", GUI),
    ("Accessibility (Wk 3)", ACC), ("Compatibility (Wk 3)", COMP), ("Web & API (Wk 4)", API),
    ("Security (Wk 5)", SEC + SEC_MANUAL), ("Performance (Wk 5)", PERF), ("UI automation (Wk 6)", UI_CASES),
])

rows, problems = [], []
for group, cases in GROUPS.items():
    for c in cases:
        tid = c["id"]
        if "status" in c:                       # manual / observation case
            status, actual, evidence, defect = c["status"], c["actual"], c["evidence"], c.get("defect", "")
            automated = "No (manual / tool-assisted)"
        else:
            source = ui if tid.startswith("AT") else core
            status, actual = source.get(tid, ("Not Run", "Not executed"))
            prefix = tid.rsplit("-", 1)[0]
            script = SCRIPT_OF[prefix]
            evidence = f"{script}; 07_Test_Management/results/{'pytest_ui_log.txt' if tid.startswith('AT') else 'pytest_core_log.txt'}"
            defect = TEST_DEFECT.get(tid, "") if status == "Fail" else ""
            automated = f"Yes ({script.split('/')[-1]})"
            if status == "Fail" and not defect:
                problems.append(f"{tid} failed but has no defect mapping: {actual}")
            if status == "Pass" and tid in TEST_DEFECT:
                problems.append(f"{tid} passed but is mapped to {TEST_DEFECT[tid]}")
        actual = actual[:1].upper() + actual[1:] if actual else actual
        rows.append(dict(c, group=group, status=status, actual=actual, evidence=evidence, defect=defect,
                         automated=automated, regression="Yes" if tid in regression_ids else "",
                         executed=RUN_DATE if status != "Not Run" else ""))

all_tests_text = " ".join(r["defect"] for r in rows)
for dft in DEFECTS:
    if dft["id"] not in all_tests_text:
        problems.append(f"{dft['id']} is not linked from any failed test")
ids = [r["id"] for r in rows]
dups = [k for k, v in Counter(ids).items() if v > 1]
if dups:
    problems.append(f"duplicate test IDs: {dups}")
if problems:
    print("CONSISTENCY PROBLEMS:\n  " + "\n  ".join(problems))
    sys.exit(1)

# ------------------------------------------------------------------ metrics
def counts(rs):
    c = Counter(r["status"] for r in rs)
    planned = len(rs)
    executed = c["Pass"] + c["Fail"] + c["Blocked"]
    return dict(planned=planned, executed=executed, passed=c["Pass"], failed=c["Fail"], blocked=c["Blocked"],
                not_run=c["Not Run"], execution_rate=round(100 * executed / planned, 1) if planned else 0,
                pass_rate=round(100 * c["Pass"] / executed, 1) if executed else 0)


by_group = OrderedDict((g, counts([r for r in rows if r["group"] == g])) for g in GROUPS)
overall = counts(rows)
sev_order = ["Critical", "Major", "Moderate", "Minor"]
sev = Counter(dft["severity"] for dft in DEFECTS)
pri = Counter(dft["priority"] for dft in DEFECTS)


AREA = {"Registration & login": ["DEF-002", "DEF-004", "DEF-019", "DEF-020"],
        "Access control & security config": ["DEF-005", "DEF-014", "DEF-015"],
        "Task input validation (create/edit)": ["DEF-008", "DEF-009", "DEF-010", "DEF-011", "DEF-013", "DEF-017", "DEF-018"],
        "Search, list & API": ["DEF-006", "DEF-007", "DEF-012", "DEF-016"],
        "Urgency & dashboard rules": ["DEF-001", "DEF-003"],
        "GUI, usability & accessibility": ["DEF-021", "DEF-022", "DEF-023", "DEF-024", "DEF-025"],
        "Performance": ["DEF-026"]}
AREA_OF = {d_: a for a, ds in AREA.items() for d_ in ds}
assert sorted(AREA_OF) == sorted(x["id"] for x in DEFECTS), "every defect needs exactly one area"
feat_defects = Counter(AREA_OF[x["id"]] for x in DEFECTS)
cov_full = json.load(open(os.path.join(RES, "coverage_full.json")))
cov_help = json.load(open(os.path.join(RES, "coverage_helpers.json")))


def cov_line(cj, fname):
    for k, v in cj["files"].items():
        if k.endswith(fname):
            s = v["summary"]
            return dict(statements=s["num_statements"], covered=s["covered_lines"], missing=s["missing_lines"],
                        branches=s["num_branches"], branches_covered=s["covered_branches"],
                        stmt_pct=round(100 * s["covered_lines"] / s["num_statements"], 1),
                        branch_pct=round(100 * s["covered_branches"] / s["num_branches"], 1) if s["num_branches"] else 100.0,
                        combined_pct=round(s["percent_covered"], 1), missing_lines=v.get("missing_lines", []))
    return None


coverage = {"helpers.py (unit tests only)": cov_line(cov_help, "helpers.py"),
            "helpers.py (all suites)": cov_line(cov_full, "helpers.py"),
            "app.py (all suites)": cov_line(cov_full, "app.py")}

perf = OrderedDict()
for u in ["1", "10", "25", "50", "100_stress"]:
    p = os.path.join(ROOT, "05_Security_Performance", "perf_results", f"u{u}_stats.csv")
    if not os.path.exists(p):
        continue
    perf[u] = {r["Name"]: dict(n=int(r["Request Count"]), fail=int(r["Failure Count"]),
                              avg=round(float(r["Average Response Time"]), 1), p95=float(r["95%"]),
                              max=round(float(r["Max Response Time"])), rps=round(float(r["Requests/s"]), 2))
               for r in csv.DictReader(open(p))}

loc_py = sum(1 for f in ["app.py", "helpers.py"] for _ in open(os.path.join(ROOT, "app", f)))
automated_cases = sum(1 for r in rows if r["automated"].startswith("Yes"))
metrics = dict(run_date=RUN_DATE, overall=overall, by_group=by_group,
               defects_total=len(DEFECTS), severity={s: sev.get(s, 0) for s in sev_order},
               priority={p: pri.get(p, 0) for p in ["High", "Medium", "Low"]}, defects_by_feature=dict(feat_defects.most_common()),
               python_loc=loc_py, defect_density_per_kloc=round(len(DEFECTS) / (loc_py / 1000), 1),
               coverage=coverage, performance=perf, automated_cases=automated_cases,
               automation_rate=round(100 * automated_cases / overall["planned"], 1),
               regression_suite_size=len(regression_ids), regression_ids=regression_ids,
               failed_by_group={g: by_group[g]["failed"] for g in by_group})
json.dump(metrics, open(os.path.join(REPORT, "metrics.json"), "w"), indent=2)

# ------------------------------------------------------------------ charts
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#ffffff"
GOOD, CRIT, NEUTRAL = "#0ca30c", "#d03b3b", "#b9b8b2"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": SURF, "axes.facecolor": SURF})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS, name), dpi=200)
    plt.close(fig)


# 1. results by test group (stacked horizontal bars, status colours + labels)
fig, ax = plt.subplots(figsize=(7.2, 3.8))
labels = list(by_group)[::-1]
left = [0] * len(labels)
for key, name, col in [("passed", "Pass", GOOD), ("failed", "Fail", CRIT), ("not_run", "Not Run", NEUTRAL)]:
    vals = [by_group[g][key] for g in labels]
    ax.barh(labels, vals, left=left, color=col, edgecolor=SURF, linewidth=1.5, label=name, height=0.62)
    for i, v in enumerate(vals):
        if v >= 1:
            ax.text(left[i] + v / 2, i, str(v), ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
    left = [a + b for a, b in zip(left, vals)]
ax.set_xlabel("Number of test cases")
ax.xaxis.grid(True, color=GRID, linewidth=0.6); ax.set_axisbelow(True)
ax.legend(ncol=3, frameon=False, loc="lower right", fontsize=9)
ax.set_title(f"Test results by phase ({overall['planned']} test cases)", loc="left", color=INK, fontsize=11, fontweight="bold")
save(fig, "results_by_phase.png")

# 2. defects by severity (single-hue ordinal ramp)
fig, ax = plt.subplots(figsize=(5.2, 2.8))
cols = ["#104281", "#256abf", "#5598e7", "#9ec5f4"]
vals = [sev.get(s, 0) for s in sev_order]
bars = ax.bar(sev_order, vals, color=cols, width=0.6)
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.15, str(v), ha="center", color=INK, fontsize=10)
ax.set_ylabel("Defects"); ax.yaxis.grid(True, color=GRID, linewidth=0.6); ax.set_axisbelow(True)
ax.set_title(f"Defects by severity ({len(DEFECTS)} confirmed)", loc="left", color=INK, fontsize=11, fontweight="bold")
save(fig, "defects_by_severity.png")

# 3. defects by feature (single hue, sorted)
fig, ax = plt.subplots(figsize=(6.4, 3.6))
items = feat_defects.most_common()[::-1]
ax.barh([k for k, _ in items], [v for _, v in items], color="#2a78d6", height=0.6)
for i, (_, v) in enumerate(items):
    ax.text(v + 0.05, i, str(v), va="center", color=INK, fontsize=9)
ax.set_xlabel("Defects"); ax.xaxis.grid(True, color=GRID, linewidth=0.6); ax.set_axisbelow(True)
fig.suptitle("Defects by area: input validation holds the most", x=0.02, ha="left", color=INK, fontsize=11, fontweight="bold")
save(fig, "defects_by_feature.png")

# 4. performance: p95 by load level (one log axis, legend + direct labels)
levels = [u for u in ["1", "10", "25", "50"] if u in perf]
fig, ax = plt.subplots(figsize=(6.6, 3.6))
for name, label, col, dy in [("/api/login", "Login", "#eb6834", 0), ("GET /api/dashboard", "Dashboard", "#1baf7a", 7),
                             ("GET /api/tasks", "Task list", "#2a78d6", -7)]:
    ys = [perf[u].get(name, {}).get("p95", 0) for u in levels]
    ax.plot([int(u) for u in levels], ys, marker="o", markersize=6, linewidth=2, color=col, label=label)
    ax.annotate(f"{label} {ys[-1]:,.0f} ms", (int(levels[-1]), ys[-1]), xytext=(8, dy), textcoords="offset points",
                va="center", color=INK2, fontsize=8.5)
ax.set_yscale("log")
ax.axhline(1000, color=INK2, linestyle="--", linewidth=1)
ax.text(1, 1250, "1,000 ms target", color=INK2, fontsize=8.5)
ax.set_xlabel("Concurrent virtual users"); ax.set_ylabel("95th percentile (ms, log scale)")
ax.set_xticks([int(u) for u in levels]); ax.set_xlim(0, 66)
ax.yaxis.grid(True, color=GRID, linewidth=0.6); ax.set_axisbelow(True)
ax.legend(frameon=False, fontsize=9, loc="center left", bbox_to_anchor=(0.02, 0.62))
ax.set_title("Only login slows down as users increase", loc="left", color=INK, fontsize=11, fontweight="bold")
save(fig, "performance_p95.png")

# ------------------------------------------------------------------ workbook
HEAD = PatternFill("solid", fgColor="1B3A5C")
FILLS = {"Pass": "E3F4E3", "Fail": "FBE3E3", "Not Run": "EEEEEE", "Blocked": "FFF3D6",
         "Critical": "F6C9C9", "Major": "FBE3E3", "Moderate": "FFF3D6", "Minor": "EEF4FB"}
thin = Side(style="thin", color="D0D0D0")
wb = Workbook()


def sheet(title, header, data, widths, status_col=None, extra_fill_col=None, first=False):
    ws = wb.active if first else wb.create_sheet()
    ws.title = title
    ws.append(header)
    for row in data:
        ws.append(list(row))
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF"); cell.fill = HEAD
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = Border(top=thin, bottom=thin, left=thin, right=thin)
        for col in [status_col, extra_fill_col]:
            if col:
                v = row[col - 1].value
                if v in FILLS:
                    row[col - 1].fill = PatternFill("solid", fgColor=FILLS[v])
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = ws.dimensions
    return ws


# Summary sheet
summ = [("Run date", RUN_DATE, "", "", "", "", "", ""),
        ("", "", "", "", "", "", "", ""),
        ("Phase", "Planned", "Executed", "Passed", "Failed", "Blocked", "Not Run", "Pass rate %")]
for g, c in by_group.items():
    summ.append((g, c["planned"], c["executed"], c["passed"], c["failed"], c["blocked"], c["not_run"], c["pass_rate"]))
summ.append(("TOTAL", overall["planned"], overall["executed"], overall["passed"], overall["failed"], overall["blocked"],
             overall["not_run"], overall["pass_rate"]))
summ += [("", "", "", "", "", "", "", ""), ("Execution rate %", overall["execution_rate"], "", "", "", "", "", ""),
         ("Confirmed defects", len(DEFECTS), "", "", "", "", "", "")]
summ += [(f"  Severity {s}", sev.get(s, 0), "", "", "", "", "", "") for s in sev_order]
summ += [("Defect density (defects / KLOC Python)", metrics["defect_density_per_kloc"], f"{loc_py} lines", "", "", "", "", ""),
         ("helpers.py statement / branch coverage %", coverage["helpers.py (unit tests only)"]["stmt_pct"],
          coverage["helpers.py (unit tests only)"]["branch_pct"], "", "", "", "", ""),
         ("app.py statement / branch coverage %", coverage["app.py (all suites)"]["stmt_pct"],
          coverage["app.py (all suites)"]["branch_pct"], "", "", "", "", ""),
         ("Automated test cases / rate %", automated_cases, metrics["automation_rate"], "", "", "", "", ""),
         ("Regression suite size", len(regression_ids), "", "", "", "", "", "")]
ws = sheet("Summary", ["PyTodo Pro QA - Test summary", "", "", "", "", "", "", ""], summ, [42, 12, 12, 10, 10, 10, 10, 12], first=True)
for r in (4, 4 + len(by_group) + 1):
    for cell in ws[r]:
        cell.font = Font(bold=True)

sheet("Test Cases", ["Test Case ID", "Phase", "Feature/Requirement", "Technique/Test Type", "Objective", "Preconditions",
                     "Test Data", "Steps", "Expected Result", "Actual Result", "Status", "Evidence", "Defect ID", "Priority",
                     "Automated", "In regression suite", "Executed on"],
      [(r["id"], r["group"], r["feature"], r["technique"], r["objective"], r["pre"], r["data"], r["steps"], r["expected"],
        r["actual"], r["status"], r["evidence"], r["defect"], r["priority"], r["automated"], r["regression"], r["executed"])
       for r in rows],
      [12, 16, 18, 22, 34, 22, 24, 30, 34, 38, 9, 34, 10, 9, 18, 10, 11], status_col=11)

# RTM
REQS = OrderedDict([
    ("F01 Registration", "Create an account with valid username/password; reject invalid or duplicate"),
    ("F02 Login/Logout", "Log in with correct credentials; log out ends the session"),
    ("F03 Access control", "Only logged-in users; only own tasks"),
    ("F04 Create task", "Title required; optional category and valid due date"),
    ("F05 View/list", "List own tasks newest first; API pagination"),
    ("F06 Edit task", "Edit fields; partial API updates"),
    ("F07 Complete/reopen", "Toggle done; completed_at set/cleared"),
    ("F08 Delete task", "Owner can delete"),
    ("F09 Filter/search", "Filter by category/status; search title"),
    ("F10 Urgency", "Correct urgency label for every due date"),
    ("F11 Dashboard", "Correct counters incl. inclusive 7-day rule"),
    ("F12 Categories", "Four seeded categories via API"),
    ("NF2 Performance", "Acceptable response time under expected load"),
    ("NF3 GUI", "Consistent, clear interface with feedback"),
    ("NF4 Accessibility", "WCAG 2.1 A/AA basics"),
    ("NF5 Compatibility", "Works on target browsers and screen sizes"),
])
rtm = []
for req, desc in REQS.items():
    rs = [r for r in rows if r["feature"] == req]
    if req == "F03 Access control":
        rs += [r for r in rows if r["id"] in ("TC-SEC-002", "TC-SEC-003")]
    techs = sorted({r["technique"].split(" (")[0] for r in rs})
    passed = sum(r["status"] == "Pass" for r in rs)
    executed = sum(r["status"] in ("Pass", "Fail", "Blocked") for r in rs)
    dfs = sorted({r["defect"] for r in rs if r["defect"]})
    result = "No tests" if not rs else ("Not run" if executed == 0 else f"{passed}/{executed} passed")
    rtm.append((req, desc, ", ".join(r["id"] for r in rs), "; ".join(techs), result, ", ".join(dfs),
                "Covered" if executed else "GAP"))
sheet("RTM", ["Requirement/Feature", "Test Scenario (expected behaviour)", "Test Case ID(s)", "Test Type/Technique",
              "Result", "Defect ID", "Coverage"], rtm, [20, 36, 60, 40, 14, 26, 10])

sheet("Defect Log", ["Defect ID", "Title", "Affected Feature", "Environment", "Preconditions", "Steps to Reproduce",
                     "Expected Result", "Actual Result", "Severity", "Priority", "Evidence", "Status", "Found by test(s)",
                     "Likely root cause (static review)", "Found in"],
      [(x["id"], x["title"], x["feature"], x["env"], x["pre"], x["steps"], x["expected"], x["actual"], x["severity"],
        x["priority"], x["evidence"], x["status"], x["tests"], x["origin"], x["found"]) for x in DEFECTS],
      [10, 40, 22, 26, 22, 40, 30, 36, 10, 9, 34, 11, 26, 36, 9], status_col=9)

score = lambda l, i: l * i  # noqa: E731
sheet("Risk Register", ["Risk ID", "Product risk", "Feature", "Likelihood (Wk 1)", "Impact", "Score (Wk 1)",
                        "Likelihood (final, after testing)", "Score (final)", "Level (final)", "Evidence / defects",
                        "Mitigation / next test"],
      [(r[0], r[1], r[2], r[3], r[4], score(r[3], r[4]), r[5], score(r[5], r[4]),
        "High" if score(r[5], r[4]) >= 6 else ("Medium" if score(r[5], r[4]) >= 3 else "Low"), r[6], r[7]) for r in RISKS],
      [8, 40, 12, 11, 8, 10, 14, 10, 10, 26, 40])

sheet("STRIDE", ["Asset / function", "STRIDE category", "Threat", "Property violated", "Test(s)", "Result",
                 "Mitigation"], STRIDE, [22, 20, 44, 16, 22, 26, 34])

sheet("Automation Map", ["Script ID", "What it automates", "Manual test case(s)", "Why chosen for automation", "Result",
                         "In regression suite"],
      [(a, d_, m, why, ui.get(a, ("Not Run",))[0], "Yes" if a in regression_ids else "") for a, d_, m, why in AUTOMATION_MAP],
      [10, 32, 26, 40, 10, 12], status_col=5)

reg_rows = [(r["id"], r["group"], r["objective"], r["status"], r["defect"]) for r in rows if r["id"] in regression_ids]
sheet("Regression Suite", ["Test ID", "Phase", "What it checks", "Last result", "Defect ID"], reg_rows, [12, 20, 50, 10, 10],
      status_col=4)

sheet("Coverage", ["Scope", "Statements", "Covered", "Missing", "Branches", "Branches covered", "Statement %",
                   "Branch %", "Missing lines (first 40)"],
      [(k, v["statements"], v["covered"], v["missing"], v["branches"], v["branches_covered"], v["stmt_pct"], v["branch_pct"],
        ", ".join(map(str, v["missing_lines"][:40]))) for k, v in coverage.items()],
      [28, 11, 10, 10, 10, 12, 11, 10, 60])

perf_rows = []
for u, d_ in perf.items():
    for name, v in d_.items():
        perf_rows.append((u.replace("_stress", " (stress, ramp 10/s)"), name, v["n"], v["fail"], v["avg"], v["p95"], v["max"], v["rps"]))
sheet("Performance", ["Users", "Request", "Requests", "Failures", "Average ms", "95th pct ms", "Max ms", "Requests/s"],
      perf_rows, [22, 22, 10, 10, 11, 11, 10, 11])

sheet("Usability (LEMES)", ["Nielsen dimension", "Type", "Observation"], USABILITY, [16, 10, 100])

sheet("Compatibility Matrix", ["Browser / OS", "Desktop 1366x768", "Tablet 768x1024", "Phone 375x812", "Test ID", "Notes"],
      [("Chrome 153 / Linux (headless)", "Pass", "Pass", "Fail (DEF-023)", "TC-COMP-001, TC-GUI-012..014",
        "Automated smoke set + screenshots"),
       ("Chrome / Windows 11", "Not Run", "Not Run", "Not Run", "TC-COMP-002", "Group laptop: HEADED=1 pytest -m ui"),
       ("Edge / Windows 11", "Not Run", "Not Run", "Not Run", "TC-COMP-003", "Group laptop"),
       ("Firefox / Windows 11", "Not Run", "Not Run", "Not Run", "TC-COMP-004", "Group laptop"),
       ("Safari / macOS", "Not Run", "Not Run", "Not Run", "TC-COMP-005", "If a member has a Mac")],
      [30, 16, 16, 16, 26, 36])

wb.save(OUT_XLSX)
print(json.dumps({"overall": overall, "defects": len(DEFECTS), "severity": metrics["severity"],
                  "coverage": {k: (v["stmt_pct"], v["branch_pct"]) for k, v in coverage.items()},
                  "regression": len(regression_ids), "automated": automated_cases}, indent=1))

# ------------------------------------------------------------------ data for the Word report
report_data = dict(metrics=metrics, rows=rows, defects=DEFECTS, rtm=rtm, stride=STRIDE, usability=USABILITY,
                   automation=[(a, d_, m, why, ui.get(a, ("Not Run",))[0]) for a, d_, m, why in AUTOMATION_MAP],
                   risks=[(r[0], r[1], r[2], r[3], r[4], r[3] * r[4], r[5], r[5] * r[4], r[6], r[7]) for r in RISKS],
                   area=AREA)
json.dump(report_data, open(os.path.join(REPORT, "report_data.json"), "w"), indent=1, default=str)
