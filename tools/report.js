// Builds 08_Final_QA_Report/PyTodo_Pro_Final_QA_Report.docx (Times New Roman 12 pt, APA references)
// from report_data.json + evidence files. Full test-case lists live in the repository workbooks.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, TableOfContents, Footer, PageNumber, ImageRun,
} = require("docx");
const L = require("./report_lib");
const { P, H1, H2, H3, bullets, numbered, img, table, tcap, caption, FONT } = L;

const ROOT = path.join(__dirname, "..");
const R = (p) => path.join(ROOT, p);
const D = JSON.parse(fs.readFileSync(R("08_Final_QA_Report/report_data.json")));
const m = D.metrics, O = m.overall, G = m.by_group, rows = D.rows, cov = m.coverage, perf = m.performance;
const byId = Object.fromEntries(rows.map((r) => [r.id, r]));
const def = Object.fromEntries(D.defects.map((d) => [d.id, d]));
const pct = (x) => `${x}%`;
const ofGroup = (g) => rows.filter((r) => r.group === g);
const failsOf = (g) => ofGroup(g).filter((r) => r.status === "Fail");
const short = (s, n = 120) => (s && s.length > n ? s.slice(0, n - 1) + "…" : s || "");
const ch = cov["helpers.py (unit tests only)"], ca = cov["app.py (all suites)"];
const C = [];
const add = (...xs) => xs.flat().forEach((x) => C.push(x));
const T = (t) => tcap(t);

// compress "TC-BB-001, TC-BB-002, TC-BB-003" -> "TC-BB-001–003"
function ranges(idsStr) {
  const ids = idsStr.split(",").map((s) => s.trim()).filter(Boolean);
  const out = []; let i = 0;
  while (i < ids.length) {
    const [pre, n] = [ids[i].replace(/\d+$/, ""), parseInt(ids[i].match(/\d+$/)[0], 10)];
    let j = i;
    while (j + 1 < ids.length && ids[j + 1].replace(/\d+$/, "") === pre && parseInt(ids[j + 1].match(/\d+$/)[0], 10) === n + (j + 1 - i)) j++;
    out.push(j > i ? `${ids[i]}–${ids[j].match(/\d+$/)[0]}` : ids[i]);
    i = j + 1;
  }
  return out.join(", ");
}

// ================================================================= COVER
const cv = (text, size, opts = {}) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: opts.after ?? 120, before: opts.before ?? 0 },
  children: [new TextRun({ text, font: FONT, size, bold: opts.bold, color: opts.color })] });
add(
  cv("UNIVERSITI TEKNOLOGI PETRONAS", 26, { bold: true, before: 600 }),
  cv("Department of Computing", 24),
  cv("TEB3433 / TFB3433 Software Testing and Quality Assurance", 24),
  cv("Group Project · September 2026 Semester", 24, { after: 900 }),
  cv("Independent Quality Assurance Evaluation of PyTodo Pro", 36, { bold: true, color: "1B3A5C", after: 200 }),
  cv("Final QA Report", 28, { color: "1B3A5C", after: 800 }),
  cv("Lecturer: Dr. Abdullateef Oluwagbemiga Balogun", 24, { after: 400 }),
  table(["Name", "Student ID", "Coordination role"], [
    ["Nureen [full name]", "[ID]", "QA / Test Lead"],
    ["[Name]", "[ID]", "Test Design Coordinator"],
    ["[Name]", "[ID]", "Automation / Tool Coordinator"],
    ["[Name]", "[ID]", "Defect & Metrics Coordinator"],
  ], [4, 2, 3.4], { size: 22 }),
  cv("GitHub repository: [link]", 24, { before: 500 }),
  cv("Submission date: [date]", 24),
);

