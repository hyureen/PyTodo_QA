# Week 5 – Security and Performance Testing

**Result:** security 14 planned, 14 executed, **6 passed, 8 failed**; performance 5 planned, 5 executed, **3 passed, 2 failed**.
All security tests run only against a temporary local database (no uncontrolled penetration testing).

| Brief deliverable | Where to find it |
| --- | --- |
| Threat / STRIDE table | [STRIDE_Threat_Table.md](STRIDE_Threat_Table.md) |
| Security test cases and findings | [test_security.py](test_security.py), [Security_Performance_Test_Cases.xlsx](Security_Performance_Test_Cases.xlsx) |
| Performance objective and workload | [Performance_Report.md §1](Performance_Report.md), [locustfile.py](locustfile.py) |
| Performance results and interpretation | [Performance_Report.md §2–3](Performance_Report.md), raw data [perf_results/](perf_results/) |
| Limitations and recommendations | [Performance_Report.md §4](Performance_Report.md), [STRIDE_Threat_Table.md](STRIDE_Threat_Table.md) |

**Run:** `pytest 05_Security_Performance -v` · load test (app running): `bash 05_Security_Performance/run_perf.sh`
