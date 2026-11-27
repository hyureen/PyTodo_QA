# Compatibility smoke checklist (TC-COMP-002 to TC-COMP-005)

Use this if the automated run (`set BROWSER=edge` / `firefox`) does not work, or to double-check by hand.
Run once per browser. Start each browser test with a fresh database (stop the app, delete `app/pytodo_pro.db`, start again).

**Tester:** ________  **Date:** ________  **Laptop OS + version:** ________
**Browser + exact version** (Chrome: `chrome://version`, Edge: `edge://version`, Firefox: Menu → Help → About):  ________

| # | Step | Expected | Actual (OK / what happened) | Screenshot name |
| --- | --- | --- | --- | --- |
| 1 | Open http://127.0.0.1:5000 | Redirects to Log in page, layout looks normal | | TC-COMP-00X_01_login.png |
| 2 | Register `comp_user1` / `Passw0rd123` | Lands on My Tasks | | |
| 3 | + New Task: "Buy milk", category Personal, due date = **today + 5** (use the date picker) | Date picker opens and works; task shows "Upcoming" | | TC-COMP-00X_03_datepicker.png |
| 4 | + New Task: "Lab report", due **today** | Known defect: shows "Overdue" (DEF-001) – record what you see | | TC-COMP-00X_04_due_today.png |
| 5 | Click ○ next to "Buy milk" | ✓ and "Done", title struck through | | |
| 6 | Choose category **Personal** in the filter | Only Personal tasks listed | | |
| 7 | Click Delete on "Lab report" → OK in the dialog | Confirm dialog appears; task removed | | |
| 8 | Open Dashboard | Counts shown in 5 cards, layout not broken | | TC-COMP-00X_08_dashboard.png |
| 9 | Press F12 → device toolbar (Ctrl+Shift+M) → iPhone size → open My Tasks | Known defect: table scrolls sideways (DEF-023) – record what you see | | TC-COMP-00X_09_phone.png |
| 10 | Log out | Back to Log in page | | |

**Result:** Pass if steps 1–3, 5–8 and 10 work (steps 4 and 9 are known defects and do not fail this compatibility test unless they look *different* from Chrome).
**Overall status:** Pass / Fail   **Notes (anything that looks different from Chrome):** ____________________