// ================================================================= FRONT MATTER
const FT = (t) => new Paragraph({ pageBreakBefore: true, spacing: { after: 200 }, children: [new TextRun({ text: t, font: FONT, size: 28, bold: true })] });
add(FT("Table of Contents"));
add(new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-2" }));
add(FT("List of Tables"));
add(new TableOfContents("List of Tables", { hyperlink: true, captionLabelIncludingNumbers: "Table" }));
add(new Paragraph({ children: [] }));
add(new Paragraph({ children: [new TextRun({ text: "List of Figures", font: FONT, size: 28, bold: true })], spacing: { before: 360, after: 160 } }));
add(new TableOfContents("List of Figures", { hyperlink: true, captionLabelIncludingNumbers: "Figure" }));
add(P("Note: if the lists above are empty, right-click each one in Word and choose Update Field → Update entire table.", { run: { size: 18, italics: true } }));

// ================================================================= EXECUTIVE SUMMARY
add(H1("Executive Summary"));
add(P(`Our group evaluated PyTodo Pro as an independent QA team over eight project weeks. We designed **${O.planned} test cases** (black-box, white-box, GUI, accessibility, compatibility, API, security, performance and Selenium automation). **${O.executed} were executed (${O.execution_rate}%): ${O.passed} passed and ${O.failed} failed.** Four compatibility cases are pending on members' own laptops. The failures trace to **${m.defects_total} confirmed defects** (${m.severity.Critical} Critical, ${m.severity.Major} Major, ${m.severity.Moderate} Moderate, ${m.severity.Minor} Minor), and every failed test is linked to a defect ID.`));
add(P("**Verdict: PyTodo Pro is not ready for release.** The normal workflow works, but users' data is not safe and bad input is not rejected:"));
add(bullets([
  "A user can delete anyone's task through the API (DEF-005), read other users' tasks with SQL injection in search (DEF-006), and forge a login cookie because the secret key is in the source code (DEF-014).",
  "HTML in a task title runs in the browser (DEF-007), and one invalid due date permanently crashes that user's task list (DEF-008).",
  "Boundary mistakes break main rules: a task due today shows \"Overdue\" (DEF-001) and an 8-character password is rejected (DEF-002).",
]));
add(P(`White-box tests reached ${ch.stmt_pct}% statement and ${ch.branch_pct}% branch coverage of helpers.py, yet three still failed, which shows that coverage measures what ran, not correctness. Normal pages stayed fast (95th percentile ≤ ${perf["50"]["GET /api/dashboard"].p95} ms at 50 users, no errors at 100 users); only login slowed under bursts. Testing cannot prove the software defect-free; residual risks and untested areas are listed in Section 11.`));

// ================================================================= 1 INTRODUCTION
add(H1("1. Introduction"));
add(H2("1.1 Purpose and independence of the evaluation"));
add(P("This report presents an evidence-based quality evaluation of PyTodo Pro, a task-management web application supplied by the lecturer. We acted as an **independent QA team**: we did not develop the application and did not change its code. Everything was tested on an unmodified copy, every test used a fresh temporary database, and any fixes are left to the developers. Independence matters because developers tend to test that their code works, while an independent tester tries to show that it does not (Myers et al., 2011)."));
add(P("The project was progressive: each week applied a new course topic to the same application, and earlier work was revised when later evidence changed our view (for example, the risk ratings in Section 8.2). For each feature we show the evidence chain: expected behaviour, why it matters, how it was tested, what happened, the defect, and the remaining risk."));
add(H2("1.2 Testing, quality control and quality assurance in this project"));
add(P("The course distinguishes three related ideas (Balogun, 2026), and this project used all three:"));
add(table(["Concept", "Focus", "What it was in our project"], [
  ["Software testing", "Running the software to find failures", `Designing and executing ${O.planned} test cases and comparing actual with expected results`],
  ["Quality control (QC)", "Product-oriented: detect defects in the product", `Checking PyTodo Pro against its requirements, confirming ${m.defects_total} defects, deciding it is not fit for release`],
  ["Quality assurance (QA)", "Process-oriented: prevent defects", "Test plan and strategy, ID and review rules, regression suite, CI/CD pipeline and the process improvements in Section 12"],
], [1.8, 2.8, 4.8]));
add(P("Testing is the main activity of QC; QA is wider and aims to stop the same defects being made again."));
add(H2("1.3 Team and responsibilities"));
add(table(["Member", "Coordination role", "Report sections owned"], [
  ["Nureen (Member 1)", "QA / Test Lead: scope, schedule, reviews, plan, integration", "1, 8, 12, 13"],
  ["[Name] (Member 2)", "Test Design: requirements, black-box, GUI, RTM", "2, 4, 9"],
  ["[Name] (Member 3)", "Automation / Tools: white-box, API, Selenium, coverage", "3, 5, 7"],
  ["[Name] (Member 4)", "Defects & Metrics: defect log, STRIDE, performance, metrics", "6, 10, 11"],
], [2.2, 5.2, 2]));
add(P("All members designed and executed tests in every phase, and no one reviewed only their own work."));
add(H2("1.4 Application overview"));
add(P("PyTodo Pro lets a registered user create, categorise, search, complete and delete personal tasks with optional due dates. Each task receives an urgency label and a dashboard summarises them. The same functions are offered as a JSON REST API. There is a single user type, and each user must see and change **only their own tasks**."));
add(T("Architecture of PyTodo Pro (three tiers)"));
add(table(["Tier", "Technology", "Tested by"], [
  ["Presentation", "6 Jinja2 templates, CSS, HTML5 form validation", "GUI, usability, accessibility, compatibility, Selenium"],
  ["Application", "Python, Flask 3.0.3 (Pallets, n.d.); app.py 482 lines, helpers.py 75 lines; session cookies", "Black-box, white-box, API, security"],
  ["Data", "SQLite: users, categories, tasks", "Data integrity, injection"],
], [1.6, 4.4, 3.4]));
add(T("Feature inventory (requirements baseline)"));
add(table(["ID", "Feature", "Business rule (README / helpers.py)"], [
  ["F01", "Registration", "Username 3–20 characters (letters, digits, _); password at least 8 characters"],
  ["F02", "Login / logout", "Correct credentials start a session; logout ends it"],
  ["F03", "Access control", "Logged out: redirect or 401; users reach only their own tasks"],
  ["F04", "Create task", "Title required; category and due date (YYYY-MM-DD) optional"],
  ["F05", "View / list", "Newest first; API pagination (page, per_page)"],
  ["F06", "Edit task", "Edit fields; API partial update"],
  ["F07", "Complete / reopen", "completed_at set when done, cleared when reopened"],
  ["F08", "Delete task", "Only the owner can delete"],
  ["F09", "Filter / search", "Category and status filters; search part of the title"],
  ["F10", "Urgency", "No due date, Overdue, Due Today, Due Soon (1–2 days), Upcoming (3+ days), Done"],
  ["F11", "Dashboard", "Total, Open, Overdue, Due Soon, Completed in last 7 days (inclusive)"],
  ["F12", "Categories", "Work, Personal, Study, Urgent"],
], [0.7, 1.8, 6.9]));
add(P("Non-functional requirements tested: NF2 performance, NF3 GUI/usability, NF4 accessibility and NF5 compatibility. Security is covered under F03 and the STRIDE analysis."));
add(H2("1.5 Quality expectations, scope and limitations"));
add(P("Using the ISO/IEC 25010 quality model (International Organization for Standardization [ISO] & International Electrotechnical Commission [IEC], 2011), we agreed that a personal task manager must above all be **correct** (urgency and dashboard rules guide deadlines), **secure** (tasks stay private), **reliable** (bad input never crashes the app), **usable** by new users, **fast** at normal load, and **compatible** with common browsers and phones."));
add(P("**In scope:** all 12 features through the web UI and the API, the rules in helpers.py, and selected non-functional checks. **Out of scope:** changing the code, production hosting, load beyond one machine, uncontrolled penetration testing (forbidden by the brief) and testing with real users with disabilities. **Main limitation:** evidence was produced on Chrome 153 (Linux); other browsers are planned on members' laptops (TC-COMP-002 to 005)."));
add(H2("1.6 Structure of the report"));
add(P("Sections 2 to 7 present each testing phase (black-box, white-box, special testing, web/API, security/performance, automation). Section 8 gives the final test plan and strategy, Section 9 the traceability matrix, Section 10 defect management, and Section 11 metrics, residual risk and the overall assessment. Section 12 relates the work to standards and recommends improvements; Section 13 concludes. Full test-case tables, logs and screenshots are in the GitHub repository (Appendix A), and this report shows the key and failed cases."));

// ================================================================= 2 BLACK-BOX
const bb = ofGroup("Black-box (Wk 1)");
add(H1("2. Application Analysis and Black-Box Testing"));
add(P(`Black-box testing checks what the system does from its requirements without looking at the code (Balogun, 2026). We designed ${bb.length} cases with four techniques and executed them through the web forms (HTTP form submissions scripted with PyTest so they can be repeated); key results were also confirmed in a real browser with Selenium screenshots. **${G["Black-box (Wk 1)"].passed} passed and ${G["Black-box (Wk 1)"].failed} failed.**`));
add(H2("2.1 Initial test scope and risk matrix"));
add(P("Before testing, each feature was rated by likelihood of failure and impact on users (1–3); risk = likelihood × impact. Following risk-based testing, the highest-risk features were tested first and most deeply."));
add(T("Week 1 risk matrix (before testing)"));
add(table(["Feature", "Likelihood", "Impact", "Score", "Priority", "Reason"], [
  ["F03 Access control / F08 Delete", "2", "3", "6", "High", "Privacy of every user"],
  ["F04 / F06 input validation", "2", "3", "6", "High", "Bad data could corrupt tasks"],
  ["F09 Search / filter", "2", "3", "6", "High", "User text reaches database queries"],
  ["F10 Urgency / F11 Dashboard", "2", "2", "4", "Medium", "Date boundaries are error-prone"],
  ["F01 Registration / F02 Login", "2", "2", "4", "Medium", "Gate to the whole app"],
  ["F05 List, F07 Toggle, F12", "1", "1–2", "1–2", "Low", "Simple display logic"],
], [2.7, 1.5, 1, 0.9, 1.1, 2.8], { fillCols: [4] }));
add(H2("2.2 Equivalence partitioning and boundary value analysis"));
add(T("Equivalence partitions"));
add(table(["Input", "Valid classes", "Invalid classes", "Test cases"], [
  ["Username length / characters", "3–20; letters, digits, _", "< 3; > 20; space or symbol", "TC-BB-001–008"],
  ["Password length", "≥ 8", "< 8; empty", "TC-BB-009–012"],
  ["Task title", "text; special characters", "empty; spaces only", "TC-BB-021–024, 048"],
  ["Due date", "valid date; none", "impossible date (2026-13-45)", "TC-BB-021, 022, 049"],
  ["Search text", "partial match; no match; apostrophe", "–", "TC-BB-041, 042, 044"],
], [2.6, 2.6, 2.6, 1.8]));
add(P("Developers often make off-by-one errors at the edges, so we used **3-value BVA** (the boundary and both neighbours), which is stricter than 2-value BVA:"));
add(T("3-value boundary value analysis"));
add(table(["Step", "Username length", "Password length", "Days until due date"], [
  ["Partitions", "0–2 | 3–20 | 21+", "0–7 | 8+", "≤ −1 | 0 | 1–2 | 3+"],
  ["Boundaries", "3 and 20", "8", "0, 1, 2, 3"],
  ["Coverage items", "2, 3, 4, 19, 20, 21", "7, 8, 9", "−1, 0, 1, 2, 3"],
  ["Test cases", "TC-BB-001–006", "TC-BB-009–011", "TC-BB-025–029"],
  ["Result", "All pass", "8 fails (DEF-002)", "Day 0 fails (DEF-001)"],
], [1.6, 2.6, 2.2, 3]));
add(P("BVA found two defects that EP alone could miss: in both, the value just inside the valid range failed, the classic off-by-one error."));
add(H2("2.3 Decision tables and state transitions"));
add(P("Registration has three conditions (2³ = 8 rules); when the username is invalid the others do not matter, so the table simplifies to four rules:"));
add(T("Decision table for registration"));
add(table(["Conditions / action", "R1", "R2", "R3", "R4"], [
  ["C1 Username valid", "Y", "Y", "Y", "N"], ["C2 Password valid", "Y", "Y", "N", "–"], ["C3 Username not taken", "Y", "N", "–", "–"],
  ["Expected action", "Create account", "'Username taken'", "Password error", "Username error"],
  ["Test / result", "TC-BB-013 Pass", "TC-BB-014 Fail", "TC-BB-015 Pass", "TC-BB-016 Pass"],
], [2.6, 1.7, 1.7, 1.7, 1.7]));
add(P("Rule R2 failed: the system has no action for a taken username, so a duplicate account is created (DEF-004), and TC-BB-020 showed the duplicate can never log in. The login table (user exists × password correct, simplified to three rules; TC-BB-017–019) passed."));
add(T("State transitions of a task (\"–\" = invalid transition)"));
add(table(["State", "Toggle", "Delete", "Edit", "Tests"], [
  ["Open", "→ Done; set completed_at", "→ Deleted", "→ Open", "TC-BB-032, 034, 047"],
  ["Done", "→ Open; clear completed_at", "→ Deleted", "→ Done", "TC-BB-033"],
  ["Deleted", "– (refused)", "–", "– (refused)", "TC-BB-035, 036"],
], [1.3, 2.6, 1.4, 1.6, 2.5]));
add(P("Session transitions (logged out → protected page; logged in → log out → protected page; TC-BB-037–038) and all task transitions passed, including invalid ones, which were refused safely."));
add(H2("2.4 Test data, justification and results"));
add(bullets([
  "Dates are calculated from the run date (today − 1 … today + 3), so tests give the same result on any day.",
  "Some cases post form data directly (title of spaces, date 2026-13-45) to bypass browser checks and test the server.",
  "Two users (qa_user1, qa_user2) allow cross-user checks; boundary usernames and passwords come from the BVA table.",
]));
add(T("Failed black-box test cases (all 49 cases: 01_Black_Box/Black_Box_Test_Cases.xlsx)"));
add(table(["ID", "Technique", "Expected", "Actual", "Defect"],
  failsOf("Black-box (Wk 1)").map((r) => [r.id, r.technique, short(r.expected, 70), short(r.actual, 90), r.defect]), [1.2, 1.8, 2.6, 3, 0.9]));
add(P(`With a ${G["Black-box (Wk 1)"].pass_rate}% pass rate, the main workflows work for normal data. Failures cluster at **boundaries** and in **server-side validation**, which matches the defect clustering principle (International Software Testing Qualifications Board [ISTQB], 2023).`));

// ================================================================= 3 WHITE-BOX
const wb = ofGroup("White-box (Wk 2)");
add(H1("3. White-Box Testing and Code Coverage"));
add(P(`White-box testing uses the source code to design tests (Balogun, 2026). As the brief requires, we did not test the whole application structurally; we selected the units below, drew control flow graphs, calculated V(G) and designed basis-path and boundary tests. ${wb.length} PyTest unit tests were written (pytest-dev, n.d.): **${G["White-box (Wk 2)"].passed} passed and ${G["White-box (Wk 2)"].failed} failed.**`));
add(T("Units selected for white-box testing"));
add(table(["Unit", "Why selected", "V(G)"], [
  ["helpers.compute_urgency", "Most important business rule; four decisions; drives badges and dashboard", "5"],
  ["helpers.is_valid_password", "Registration gate; boundary at 8", "3"],
  ["helpers.is_valid_username", "Registration gate; range and character rules", "4"],
  ["helpers.completed_in_last_n_days", "Dashboard counter; inclusive boundary; compound condition", "4"],
  ["app.api_update_task (completed_at)", "if / elif / else that sets or clears completion time", "3"],
], [3.2, 5.4, 0.8]));
add(img(R("02_White_Box_Coverage/cfg/compute_urgency_cfg.png"), 270, "Control flow graph of compute_urgency() (shaded = predicate node)"));
add(P("For compute_urgency, V(G) agrees by all three methods: E − N + 2 = 13 − 10 + 2 = 5; predicates + 1 = 4 + 1 = 5; and 5 regions. A value of 5 (band 1–10) means a well-structured, easily testable unit needing at most five basis-path tests. The graph for completed_in_last_n_days (V(G) = 4) is in the repository."));
add(T("Basis paths and white-box tests for compute_urgency() (today = 2026-11-21)"));
add(table(["Basis path", "Meaning", "Input", "Expected", "Test"], [
  ["1-3-4-10", "No due date", "None", "No due date", "TC-WB-001"],
  ["1-2-3-5-7-9-10", "today defaulted", "today + 30", "Upcoming", "TC-WB-002"],
  ["1-3-5-6-10", "Past date", "2026-11-20", "Overdue", "TC-WB-003"],
  ["1-3-5-7-8-10", "1–2 days away", "2026-11-22", "Due Soon", "TC-WB-005"],
  ["1-3-5-7-9-10", "3+ days away", "2026-11-24", "Upcoming", "TC-WB-007"],
  ["Boundary of 'due <= today'", "Due today", "2026-11-21", "Due Today", "TC-WB-004 (Fail)"],
], [2.6, 1.8, 1.6, 1.6, 1.8]));
add(P("All basis paths pass, yet TC-WB-004 fails: the specification needs \"Due Today\", but no branch can return it because `due <= today` sends today into the Overdue branch (DEF-001). The other failures are TC-WB-010 (exactly 8 characters, `len > 8`; DEF-002) and TC-WB-021 (exactly 7 days, `age.days < n`; DEF-003)."));
add(P("**Path and data-flow notes:** there are no infeasible paths. The compound condition `age > 0 and age.days < n` was tested with each part false (TC-WB-021, 023). The due date is defined by the user, stored without validation and only used later, where `strptime` raises an error (TC-WB-008); this define–store–use chain with no check is the root cause of DEF-008."));
add(T("Coverage measured with pytest-cov / coverage.py (Batchelder, n.d.)"));
add(table(["Scope", "Statements", "Statement %", "Branches", "Branch %"], [
  ["helpers.py (unit tests)", `${ch.covered}/${ch.statements}`, pct(ch.stmt_pct), `${ch.branches_covered}/${ch.branches}`, pct(ch.branch_pct)],
  ["app.py (all automated suites)", `${ca.covered}/${ca.statements}`, pct(ca.stmt_pct), `${ca.branches_covered}/${ca.branches}`, pct(ca.branch_pct)],
], [3.2, 1.6, 1.6, 1.4, 1.6]));
add(P(`helpers.py is fully covered, yet three tests fail: **coverage shows what code ran, not whether it is correct, and it cannot reveal missing code.** In app.py, lines 242 and 266 (empty forms on GET) ran only in Selenium, which is not measured; line 375, the API \`status=open\` filter, was **not tested** (a gap); lines 481–482 are the start-up block.`));

// ================================================================= 4 SPECIAL
const gui = ofGroup("GUI & config (Wk 3)"), acc = ofGroup("Accessibility (Wk 3)");
add(H1("4. GUI, Compatibility, Usability and Accessibility Testing"));
add(P("This phase asks whether the application is visible, easy to use, usable by everyone and consistent across platforms (Balogun, 2026). Selenium opened all seven pages in Chrome at desktop (1366×768), tablet (768×1024) and phone (375×812) sizes and saved 21 screenshots (Selenium Project, n.d.). The Axe engine checked WCAG 2.1 A and AA rules (Deque Systems, n.d.; W3C, 2018); we then checked the keyboard and reviewed each screen against a checklist."));
add(H2("4.1 GUI checklist results"));
add(P(`${gui.length} GUI checks: **${G["GUI & config (Wk 3)"].passed} passed, ${G["GUI & config (Wk 3)"].failed} failed.** Titles, navigation, button labels, error messages, required-field checks, delete confirmation, done-task styling and empty-state messages all work. The failed checks were:`));
add(T("Failed GUI checks (all checks: 03_Special_Testing/Special_Testing_Results.xlsx)"));
add(table(["ID", "Check", "Actual", "Defect"], failsOf("GUI & config (Wk 3)").map((r) => [r.id, r.objective, short(r.actual, 110), r.defect]), [1.3, 3, 4.1, 1]));
add(H2("4.2 Compatibility and configuration"));
add(T("Compatibility and configuration matrix"));
add(table(["Browser / OS", "Desktop", "Tablet", "Phone", "Test"], [
  ["Chrome 153 / Linux", "Pass", "Pass", "Fail (DEF-023)", "TC-COMP-001, TC-GUI-012–014"],
  ["Chrome / Windows 11", "Not Run", "Not Run", "Not Run", "TC-COMP-002"],
  ["Edge / Windows 11", "Not Run", "Not Run", "Not Run", "TC-COMP-003"],
  ["Firefox / Windows 11", "Not Run", "Not Run", "Not Run", "TC-COMP-004"],
  ["Safari / macOS", "Not Run", "Not Run", "Not Run", "TC-COMP-005"],
], [2.4, 1.3, 1.3, 1.7, 2.7], { fillCols: [1, 2, 3] }));
add(P("Testing every OS × browser × screen combination is impossible, so common student setups were chosen. On a phone-sized screen the task table is wider than the screen: users must scroll sideways and the Urgency column is cut off (DEF-023, also a WCAG 1.4.10 Reflow failure). The Windows browser runs are being completed by members; Safari cannot be tested because no member owns a Mac, which remains a residual risk."));
add(img(R("03_Special_Testing/screenshots/04_task_list_phone_375x812.png"), 120, "My Tasks at phone size: sideways scroll, Urgency column cut off (DEF-023)"));
add(H2("4.3 Usability observations"));
add(P("A team heuristic review using Nielsen's LEMES dimensions (an expert walkthrough, not real-user testing) found:"));
add(table(["Dimension", "Positive", "Issue"], [
  ["Learnability", "Simple layout; first task created in under a minute", "8-character rule shown but 9 enforced (DEF-002)"],
  ["Efficiency", "Dropdown filters apply instantly", "Search needs the Filter button (inconsistent); no sort by due date"],
  ["Memorability", "Same top bar and styles on every page", "–"],
  ["Errors", "Delete confirmation; plain-language errors", "No success messages (DEF-024); register form clears input (DEF-025); one bad date crashes the list (DEF-008)"],
  ["Satisfaction", "Clean look; badges with text and colour", "Phone layout needs sideways scrolling (DEF-023)"],
], [1.6, 3.4, 4.4]));
add(H2("4.4 Accessibility findings"));
add(P(`${acc.length} WCAG checks: **${G["Accessibility (Wk 3)"].passed} passed, ${G["Accessibility (Wk 3)"].failed} failed.** Language, page titles, keyboard order, visible focus, text error messages and non-colour urgency labels pass.`));
add(T("Failed accessibility checks"));
add(table(["ID", "WCAG criterion", "Actual", "Defect"], failsOf("Accessibility (Wk 3)").map((r) => [r.id, r.technique.replace("WCAG ", ""), short(r.actual, 115), r.defect]), [1.2, 2.4, 4.8, 1]));
add(P("In POUR terms, the application is **operable** and **understandable**, but weak on **perceivable** (contrast) and **robust** (labels are not linked to inputs, so a screen reader cannot name the fields). It does not reach WCAG 2.1 Level AA. **Recommendations:** link labels to inputs and add aria-labels to the dropdowns and ○/✓ button; darken grey text to at least #767676; make the table responsive; add success messages and keep typed values after errors."));

// ================================================================= 5 WEB & API
const api = ofGroup("Web & API (Wk 4)");
add(H1("5. Web and API Testing"));
add(P(`API testing checks the business-logic layer directly, by sending JSON requests and checking the status code and body (Balogun, 2026). We wrote ${api.length} API tests with PyTest and the Flask test client: **${G["Web & API (Wk 4)"].passed} passed and ${G["Web & API (Wk 4)"].failed} failed.** A 500 error on bad input always counts as a failure, because the server must answer with a 4xx code. The main web workflows (register → log in → create → complete → filter → dashboard → log out) were covered by the black-box and Selenium suites.`));
add(T("REST API endpoints and the test types applied"));
add(table(["Endpoint", "Auth", "Test types", "Tests"], [
  ["POST /api/register", "No", "Valid, invalid, wrong type, duplicate", "TC-API-001–006"],
  ["POST /api/login", "No", "Valid, wrong password, unknown user", "TC-API-007–009"],
  ["GET /api/categories", "Yes", "Functional, no session", "TC-API-011–012"],
  ["GET /api/tasks", "Yes", "Pagination, filters, search, edge cases", "TC-API-010, 025–033"],
  ["POST /api/tasks", "Yes", "Valid, missing, wrong type, invalid date, edge", "TC-API-013–021"],
  ["GET / PUT /api/tasks/{id}", "Yes", "Own, unknown, other user, partial, wrong type", "TC-API-022–024, 034–039"],
  ["DELETE /api/tasks/{id}", "Yes", "Own, unknown, other user, no session", "TC-API-040–043"],
  ["GET /api/dashboard", "Yes", "Counts, boundary, no session", "TC-API-044–046"],
], [2.6, 0.8, 3.6, 2.4]));
add(T("Failed API tests: expected versus actual (all 46: 04_Web_API/API_Test_Cases.xlsx)"));
add(table(["ID", "Objective", "Expected", "Actual", "Defect"],
  failsOf("Web & API (Wk 4)").map((r) => [r.id, short(r.objective, 60), short(r.expected, 40), short(r.actual, 75), r.defect]), [1.2, 2.6, 1.8, 3, 0.9]));
add(H2("5.1 Client-side versus server-side behaviour"));
add(P("Validation on the client is for usability; validation on the server is for security. We sent the same data through the browser and directly to the server:"));
add(T("UI versus server/API behaviour"));
add(table(["Input", "Browser", "Server / API", "Defect"], [
  ["Empty title", "Blocked by 'required'", "Saved by form post and API PUT", "DEF-009"],
  ["Impossible date", "Date picker prevents it", "Saved, then 500 on every list", "DEF-008"],
  ["Apostrophe in search", "Web search works", "API search returns 500", "DEF-006"],
  ["Delete another user's task", "Not possible", "Possible", "DEF-005"],
  ["Duplicate username", "Accepted", "Accepted", "DEF-004"],
], [2.4, 2.2, 3.4, 1.4]));
add(P("The developer relied on browser checks or wrote the web and API versions of a feature differently, so anyone using Postman or an edited request skips every client-side check. Happy-path API tests all pass, as do 401 for no session and 404 for other users' tasks on GET and PUT; most failures are negative tests."));

// ================================================================= 6 SECURITY & PERFORMANCE
const sec = ofGroup("Security (Wk 5)");
add(H1("6. Security and Performance Testing"));
add(H2("6.1 STRIDE threat analysis and security tests"));
add(P("We followed the threat-modelling steps from the course: decompose the application into assets and data flows, apply STRIDE, decide mitigations, and derive safe tests (Balogun, 2026; OWASP Foundation, 2021). **All security tests ran only on our local copy with a temporary database.**"));
add(T("STRIDE threat table"));
add(table(["Asset / function", "STRIDE", "Threat", "Property", "Test(s)", "Result"],
  D.stride.map((s) => [s[0], s[1], s[2], s[3], s[4], s[5]]), [1.6, 1.4, 2.8, 1.3, 1.3, 1.5], { size: 18 }));
add(P(`${sec.length} security tests: **${G["Security (Wk 5)"].passed} passed, ${G["Security (Wk 5)"].failed} failed.** Passwords are stored as salted scrypt hashes, cookies are HttpOnly, wrongly signed cookies are rejected, and GET, PUT and the edit page refuse other users' tasks. The three most serious findings are fully reproducible:`));
add(numbered([
  "**Session forgery (DEF-014):** using only the SECRET_KEY written in app.py, we signed a cookie for user 2 and read that user's private task.",
  "**SQL injection with data leak (DEF-006):** the search text `x%' OR user_id != 0 OR title LIKE '%` made the API return another user's task.",
  "**Debugger exposed (DEF-014):** with debug=True, any server error shows the Werkzeug Debugger with the traceback and file paths.",
], "num2"));
add(P("The other failures are cross-user delete (DEF-005), stored XSS (DEF-007), no CSRF protection (DEF-015), no login attempt limit (DEF-019) and cookies still valid after logout (DEF-020)."));
add(H2("6.2 Performance experiment"));
add(P("**Objective (defined before execution):** measure response time, throughput and error rate as users increase. **Workload (Locust; Locust, n.d.):** each virtual user logs in once as perf_user (100 tasks), then with 1–2 s think time requests GET /api/tasks (60%), GET /api/dashboard (30%) and POST /api/tasks (10%). Levels: 1, 10, 25 and 50 users for 40 s each, plus a stress step of 100 users added 10 per second. **Criterion:** 95th percentile < 1,000 ms and 0% errors for every request type. **Environment:** Flask development server (debug on), SQLite, load generator on the same 2-vCPU / 8 GB machine."));
const pr = (u, n) => (perf[u] && perf[u][n]) || {};
add(T("Performance results by load level"));
add(table(["Users", "Task list avg / p95 (ms)", "Dashboard avg / p95 (ms)", "Login avg / p95 (ms)", "Req/s", "Errors", "Result"],
  ["1", "10", "25", "50", "100_stress"].map((u) => {
    const a = pr(u, "GET /api/tasks"), b = pr(u, "GET /api/dashboard"), c = pr(u, "/api/login"), g = pr(u, "Aggregated");
    const r = byId[{ "1": "TC-PERF-001", "10": "TC-PERF-002", "25": "TC-PERF-003", "50": "TC-PERF-004", "100_stress": "TC-PERF-005" }[u]];
    return [u.replace("_stress", " (stress)"), `${a.avg} / ${a.p95}`, `${b.avg} / ${b.p95}`, `${c.avg} / ${c.p95}`, g.rps, g.fail, r.status];
  }), [1.3, 1.8, 1.8, 1.8, 0.9, 0.9, 0.9], { fillCols: [6] }));
add(img(R("08_Final_QA_Report/charts/performance_p95.png"), 330, "95th-percentile response time by number of users (log scale)"));
add(P("Task list and dashboard stayed below 15 ms (p95) up to 50 users, throughput rose roughly in line with users (about 0.7 req/s each), and there were no errors at any level, so the stress step found no breaking point. **Login is the bottleneck (DEF-026):** when all users log in in the same second, CPU-heavy password hashing makes requests queue, so login p95 reached 1,200 ms at 25 users and 2,500 ms at 50; with a gradual ramp, 100 users logged in at about 483 ms. **Limitations:** development server, shared CPU with the load generator, SQLite, short runs and no CPU/memory monitoring, so results show trends rather than production capacity. We recommend a production server with debug off, login rate limiting and a repeat test on production-like hardware."));

// ================================================================= 7 AUTOMATION
add(H1("7. Test Automation and Regression"));
add(P("A test was automated if it was **repeated often, stable, critical or valuable for regression** (Balogun, 2026). Exploratory, visual, usability and accessibility judgements and one-off cross-browser checks stayed manual. Our suite follows the test pyramid:"));
add(T("Automated tests by pyramid layer"));
add(table(["Layer", "Tool", "Tests", "Run time"], [
  ["UI / end-to-end (few)", "Selenium WebDriver with Page Object Model", `${G["UI automation (Wk 6)"].planned}`, "≈ 20 s"],
  ["API / integration", "PyTest + Flask test client (forms, API, security)", `${G["Black-box (Wk 1)"].planned + G["Web & API (Wk 4)"].planned + G["Security (Wk 5)"].planned - 1}`, "≈ 13 s"],
  ["Unit (many)", "PyTest with parametrize", `${G["White-box (Wk 2)"].planned}`, "< 1 s"],
], [2.4, 4, 1, 1.4]));
add(P("Every test starts with a fresh temporary database, so tests never depend on each other. The Page Object Model keeps locators in one file, so a renamed button needs only one fix. Each Selenium script is traced to the manual cases it automates:"));
add(T("Manual-to-automated traceability"));
add(table(["Script", "What it automates", "Manual test(s)", "Result"], D.automation.map((a) => [a[0], a[1], a[2], a[4]]), [1, 3.6, 3.2, 1], { fillCols: [3] }));
const regRows = rows.filter((r) => m.regression_ids.includes(r.id));
const regPass = regRows.filter((r) => r.status === "Pass").length;
add(P(`The focused **regression suite** has ${m.regression_suite_size} tests tagged \`@pytest.mark.regression\` (run with \`pytest -m regression\`): high-risk areas, frequently used features, critical rules and every failed boundary. Currently ${regPass} pass and ${regRows.length - regPass} fail; the failing ones are known defects and act as **confirmation tests** after a fix, while the rest check that the fix broke nothing.`));
add(P("**Reflection:** the non-UI suite of 137 tests runs in about 13 seconds, so we re-ran it many times with identical results, and generating documents from results kept IDs consistent. On the other hand, scripts took longer to write than one manual run, one Selenium test was flaky until waits and a retry were added, and automation cannot judge usability."));

// ================================================================= 8 PLAN & STRATEGY
add(H1("8. Test Plan and Test Strategy"));
add(P("Version 2.0 of our plan (PYTODO-STP v2.0) was updated in Week 7 with evidence from Weeks 1–6 and follows the IEEE 829 structure (IEEE, 2008). The full plan is in 07_Test_Management/Test_Plan_and_Strategy.md; the essentials are below."));
add(H2("8.1 Software Test Plan"));
add(P("**Objectives:** verify F01–F12 against the README and helpers.py; find reproducible defects; measure coverage of selected units; evaluate security, performance, usability, accessibility and compatibility; build a regression suite; give an evidence-based quality judgement. **Scope:** PyTodo Pro as issued and its database; F01–F12 through UI and API plus NF2–NF5; out of scope as in Section 1.5. **Environment and tools:** Python 3.13, Flask 3.0.3, Chrome 153, PyTest, pytest-cov, Selenium, axe-core, Locust, an Excel test-management workbook and GitHub. **Test data:** two users; boundary usernames and passwords; dates from today − 1 to today + 3; empty, space-only, HTML and 5,000-character titles; apostrophes; impossible dates."));
add(P("**Pass/fail rules:** Pass when the actual result matches the expected result written before execution; Fail when it differs (linked to a defect); Blocked when a precondition cannot be met; Not Run when planned but not executed (reason recorded). **Suspension:** if the app cannot start, the database is corrupted (DEF-008) or more than 30% of a suite is blocked; resume after resetting the database."));
const hi = rows.filter((r) => r.priority === "High"), hiExec = hi.filter((r) => r.status !== "Not Run").length;
add(T("Entry and exit criteria and their status"));
add(table(["Criterion", "Type", "Target", "Actual", "Met?"], [
  ["App runs; cases have IDs, data and expected results; fresh DB per run", "Entry", "Yes", "Yes", "Yes"],
  ["High-priority cases executed", "Exit", "100%", `${hiExec}/${hi.length}`, hiExec === hi.length ? "Yes" : "Pending (TC-COMP-002)"],
  ["All planned cases executed", "Exit", "≥ 90%", pct(O.execution_rate), O.execution_rate >= 90 ? "Yes" : "No"],
  ["Every failed case linked to a defect", "Exit", "100%", "100%", "Yes"],
  ["helpers.py branch / app.py statement coverage", "Exit", "≥ 90% / ≥ 70%", `${ch.branch_pct}% / ${ca.stmt_pct}%`, "Yes"],
  ["Every feature has an executed test (RTM)", "Exit", "100%", "100%", "Yes"],
  ["Release: no open Critical defects", "Release", "0", `${m.severity.Critical}`, "No"],
], [4, 1, 1.4, 1.6, 1.6]));
add(P("Our testing exit criteria are met (apart from compatibility runs still in progress), but the release criterion is not, which supports the verdict that the app is not ready for release."));
add(T("Schedule and deliverables"));
add(table(["Project week (course week)", "Phase", "Lead", "Folder"], [
  ["1 (4)", "Application analysis, black-box", "Member 2", "/01_Black_Box"],
  ["2 (5)", "White-box and coverage", "Member 3", "/02_White_Box_Coverage"],
  ["3 (6)", "GUI, compatibility, usability, accessibility", "Member 2", "/03_Special_Testing"],
  ["4 (7)", "Web and API", "Member 3", "/04_Web_API"],
  ["5 (8)", "Security and performance", "Member 4", "/05_Security_Performance"],
  ["6 (9)", "Automation and regression", "Member 3", "/06_Automation_Regression"],
  ["7 (10)", "Test plan v2, RTM, defect consolidation", "Members 1, 2", "/07_Test_Management"],
  ["8–9 (11–12)", "Metrics, evaluation, standards, presentation", "Members 4, 1", "/08, /09"],
], [2.2, 3.6, 1.4, 2.2]));
add(P("**Project risks and contingencies:** missed deadlines (weekly check-in; the support member takes over), results differing between machines (injected dates; environment recorded), a blocking defect (fresh database per test), inconsistent IDs (one catalogue; the build script refuses mismatches) and a failed live demo (recorded backup)."));
add(H2("8.2 Test Strategy"));
add(P("The strategy is **risk-based**. Product risks were rated in Week 1 and re-rated as evidence arrived; the table shows how our understanding changed, as the Week 1 ratings were too optimistic about security and validation."));
add(T("Risk register: Week 1 versus final likelihood (impact unchanged)"));
add(table(["ID", "Product risk", "L (Wk 1)", "Impact", "Score Wk 1", "L final", "Score final", "Evidence"],
  D.risks.map((r) => [r[0], r[1], r[3], r[4], r[5], r[6], r[7], r[8]]), [0.7, 3.2, 0.8, 0.8, 0.9, 0.8, 0.9, 2.1], { size: 18 }));
add(bullets([
  "**Levels:** unit (helpers.py) → integration/API (Flask client) → system (Selenium, manual GUI) → acceptance-style scenarios. A static code review found the root cause of eight defects before dynamic tests confirmed them.",
  "**Techniques:** EP, BVA, decision tables, state transitions, basis paths, API negative testing, STRIDE, load testing, WCAG and LEMES reviews.",
  "**Automation:** the test pyramid; automate repeated, stable, critical, regression-valuable tests (Section 7).",
  "**Defects and metrics:** one central log with severity and priority (Section 10); metrics in Section 11.",
]));

// ================================================================= 9 RTM
add(H1("9. Requirements Traceability Matrix"));
add(P(`Traceability links every requirement to its tests, and every result to its defects. All ${O.planned} cases are kept in one master repository with the Test Case Template fields, plus priority, automation and regression flags (07_Test_Management/PyTodo_Test_Management.xlsx). The repository and RTM are generated from the test catalogue and the PyTest results, so they always match what actually ran.`));
add(T("Requirements Traceability Matrix"));
add(table(["Requirement", "Test case IDs", "Result", "Defect IDs"],
  D.rtm.map((r) => [r[0], ranges(r[2]), r[4], r[5]]), [1.8, 4.6, 1.2, 1.8], { size: 18 }));
add(P("Every requirement has at least one executed test, so the RTM shows no coverage gaps."));
add(T("Execution status by phase"));
add(table(["Phase", "Planned", "Executed", "Passed", "Failed", "Not Run", "Pass rate"],
  [...Object.entries(G).map(([g, c]) => [g, c.planned, c.executed, c.passed, c.failed, c.not_run, pct(c.pass_rate)]),
    ["**Total**", O.planned, O.executed, O.passed, O.failed, O.not_run, pct(O.pass_rate)]], [3, 1, 1, 1, 1, 1, 1.2]));

// ================================================================= 10 DEFECTS
add(H1("10. Defect Management"));
add(P("We used the defect lifecycle from the course (New → Assigned → Open → Fixed → Retest → Closed, with Duplicate, Rejected and Deferred exits; ISTQB, 2023). As an independent team we cannot fix code, so a defect moved from New to **Confirmed** once a second member reproduced it; all 26 are Confirmed. The lead's early smoke test listed 17 candidates, all reproduced as DEF-001 to DEF-017; nine more were found later. Severity describes impact and priority describes urgency:"));
add(table(["Severity", "Meaning in PyTodo Pro", "Priority", "Meaning"], [
  ["Critical", "Other users' data exposed or changed, security breach, data loss", "High", "Fix before release"],
  ["Major", "A main rule wrong with no workaround", "Medium", "Fix in next release"],
  ["Moderate", "Wrong behaviour with a workaround, inconsistent validation", "Low", "Fix when time allows"],
  ["Minor", "Cosmetic, wording or edge-case handling", "", ""],
], [1.2, 4.5, 1, 2.7], { fillCols: [0, 2] }));
add(T("Consolidated defect log (full Defect Report Template fields in the workbook)"));
add(table(["ID", "Title", "Severity", "Priority", "Status"], D.defects.map((d) => [d.id, d.title, d.severity, d.priority, d.status]),
  [1, 5.6, 1.1, 1, 1.1], { size: 18, fillCols: [2, 3] }));
const sev = img(R("08_Final_QA_Report/charts/defects_by_severity.png"), 210)[0];
const area = img(R("08_Final_QA_Report/charts/defects_by_feature.png"), 245)[0];
add(new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, children: [
  new ImageRun({ type: "png", data: fs.readFileSync(R("08_Final_QA_Report/charts/defects_by_severity.png")), transformation: { width: 268, height: 145 }, altText: { title: "severity", description: "Defects by severity", name: "sev" } }),
  new TextRun("  "),
  new ImageRun({ type: "png", data: fs.readFileSync(R("08_Final_QA_Report/charts/defects_by_feature.png")), transformation: { width: 320, height: 180 }, altText: { title: "area", description: "Defects by area", name: "area" } }),
] }));
add(caption("Defects by severity (left) and by area (right)"));
add(P(`${m.severity.Critical + m.severity.Major} of ${m.defects_total} defects (${Math.round(100 * (m.severity.Critical + m.severity.Major) / m.defects_total)}%) are Critical or Major. Input validation is the largest cluster (7), then GUI/accessibility (5): most defects sit where the developer trusted user input. A static code review located the root cause of most of them in a few lines, showing how cheap early reviews would have been compared with fixing defects after release.`));
const d5 = def["DEF-005"];
add(T("Example of a complete defect report (DEF-005)"));
add(table(["Field", "Value"], [
  ["Defect ID / Title", `${d5.id}: ${d5.title}`], ["Affected feature / Environment", `${d5.feature} · ${d5.env}`],
  ["Preconditions", d5.pre], ["Steps to reproduce", d5.steps], ["Expected result", d5.expected], ["Actual result", d5.actual],
  ["Severity / Priority / Status", `${d5.severity} / ${d5.priority} / ${d5.status}`], ["Evidence", `${d5.tests}; ${d5.evidence}`],
], [2.4, 7], { size: 18 }));

