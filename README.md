# PyTodo Pro – Independent Software Quality Assurance Evaluation

**Course:** TEB3433 / TFB3433 Software Testing and Quality Assurance · September 2026
**Lecturer:** Dr. Abdullateef Oluwagbemiga Balogun
**System under test:** PyTodo Pro (Flask + SQLite task manager), as issued. The application code in `app/` was **not modified**.

## Team

| Name | Student ID | Coordination role |
| --- | --- | --- |
| Nureen [full name] | [ID] | QA / Test Lead |
| [Name] | [ID] | Test Design Coordinator |
| [Name] | [ID] | Automation / Tool Coordinator |
| [Name] | [ID] | Defect & Metrics Coordinator |

All members designed and executed tests in every phase.

## Results at a glance

| Measure | Result |
| --- | --- |
| Test cases planned / executed | 184 / 180 (97.8%) |
| Passed / failed / not run | 128 / 52 / 4 (compatibility cases on members' laptops) |
| Confirmed defects | 26 – 5 Critical, 5 Major, 7 Moderate, 9 Minor |
| `helpers.py` coverage | 100% statement, 100% branch |
| `app.py` coverage | 98.3% statement, 89.1% branch |
| Regression suite | 52 tests (`pytest -m regression`) |
| Verdict | Not ready for release until Critical/Major defects are fixed |

📄 **Final report:** [`08_Final_QA_Report/PyTodo_Pro_Final_QA_Report.docx`](08_Final_QA_Report/PyTodo_Pro_Final_QA_Report.docx)
📊 **Master test repository, RTM, defect log, risks:** [`07_Test_Management/PyTodo_Test_Management.xlsx`](07_Test_Management/PyTodo_Test_Management.xlsx)

## Where each weekly deliverable is

Every folder has its own `README.md` mapping the brief's "Deliverable Contents" to files.

| Folder | Week | Main contents |
| --- | --- | --- |
| [`00_Smoke/`](00_Smoke/) | – | Lead's first exploratory smoke test |
| [`01_Black_Box/`](01_Black_Box/) | 1 | Feature inventory, risk matrix, EP/BVA/decision-table/state-transition design, 49 test cases, PyTest suite |
| [`02_White_Box_Coverage/`](02_White_Box_Coverage/) | 2 | Unit selection, control flow graphs, V(G), 29 unit tests, HTML coverage reports |
| [`03_Special_Testing/`](03_Special_Testing/) | 3 | GUI checklist, compatibility matrix, usability (LEMES), WCAG/Axe findings, 21 screenshots |
| [`04_Web_API/`](04_Web_API/) | 4 | Web scenarios, 46 API tests, expected vs actual status, UI vs API comparison |
| [`05_Security_Performance/`](05_Security_Performance/) | 5 | STRIDE table, 14 security tests, Locust workload and results |
| [`06_Automation_Regression/`](06_Automation_Regression/) | 6 | Selenium + Page Object Model, manual-to-automated map, regression suite, reflection |
| [`07_Test_Management/`](07_Test_Management/) | 7 | Test Plan & Strategy, RTM, master repository, defect log, execution logs |
| [`08_Final_QA_Report/`](08_Final_QA_Report/) | 8 | Final report, metrics, charts |
| [`09_Presentation/`](09_Presentation/) | 9 | Standards integration pointers, demo script, slides |
| [`tools/`](tools/) | – | Test catalogue and scripts that rebuild all documents from the real results |
| [`.github/workflows/qa.yml`](.github/workflows/qa.yml) | 9 | Example CI/CD pipeline with quality gates |

## Setup

Python 3.11+ and Google Chrome are needed.

```bash
python -m venv venv
venv\Scripts\activate                    # Mac/Linux: source venv/bin/activate
pip install -r app/requirements.txt
pip install -r requirements-test.txt
```

## Running the automated tests

```bash
pytest -m "not ui"            # black-box, white-box, API, security (no server needed): 100 pass, 37 fail
pytest -m unit --cov=app --cov-branch --cov-report=html     # unit tests + coverage
pytest -m regression          # focused regression suite
```

Selenium UI tests need the app running in a second terminal:

```bash
cd app && python app.py       # serves http://127.0.0.1:5000
pytest -m ui -v               # Windows: set HEADED=1 to watch; set BROWSER=edge or firefox for other browsers
```

Extras: GUI/accessibility audit `python 03_Special_Testing/gui_a11y_audit.py node_modules/axe-core/axe.min.js`
(needs `npm install axe-core`) · load test `bash 05_Security_Performance/run_perf.sh` · rebuild every document
from fresh results `bash tools/run_all.sh`.

## Troubleshooting

- `This version of ChromeDriver only supports Chrome version X` → update Chrome, or delete the old `chromedriver` on your PATH.
- UI tests **skipped** → the app is not running on http://127.0.0.1:5000.
- My Tasks shows an error page → the database holds an invalid date from a manual test (that is DEF-008). Stop the app, delete `app/pytodo_pro.db`, start again.

## Conventions

- Test case IDs: `TC-BB`, `TC-WB`, `TC-GUI`, `TC-ACC`, `TC-COMP`, `TC-API`, `TC-SEC`, `TC-PERF` + 3 digits; Selenium scripts `AT-###`; defects `DEF-###`.
- Each test function or parameter id carries its test case ID, so every result traces to the RTM.

## Note on results

**Some tests are expected to fail.** Each failing test documents a confirmed defect linked to a `DEF-###`. When the
developers fix a defect, its test should turn green (confirmation testing) and the rest should stay green (regression
testing). Testing shows the presence of defects, not their absence. All security tests run only against a temporary
local database.
