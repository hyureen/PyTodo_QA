# Week 4 – Web and API Testing

**Result:** 46 planned, 46 executed, **28 passed, 18 failed**.

| Brief deliverable | Where to find it |
| --- | --- |
| Web test scenarios | [Web_and_API_Testing.md §1](Web_and_API_Testing.md) (+ black-box and Selenium suites) |
| API test suite | [test_api.py](test_api.py) |
| Request / test data | [API_Test_Cases.xlsx](API_Test_Cases.xlsx) column *Test Data* |
| Expected versus actual status / response | [API_Test_Cases.xlsx](API_Test_Cases.xlsx); [Web_and_API_Testing.md §3](Web_and_API_Testing.md) |
| Execution evidence and defects | log `07_Test_Management/results/pytest_core_log.txt`; [Web_and_API_Testing.md §4](Web_and_API_Testing.md) |

**Run:** `pytest 04_Web_API -v` (no server needed – Flask test client, fresh database per test)