// ================================================================= 11 METRICS
add(H1("11. SQA Metrics and Final Quality Evaluation"));
add(img(R("08_Final_QA_Report/charts/results_by_phase.png"), 360, "Test results by phase"));
add(T("Test and defect metrics"));
add(table(["Metric", "Formula / working", "Value"], [
  ["Planned / executed", "count; passed + failed + blocked", `${O.planned} / ${O.executed}`],
  ["Passed / failed / blocked / not run", "count", `${O.passed} / ${O.failed} / ${O.blocked} / ${O.not_run}`],
  ["Execution rate", "executed ÷ planned × 100", pct(O.execution_rate)],
  ["Pass rate", "passed ÷ executed × 100", pct(O.pass_rate)],
  ["Automation rate", "automated ÷ planned × 100", `${m.automated_cases} ÷ ${O.planned} = ${m.automation_rate}%`],
  ["Confirmed defects (Critical + Major)", "count", `${m.defects_total} (${m.severity.Critical + m.severity.Major})`],
  ["Defect density", `${m.defects_total} ÷ ${(m.python_loc / 1000).toFixed(3)} KLOC (app.py + helpers.py)`, `${m.defect_density_per_kloc} per KLOC`],
  ["Coverage (helpers.py / app.py)", "statement %, branch %", `${ch.stmt_pct}/${ch.branch_pct}% · ${ca.stmt_pct}/${ca.branch_pct}%`],
], [3, 4, 2.4]));
add(P("A 71% pass rate does not mean weak testing: tests were designed to find defects, many on edges and negative cases (Myers et al., 2011). Defect density looks high because the application is tiny (557 lines) and several defects are in templates or CSS, so it is only a rough indicator."));
add(H2("11.1 Combined evidence and residual risk"));
add(table(["Area", "Result", "Key evidence"], [
  ["API", `${G["Web & API (Wk 4)"].passed}/${api.length} passed`, "Happy paths pass; negative tests and ownership checks fail"],
  ["Security", `${G["Security (Wk 5)"].passed}/${sec.length} passed`, "Session forgery, SQL injection, XSS, CSRF, no rate limit"],
  ["Performance", `${G["Performance (Wk 5)"].passed}/${ofGroup("Performance (Wk 5)").length} passed`, "Normal pages < 15 ms p95 at 50 users; login slow in bursts"],
  ["Usability / accessibility", `${G["Accessibility (Wk 3)"].passed}/${acc.length} WCAG checks passed`, "Easy to learn; unlabeled fields, contrast, reflow, little feedback"],
  ["Compatibility", "Chrome tested; others in progress", "Desktop and tablet pass; phone layout fails"],
], [2.2, 2.6, 4.6]));
add(P("Because no defect has been fixed, every confirmed risk remains (residual risk):"));
add(T("Residual risks"));
add(table(["Risk", "Level", "Evidence", "Recommended action"],
  D.risks.map((r) => [r[1], r[7] >= 6 ? "High" : r[7] >= 3 ? "Medium" : "Low", r[8], r[9]]), [3, 0.9, 2.2, 3.3], { size: 18, fillCols: [1] }));
