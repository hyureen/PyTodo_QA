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
| Criterion | Target | Actual |
| --- | --- | --- |
| High-priority cases executed | 100% | 90/91 |
| All cases executed | ≥ 90% | 97.8% |
| Failed cases linked to defects | 100% | 100% |
| helpers.py branch coverage | ≥ 90% | 100.0% |
| app.py statement coverage | ≥ 70% | 98.3% |
| Every feature has an executed test | 100% | 100% |
| Release: open Critical defects | 0 | 5 (not ready to release) |

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
