# Black-box test design (Week 1)

## 1. Application overview
PyTodo Pro is a Flask + SQLite web app. A registered user creates, categorises, searches, completes and deletes
personal tasks with optional due dates. Each task gets an urgency label and a dashboard shows totals. The same
functions are offered as a JSON REST API. There is one user type (registered user); each user must only see and
change their own tasks.

## 2. Feature inventory
| ID | Feature | Business rule |
| --- | --- | --- |
| F01 | Registration | Username 3–20 chars (letters, digits, _); password at least 8 chars |
| F02 | Login / logout | Correct credentials start a session; logout ends it |
| F03 | Access control | Logged out: redirect / 401; users reach only their own tasks |
| F04 | Create task | Title required; category and due date (YYYY-MM-DD) optional |
| F05 | View / list | Newest first; API pages with page, per_page |
| F06 | Edit task | Edit fields; API partial update |
| F07 | Complete / reopen | completed_at set when done, cleared when reopened |
| F08 | Delete task | Owner only |
| F09 | Filter / search | Category, status; search part of title |
| F10 | Urgency | No due date, Overdue, Due Today, Due Soon (1–2 days), Upcoming (3+), Done |
| F11 | Dashboard | Total, Open, Overdue, Due Soon, Completed last 7 days (inclusive) |
| F12 | Categories | Work, Personal, Study, Urgent |

## 3. Initial test scope / risk matrix (before testing)
Risk score = likelihood × impact (1–3 each). High ≥ 6, Medium 3–4, Low ≤ 2.

| Feature | Likelihood | Impact | Score | Priority | Reason |
| --- | --- | --- | --- | --- | --- |
| F03 Access control / F08 Delete | 2 | 3 | 6 | High | Privacy of every user |
| F04 / F06 validation | 2 | 3 | 6 | High | Bad data could corrupt tasks |
| F09 Search / filter | 2 | 3 | 6 | High | User text reaches database queries |
| F10 Urgency / F11 Dashboard | 2 | 2 | 4 | Medium | Date boundaries easy to get wrong |
| F01 Registration / F02 Login | 2 | 2 | 4 | Medium | Gate to the app |
| F05 List, F07 Toggle | 1 | 2 | 2 | Low | Simple display logic |
| F12 Categories | 1 | 1 | 1 | Low | Read-only seeded list |

The final (after-testing) ratings are in the Risk Register sheet of `07_Test_Management/PyTodo_Test_Management.xlsx`.

## 4. Equivalence partitioning
| Input | Valid classes | Invalid classes | Test cases |
| --- | --- | --- | --- |
| Username length | 3–20 | < 3; > 20 | TC-BB-001..006 |
| Username characters | letters, digits, _ | space, symbols | TC-BB-007, 008 |
| Password length | ≥ 8 | < 8; empty | TC-BB-009..012 |
| Task title | text; special characters | empty; spaces only | TC-BB-021..024, 048 |
| Due date | valid date; none | impossible date | TC-BB-021, 022, 049 |
| Search text | partial match; no match; apostrophe | – | TC-BB-041, 042, 044 |

## 5. Boundary value analysis (3-value)
| Step | Username length | Password length | Days until due date |
| --- | --- | --- | --- |
| Partitions | 0–2 / 3–20 / 21+ | 0–7 / 8+ | ≤ −1 / 0 / 1–2 / 3+ |
| Boundaries | 3, 20 | 8 | 0, 1, 2, 3 |
| Coverage items | 2, 3, 4, 19, 20, 21 | 7, 8, 9 | −1, 0, 1, 2, 3 |
| Test cases | TC-BB-001..006 | TC-BB-009..011 | TC-BB-025..029 |
| Result | All pass | 8 fails (DEF-002) | 0 fails (DEF-001) |

## 6. Decision tables
**Registration** (C1 username valid, C2 password valid, C3 username not taken; 2³ = 8 rules simplified to 4):

|  | R1 | R2 | R3 | R4 |
| --- | --- | --- | --- | --- |
| C1 Username valid | Y | Y | Y | N |
| C2 Password valid | Y | Y | N | – |
| C3 Not taken | Y | N | – | – |
| Action | Create account | 'Username taken' | Password error | Username error |
| Test case | TC-BB-013 | TC-BB-014 | TC-BB-015 | TC-BB-016 |
| Result | Pass | Fail (DEF-004) | Pass | Pass |

**Login** (C1 user exists, C2 password correct; 2² = 4 rules simplified to 3): R1 Y/Y log in (TC-BB-017), R2 Y/N error
(TC-BB-018), R3 N/– same error (TC-BB-019). All pass.

## 7. State transitions
| State | toggle | delete | edit | Tests |
| --- | --- | --- | --- | --- |
| Open | → Done, set completed_at | → Deleted | → Open | TC-BB-032, 034, 047 |
| Done | → Open, clear completed_at | → Deleted | → Done | TC-BB-033 |
| Deleted | invalid (refused) | – | invalid (refused) | TC-BB-035, 036 |

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
| Test | Objective | Actual | Defect |
| --- | --- | --- | --- |
| TC-BB-010 | Password of exactly 8 characters (minimum) is accepted | 8-character password refused with 'Password must be at least 8 characters.' | DEF-002 |
| TC-BB-014 | Valid username + valid password + username already taken -> rejected | Duplicate username 'dt_taken' was registered again (HTTP 302 to /) | DEF-004 |
| TC-BB-020 | When two accounts share a username, the second account can still log in with its own password | Second 'dup_user' account was created but cannot log in ('Invalid username or password.') | DEF-004 |
| TC-BB-023 | Title of only spaces is rejected (server-side check) | Task with an empty title was created (blank row in My Tasks) | DEF-009 |
| TC-BB-024 | Title with special characters is shown exactly as typed | Title inserted as raw HTML; '<urgent>' becomes an HTML tag and is not shown | DEF-007 |
| TC-BB-026 | Task due today shows 'Due Today' | Badge 'Overdue' | DEF-001 |
| TC-BB-046 | A task due today is not counted as Overdue | Overdue = 1 | DEF-001 |
| TC-BB-048 | Editing a title to spaces is rejected | Title changed to '' (empty) | DEF-009 |
| TC-BB-049 | Server rejects an impossible due date sent from the form | Task was saved and My Tasks now returns HTTP 500 (Internal Server Error) | DEF-008 |