add(P("**Important untested areas:** Safari and real phones; the API `status=open` filter; screen-reader testing with real users; long-running reliability, crash recovery and concurrent edits; production-like performance; automated security scanning (e.g. OWASP ZAP), which the brief did not allow."));
add(H2("11.2 Overall quality assessment"));
add(T("Quality by ISO/IEC 25010 characteristic"));
add(table(["Characteristic", "Rating", "Reason"], [
  ["Functional suitability", "Fair", "Main flows correct; urgency and validation boundaries wrong"],
  ["Security", "Poor", "Cross-user delete, SQL injection, XSS, session forgery"],
  ["Reliability", "Poor", "One bad date permanently crashes a user's pages; wrong types give 500"],
  ["Usability", "Fair", "Easy to learn; weak feedback and phone layout"],
  ["Performance efficiency", "Good", "Fast at expected load; login slow only in bursts"],
  ["Compatibility", "Fair (partly tested)", "Chrome desktop/tablet fine; phone fails"],
  ["Maintainability", "Good", "Small, readable code; helpers.py easy to test (V(G) ≤ 5)"],
  ["Portability", "Not evaluated", "Only run locally"],
], [2.6, 1.8, 5]));
add(P("PyTodo Pro is a good prototype with a clean, testable structure, but on our evidence it is **not fit for release** until the Critical and Major defects are fixed and the regression suite passes. Testing shows the presence of defects, not their absence (ISTQB, 2023), and the untested areas still carry risk."));
add(P("**How our understanding changed:** in Week 1 we expected date logic to be the main risk; BVA confirmed it, and decision tables exposed a missing rule. Week 2 taught us that 100% coverage is not correctness. Testing the API separately in Week 4 changed our view most, because the web pages protected actions that the API did not. STRIDE in Week 5 turned vague concerns into concrete tests and found the most serious defects, so several risk scores rose to the maximum."));

