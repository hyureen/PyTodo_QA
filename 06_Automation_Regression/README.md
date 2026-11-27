# Week 6 – Test Automation and Regression

**Result:** Selenium 10 planned, 10 executed, **7 passed, 3 failed**. 147 of 184 test cases automated
(79.9%). Regression suite: 52 tests.

| Brief deliverable | Where to find it |
| --- | --- |
| Automation candidate justification | [Automation_Reflection.md §1](Automation_Reflection.md) |
| Automated scripts | [test_ui_selenium.py](test_ui_selenium.py), [pages.py](pages.py) (Page Object Model) + PyTest suites in 01, 02, 04, 05 |
| Manual-to-automated traceability | [Automation_Traceability.xlsx](Automation_Traceability.xlsx) |
| Execution report / logs | `07_Test_Management/results/pytest_ui_log.txt`, `pytest_regression_log.txt`, `junit_*.xml`; screenshots [evidence/](evidence/) |
| Regression suite and automation reflection | `pytest -m regression`; [Automation_Reflection.md §2–3](Automation_Reflection.md) |

**Run UI tests** (app running): `pytest -m ui -v` · other browsers: `set BROWSER=edge` / `firefox` · watch: `set HEADED=1`
