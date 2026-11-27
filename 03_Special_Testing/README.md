# Week 3 – GUI, Compatibility, Usability and Accessibility

**Result:** GUI 15 planned, 15 executed, **11 passed, 4 failed**; accessibility 11 planned, 11 executed, **6 passed, 5 failed**;
compatibility 5 planned, 1 executed, **1 passed, 0 failed**, 4 not run.

| Brief deliverable | Where to find it |
| --- | --- |
| GUI testing checklist / results | [Special_Testing_Results.xlsx](Special_Testing_Results.xlsx) sheet *GUI checklist* |
| Compatibility / configuration matrix | sheet *Compatibility*; [compatibility_checklist.md](compatibility_checklist.md) for manual runs |
| Usability observations | sheet *Usability (LEMES)*; [Special_Testing_Findings.md](Special_Testing_Findings.md) |
| Basic accessibility findings | sheet *Accessibility*; Axe output [audit_results.json](audit_results.json) |
| Defects and improvement recommendations | [Special_Testing_Findings.md](Special_Testing_Findings.md) |
| Screenshots (7 pages × 3 screen sizes) | [screenshots/](screenshots/) |

**Re-run the audit** (app running, `npm install axe-core`): `python 03_Special_Testing/gui_a11y_audit.py node_modules/axe-core/axe.min.js`