// ================================================================= 12 STANDARDS
add(H1("12. Standards Integration and Recommendations"));
add(H2("12.1 ISO/IEC 25010 characteristics evaluated"));
add(P("Functional suitability, security, usability and performance efficiency were evaluated **directly**; compatibility **partly** (Chrome at three screen sizes); reliability and maintainability **indirectly** (error handling, code review, V(G)); portability was **not adequately evaluated** (ISO & IEC, 2011). Also not adequately evaluated: availability and recoverability, capacity on a real server, and accessibility with real users. IEEE 829 shaped our plan, test case and defect report structure (IEEE, 2008), and our weekly cycle of plan, test, review and adjust mirrors ISO 9001's plan-do-check-act approach."));
add(H2("12.2 Regression tests in CI/CD and continuous testing"));
add(P("We wrote an example GitHub Actions pipeline (.github/workflows/qa.yml) in which cheap checks run first and stop the pipeline early:"));
add(T("Proposed CI/CD quality gates"));
add(table(["Stage", "What runs", "Gate", "Would have caught"], [
  ["Static analysis", "Bandit, flake8", "No high findings", "Hard-coded secret, f-string SQL, debug=True"],
  ["Unit tests", "pytest -m unit with coverage", "All pass; branch ≥ 90%", "DEF-001, 002, 003"],
  ["API regression", "pytest -m \"regression and not ui\"", "All pass", "DEF-004, 005, 007, 008, 009"],
  ["UI smoke", "Selenium headless", "All pass", "Broken pages, XSS"],
  ["Nightly", "Locust baseline, Axe scan", "No regression", "DEF-021, 026"],
], [1.7, 2.8, 2, 2.9]));
add(P("This is continuous testing: every change is checked automatically, a fixed defect cannot quietly return, and testing moves left to the moment code is written, where fixes are cheapest."));
add(H2("12.3 Process improvements for Agile/DevOps"));
add(table(["Improvement", "Prevents", "Where it fits"], [
  ["Acceptance criteria with boundary examples in user stories", "DEF-001, 002, 003", "Backlog refinement"],
  ["Secure-coding checklist in code review (parameterised SQL, ownership checks, no |safe, no secrets)", "DEF-005, 006, 007, 014", "Pull request review"],
  ["One shared server-side validation function for web and API", "DEF-008–011, 013, 018", "Definition of Done"],
  ["UNIQUE username, CSRF tokens, rate limiting", "DEF-004, 015, 019", "Framework setup"],
  ["Accessibility checklist and Axe in CI", "DEF-021, 022, 023", "Definition of Done"],
], [5, 2.2, 2.2]));
add(P("The original development shows no evidence of reviews, standards or automated checks, typical of CMMI Level 1 (Initial). Our project introduces defined test processes (Level 3) and metrics, a first step towards Level 4 (Managed)."));
add(H2("12.4 Prioritised recommendations and future testing"));
add(numbered([
  "**Fix now (Critical):** scope DELETE by user_id (DEF-005); parameterise search SQL (DEF-006); remove |safe (DEF-007); validate input on the server (DEF-008); move SECRET_KEY to an environment variable and turn debug off (DEF-014).",
  "**Fix next (Major):** urgency boundary (DEF-001), password `>= 8` (DEF-002), unique usernames (DEF-004), CSRF tokens (DEF-015), form labels (DEF-021).",
  "**Then:** Moderate and Minor defects, starting with DEF-018, 019 and 020; re-run the full suite for confirmation and regression testing.",
  "**Future testing:** complete the browser matrix including Safari; screen-reader testing; production-like load test; OWASP ZAP scan; add the status=open API test; refresh tests regularly to avoid the pesticide paradox.",
], "num3"));

