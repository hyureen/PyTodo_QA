# Week 3 findings and recommendations

Method: Selenium opened every page in Chrome at desktop (1366×768), tablet (768×1024) and phone (375×812) sizes
and saved screenshots; the Axe engine checked WCAG 2.1 A/AA rules; keyboard order was checked; screens were reviewed
against a GUI checklist and Nielsen's LEMES dimensions.

## Compatibility / configuration matrix
| Browser / OS | Desktop | Tablet | Phone | Test |
| --- | --- | --- | --- | --- |
| Chrome 153 / Linux | Pass | Pass | Fail (DEF-023) | TC-COMP-001, TC-GUI-012..014 |
| Chrome / Windows 11 | Not Run | Not Run | Not Run | TC-COMP-002 |
| Edge / Windows 11 | Not Run | Not Run | Not Run | TC-COMP-003 |
| Firefox / Windows 11 | Not Run | Not Run | Not Run | TC-COMP-004 |
| Safari / macOS | Not Run | Not Run | Not Run | TC-COMP-005 (no Mac in group) |

## Failed checks
| Test | Check | Actual | Defect |
| --- | --- | --- | --- |
| TC-GUI-008 | Each urgency label has its own badge style | 'Due Today' never appears; task due today shows red 'Overdue' | DEF-001 |
| TC-GUI-011 | User gets a confirmation after create / edit / delete | No message; page silently reloads | DEF-024 |
| TC-GUI-014 | Layout at phone 375x812 | Task list, New Task and Dashboard scroll sideways; Urgency column cut off; username cut off in top bar | DEF-023 |
| TC-GUI-015 | Form keeps typed values after a validation error | Both fields are emptied | DEF-025 |
| TC-ACC-003 | Form inputs have programmatic labels | Axe 'label' (critical): 2 inputs on Login, 2 on Register, 3 on New Task. <label> is not linked to its input (no for/id) | DEF-021 |
| TC-ACC-004 | Filter dropdowns have an accessible name | Axe 'select-name' (critical): category and status <select> have no name | DEF-021 |
| TC-ACC-005 | Text contrast at least 4.5:1 | Empty-state text #999 on white = 2.8:1 (also used for done-task titles) | DEF-022 |
| TC-ACC-010 | Content reflows on a narrow screen without sideways scrolling | Horizontal scroll; Urgency column hidden | DEF-023 |
| TC-ACC-011 | Complete/reopen button has a meaningful name | Button text is only the symbol '○' or '✓'; a screen reader announces 'white circle' | DEF-021 |

## Usability (LEMES)
| Dimension | Type | Observation |
| --- | --- | --- |
| Learnability | Positive | Simple layout; one main list; clear '+ New Task' button; first task created in under a minute. |
| Learnability | Issue | Password rule is shown on Register but the 8-character rule is enforced as 9 (DEF-002), confusing new users. |
| Efficiency | Positive | Category and status filters apply instantly when changed. |
| Efficiency | Issue | Search needs the Filter button while the dropdowns apply instantly: inconsistent behaviour. |
| Efficiency | Issue | No sorting by due date; the list is always newest first, so urgent tasks can be far down. |
| Memorability | Positive | Same top bar and button styles on every page; easy to return to after a break. |
| Errors | Positive | Delete asks for confirmation; required fields are checked by the browser; errors are in plain words. |
| Errors | Issue | Register form clears the typed values after an error (DEF-025); no success message after actions (DEF-024). |
| Errors | Issue | One bad date makes the whole task list crash with no way to recover in the UI (DEF-008). |
| Satisfaction | Positive | Clean, modern look; colour-coded urgency badges with text. |
| Satisfaction | Issue | Phone layout needs sideways scrolling and hides the Urgency column (DEF-023). |

## Recommendations
1. Link every `<label>` to its input (`for`/`id`); add `aria-label` to the filter dropdowns and the ○/✓ button.
2. Darken grey text to at least #767676 (4.5:1 contrast).
3. Make the task table responsive below 600 px.
4. Show success messages after create/edit/delete; keep typed values after a validation error.
5. Make search apply on Enter like the dropdowns; allow sorting by due date.
