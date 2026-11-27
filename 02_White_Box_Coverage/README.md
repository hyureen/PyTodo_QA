# Week 2 – White-Box Testing and Coverage

**Result:** 29 planned, 29 executed, **26 passed, 3 failed**. helpers.py **100.0% statement / 100.0% branch** coverage;
app.py 98.3% / 89.1% (all suites).

| Brief deliverable | Where to find it |
| --- | --- |
| Selected code units and justification | [White_Box_Analysis.md §1](White_Box_Analysis.md) |
| Control-flow analysis | [White_Box_Analysis.md §2](White_Box_Analysis.md), [cfg/](cfg/) (CFG diagrams + .dot sources) |
| White-box test cases | [White_Box_Test_Cases.xlsx](White_Box_Test_Cases.xlsx) |
| Automated/unit test file | [test_whitebox_helpers.py](test_whitebox_helpers.py) |
| Coverage report and interpretation | [htmlcov_helpers/index.html](htmlcov_helpers/index.html), [htmlcov_full/index.html](htmlcov_full/index.html), [White_Box_Analysis.md §4](White_Box_Analysis.md) |

**Run:** `pytest -m unit --cov=app --cov-branch --cov-report=html`