// ================================================================= 13 CONCLUSION
add(H1("13. Conclusion"));
add(P(`Over eight weeks we applied the course's techniques to one real application: black-box and white-box design, special testing types, web and API testing, security and performance testing, automation, test management and metrics. We designed ${O.planned} test cases, executed ${O.executed} and confirmed ${m.defects_total} defects, each with evidence and a linked test. The key lessons were that boundaries and server-side validation hide many defects, that full coverage does not mean correct code, and that testing the API directly reveals problems the UI hides. PyTodo Pro handles everyday tasks well but should not be released until its Critical and Major defects are fixed; our tests, regression suite and CI pipeline are ready for that next cycle.`));

// ================================================================= REFERENCES (APA 7)
add(H1("References"));
const ref = (parts) => new Paragraph({ indent: { left: 720, hanging: 720 }, spacing: { after: 120, line: 252 },
  children: parts.map(([t, it]) => new TextRun({ text: t, italics: !!it, font: FONT, size: 24 })) });
[
  [["Balogun, A. O. (2026). "], ["Software testing and quality assurance (TEB3433/TFB3433): Chapters 1–12", 1], [" [Lecture slides]. Universiti Teknologi PETRONAS."]],
  [["Batchelder, N. (n.d.). "], ["Coverage.py documentation", 1], [". https://coverage.readthedocs.io/"]],
  [["Deque Systems. (n.d.). "], ["axe-core", 1], [" [Computer software]. GitHub. https://github.com/dequelabs/axe-core"]],
  [["IEEE. (2008). "], ["IEEE standard for software and system test documentation", 1], [" (IEEE Std 829-2008). https://doi.org/10.1109/IEEESTD.2008.4578383"]],
  [["International Organization for Standardization & International Electrotechnical Commission. (2011). "], ["Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — System and software quality models", 1], [" (ISO/IEC Standard No. 25010:2011)."]],
  [["International Software Testing Qualifications Board. (2023). "], ["Certified Tester Foundation Level syllabus", 1], [" (Version 4.0). https://www.istqb.org/"]],
  [["Locust. (n.d.). "], ["Locust documentation", 1], [". https://docs.locust.io/"]],
  [["Myers, G. J., Badgett, T., & Sandler, C. (2011). "], ["The art of software testing", 1], [" (3rd ed.). Wiley."]],
  [["OWASP Foundation. (2021). "], ["OWASP Top 10: 2021", 1], [". https://owasp.org/Top10/"]],
  [["Pallets. (n.d.). "], ["Flask documentation", 1], [". https://flask.palletsprojects.com/"]],
  [["pytest-dev. (n.d.). "], ["pytest documentation", 1], [". https://docs.pytest.org/"]],
  [["Selenium Project. (n.d.). "], ["Selenium documentation", 1], [". https://www.selenium.dev/documentation/"]],
  [["W3C. (2018). "], ["Web Content Accessibility Guidelines (WCAG) 2.1", 1], [". https://www.w3.org/TR/WCAG21/"]],
].forEach((r) => add(ref(r)));

