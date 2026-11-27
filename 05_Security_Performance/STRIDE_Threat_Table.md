# STRIDE threat table (Week 5)

Steps: decompose the app into assets and data flows → apply STRIDE → decide mitigations → derive safe tests.

| Asset / function | STRIDE | Threat | Property | Test(s) | Result | Mitigation |
| --- | --- | --- | --- | --- | --- | --- |
| Login / session cookie | Spoofing | Attacker forges a session cookie using the secret in the source code | Authenticity | TC-SEC-002, TC-SEC-003 | Forgery works (DEF-014) | Secret from environment variable; rotate key |
| Login | Spoofing | Password guessing with unlimited attempts | Authenticity | TC-SEC-004 | No limit (DEF-019) | Rate limiting / lockout |
| Logout | Spoofing | Stolen cookie replayed after the user logs out | Authenticity | TC-SEC-005 | Still valid (DEF-020) | Server-side sessions or short expiry |
| Task API (PUT/DELETE) | Tampering | User changes or deletes another user's task | Integrity | TC-SEC-007, TC-SEC-008 | PUT safe; DELETE unsafe (DEF-005) | Check ownership on every query |
| Web forms | Tampering | Cross-site request forges delete/toggle | Integrity | TC-SEC-006 | Accepted (DEF-015) | CSRF tokens (Flask-WTF), SameSite cookies |
| Task list page | Tampering | Stored script in title runs in viewer's browser (XSS) | Integrity | TC-SEC-012 | Rendered (DEF-007) | Remove /safe; output encoding |
| All actions | Repudiation | User denies deleting or changing a task; no audit trail | Non-repudiation | Code review (no logging in app.py) | No audit log (observation) | Log who changed what and when |
| Task search | Information disclosure | SQL injection returns other users' tasks | Confidentiality | TC-SEC-010 | Leaks data (DEF-006) | Parameterised queries |
| Task API (GET) | Information disclosure | Reading another user's task by id | Confidentiality | TC-SEC-009, TC-API-024 | Protected (404) | Keep user_id scoping |
| Error pages | Information disclosure | Debugger shows code and paths | Confidentiality | TC-SEC-013 | Exposed (DEF-014) | debug=False; generic error page |
| User table | Information disclosure | Passwords readable if DB is copied | Confidentiality | TC-SEC-011 | Hashed (scrypt) | Keep hashing |
| Task list / dashboard | Denial of service | One invalid date makes the user's pages crash | Availability | TC-API-017, TC-BB-049 | Crashes (DEF-008) | Validate dates; handle errors |
| Login | Denial of service | Burst of logins slows the server | Availability | TC-PERF-003/004 | Slow > 1 s (DEF-026) | Rate limiting; production WSGI server |
| Edit page / API | Elevation of privilege | Normal user acts on another user's resources | Authorization | TC-SEC-014, TC-SEC-008 | Edit page safe; API delete unsafe (DEF-005) | Consistent authorization checks |

## Security failures
| Test | Objective | Actual | Defect |
| --- | --- | --- | --- |
| TC-SEC-003 | Knowing the source code does not let an attacker forge a session | HTTP 200; forged cookie accepted and attacker read ['qa_user2 secret plan'] | DEF-014 |
| TC-SEC-004 | Repeated wrong passwords are limited | 10 wrong attempts all returned {401}; 11th (correct) returned 200; no limit | DEF-019 |
| TC-SEC-005 | Session cookie stops working after logout | HTTP 200; old cookie still works after logout | DEF-020 |
| TC-SEC-006 | Cross-site form post without a CSRF token is refused | HTTP 302; cross-site request without token deleted the task | DEF-015 |
| TC-SEC-008 | User A cannot delete User B's task | Qa_user1 deleted qa_user2's task | DEF-005 |
| TC-SEC-010 | Search input cannot change the SQL query (injection) | HTTP 200; injected condition returned other user's data: ['B confidential', 'A task'] | DEF-006 |
| TC-SEC-012 | HTML in a task title is escaped, not executed | Title rendered as live HTML (script would run) | DEF-007 |
| TC-SEC-013 | Error pages do not show the stack trace or debugger | Werkzeug Debugger page with full traceback, file paths and code | DEF-014 |
