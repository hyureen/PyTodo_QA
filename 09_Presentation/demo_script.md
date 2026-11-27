# Live demo script (about 5 minutes)

**Before the presentation**
- Fresh copy of the repo on two laptops; `pip install` done; Chrome installed.
- Delete `app/pytodo_pro.db`, then start the app: `cd app && python app.py`.
- Open three things: the browser at http://127.0.0.1:5000, a terminal at the repo root, and the workbook `07_Test_Management/PyTodo_Test_Management.xlsx`.
- Backup: record this demo once as a video, and keep the screenshots in `06_Automation_Regression/evidence/`.

| # | Who | Show | Say (one line) |
| --- | --- | --- | --- |
| 1 | Member 2 | Register `demo_user` with password `abcdefgh` (8 characters) | "The rule says at least 8, but 8 is rejected: BVA found this (DEF-002)." |
| 2 | Member 2 | Register with `abcdefghi`, create task due **today** | "Due today shows Overdue, not Due Today (DEF-001)." |
| 3 | Member 3 | Terminal: `pytest -m unit -v` then open `htmlcov` | "100% branch coverage, yet 3 tests fail: coverage is not correctness." |
| 4 | Member 3 | Terminal: `pytest 04_Web_API -k "042" -v` | "The API lets one user delete another user's task (DEF-005)." |
| 5 | Member 4 | Terminal: `pytest 05_Security_Performance -k "SEC_003 or SEC_010" -v` | "Forged cookie and SQL injection both expose another user's tasks." |
| 6 | Member 3 | Terminal: `HEADED=1 pytest -m ui -k "AT_005 or AT_004" -v` | "Selenium with the Page Object Model runs our critical flows." |
| 7 | Nureen | Workbook: RTM sheet, then Defect Log | "Every requirement traces to tests, every failure to a defect." |
| 8 | Member 4 | Report Figure 6 (performance chart) | "Normal pages stay fast; only login slows when 25+ users log in at once." |

**Safety note:** show security results from the test output; do not type attack payloads live in the browser.

**Likely questions to prepare (one per member)**
- Why 3-value BVA instead of 2-value? (Member 2)
- What does V(G) = 5 mean, and why do tests still fail at 100% coverage? (Member 3)
- What is the difference between 401 and 403, and which did you expect where? (Member 3)
- Which STRIDE property does DEF-006 break, and how would you fix it? (Member 4)
- Why is the pass rate only 71% – is that bad testing? (Nureen)
- How would these tests fit into CI/CD? (Nureen)