// ================================================================= APPENDIX
add(H1("Appendix A: Repository Contents and How to Run the Tests"));
add(P("The GitHub repository follows the structure suggested in the brief. Each folder has a README that maps the brief's deliverable contents to files."));
add(table(["Folder", "Contents"], [
  ["01_Black_Box", "Feature inventory, risk matrix, EP/BVA/decision-table/state-transition design, 49 test cases, PyTest suite"],
  ["02_White_Box_Coverage", "Unit selection, control flow graphs, 29 unit tests, HTML coverage reports"],
  ["03_Special_Testing", "GUI, accessibility, compatibility, usability results; Axe output; 21 screenshots; manual checklist"],
  ["04_Web_API", "Web scenarios, 46 API tests with request data, expected and actual results"],
  ["05_Security_Performance", "STRIDE table, 14 security tests, Locust workload, raw results, performance report"],
  ["06_Automation_Regression", "Selenium tests with Page Object Model, manual-to-automated map, regression suite, evidence"],
  ["07_Test_Management", "Test Plan and Strategy, master test repository, RTM, defect log, risk register, execution logs"],
  ["08_Final_QA_Report · 09_Presentation", "This report, metrics and charts · demo script and slides"],
  ["tools · .github/workflows", "Test catalogue and scripts that rebuild all documents from results · CI/CD pipeline"],
], [2.8, 6.6], { size: 20 }));
add(P("**Setup:** `pip install -r app/requirements.txt -r requirements-test.txt`. **Non-UI tests:** `pytest -m \"not ui\"` (expected: 100 pass, 37 fail, each failure a known defect). **Regression:** `pytest -m regression`. **UI tests:** start the app with `python app.py` in app/, then `pytest -m ui` (set BROWSER=edge or firefox for other browsers). **Rebuild all documents:** `bash tools/run_all.sh`."));

// ================================================================= DOCUMENT
const hs = (id, name, size, before, after, lvl) => ({ id, name, basedOn: "Normal", next: "Normal", quickFormat: true,
  run: { font: FONT, size, bold: true, color: "000000" },
  paragraph: { spacing: { before, after }, keepNext: true, keepLines: true, outlineLevel: lvl } });
const doc = new Document({
  features: { updateFields: true },
  creator: "PyTodo Pro QA Group", title: "PyTodo Pro Final QA Report",
  styles: {
    default: { document: { run: { font: FONT, size: 24 } } },
    paragraphStyles: [
      hs("Heading1", "Heading 1", 28, 0, 200, 0),
      hs("Heading2", "Heading 2", 26, 240, 120, 1),
      hs("Heading3", "Heading 3", 24, 200, 80, 2),
      { id: "Caption", name: "caption", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 20, bold: true } },
    ],
  },
  numbering: L.numberingConfig,
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 20 })] })] }) },
    children: C,
  }],
});
Packer.toBuffer(doc).then((buf) => {
  const out = R("08_Final_QA_Report/PyTodo_Pro_Final_QA_Report.docx");
  fs.writeFileSync(out, buf);
  console.log("written", out);
});
