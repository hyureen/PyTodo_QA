# Web and API testing (Week 4)

## 1. Web scenarios
1. Register → log in → create task → complete → filter → dashboard → log out (TC-BB-013..045, AT-001..009).
2. Logged-out user opens a protected page → redirect to /login (TC-BB-037); after logout the dashboard is closed (TC-BB-038).
3. Client vs server validation: same bad data through the browser and directly to the server (§3).

## 2. Endpoints
| Endpoint | Auth | Tests |
| --- | --- | --- |
| POST /api/register | No | TC-API-001..006 |
| POST /api/login | No | TC-API-007..009 |
| GET /api/categories | Yes (README) | TC-API-011, 012 |
| GET /api/tasks | Yes | TC-API-010, 025..033 |
| POST /api/tasks | Yes | TC-API-013..021 |
| GET /api/tasks/{id} | Yes | TC-API-022..024 |
| PUT /api/tasks/{id} | Yes | TC-API-034..039 |
| DELETE /api/tasks/{id} | Yes | TC-API-040..043 |
| GET /api/dashboard | Yes | TC-API-044..046 |

## 3. UI versus server behaviour
| Input | Browser | Server / API | Verdict |
| --- | --- | --- | --- |
| Empty title | Blocked by `required` (AT-010) | Saved via form post / API PUT (TC-BB-023, TC-API-035) | DEF-009 |
| Impossible date | Date picker prevents it | Saved, then 500 on every list (TC-BB-049, TC-API-017) | DEF-008 |
| Apostrophe in search | Works (TC-BB-044) | 500 (TC-API-033) | DEF-006 |
| Delete other user's task | Not possible | Possible (TC-API-042) | DEF-005 |

## 4. Failed cases (expected vs actual)
| Test | Objective | Actual | Defect |
| --- | --- | --- | --- |
| TC-API-005 | Duplicate username is rejected | HTTP 201, body {'id': 2, 'username': 'api_dup'} | DEF-004 |
| TC-API-006 | Number as username is rejected cleanly | HTTP 500, body '<!doctype html>\n<html lang=en>\n<title>500 Internal Server Er' | DEF-018 |
| TC-API-011 | Categories need login (README: all except register/login) | HTTP 200, body [{'id': 2, 'name': 'Personal'}, {'id': 3, 'name': 'Study'}, {'id': 4, 'name': 'Urgent'}, {'id': 1, 'name': 'Work'}] | DEF-016 |
| TC-API-016 | Number as title is handled cleanly | HTTP 500, body '<!doctype html>\n<html lang=en>\n<title>500 Internal Server Er' | DEF-018 |
| TC-API-017 | Impossible date is rejected | HTTP 500, body '<!doctype html>\n<html lang=en>\n<title>500 Internal Server Er' | DEF-008 |
| TC-API-018 | Wrong date format is rejected | HTTP 500, body '<!doctype html>\n<html lang=en>\n<title>500 Internal Server Er' | DEF-008 |
| TC-API-019 | Unknown category id is rejected | HTTP 201, body {'category': None, 'category_id': 999, 'completed_at': None, 'created_at': '2026-11-21T02:30:34.796603', 'description': '', 'done': False, 'due_date': None, 'id': 1, 'title': 'x', 'urgency': 'No due date'} | DEF-011 |
| TC-API-020 | Non-JSON body gets a clear error | HTTP 400, body {'error': 'title is required'} | DEF-017 |
| TC-API-021 | Very long title is limited | HTTP 201, body {'category': None, 'category_id': None, 'completed_at': None, 'created_at': '2026-11-21T02:30:35.010326', 'description': '', 'done': False, 'due_date': None, 'id': 1, 'title': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'urgency': 'No due date'} (title of 5,000 characters stored) | DEF-013 |
| TC-API-027 | Negative page is rejected | HTTP 200, body [{'category': None, 'category_id': None, 'completed_at': None, 'created_at': '2026-11-21T02:30:35.779610', 'description': '', 'done': False, 'due_date': None, 'id': 1, 'title': 'Sample task', 'urgency': 'No due date'}] | DEF-012 |
| TC-API-028 | per_page=0 is rejected | HTTP 200, body [] | DEF-012 |
| TC-API-033 | Search with an apostrophe works like the web UI | HTTP 500, body '<!doctype html>\n<html lang=en>\n<title>500 Internal Server Er' | DEF-006 |
| TC-API-035 | PUT empty title is rejected | HTTP 200, body {'category': None, 'category_id': None, 'completed_at': None, 'created_at': '2026-11-21T02:30:36.576915', 'description': '', 'done': False, 'due_date': None, 'id': 1, 'title': '', 'urgency': 'No due date'} | DEF-009 |
| TC-API-036 | done='false' (string) is not treated as true | HTTP 200, done = True (task marked complete) | DEF-010 |
| TC-API-039 | PUT impossible date is rejected | HTTP 500, body '<!doctype html>\n<html lang=en>\n<title>500 Internal Server Er' | DEF-008 |
| TC-API-041 | Delete unknown id returns 404 | HTTP 200, body {'result': 'ok'} | DEF-005 |
| TC-API-042 | Cannot delete another user's task | HTTP 200 {'result': 'ok'} and qa_user2's task was deleted | DEF-005 |
| TC-API-045 | Task due today not counted as overdue | {'completed_this_week': 0, 'due_soon': 0, 'open': 1, 'overdue': 1, 'total': 1} | DEF-001 |
