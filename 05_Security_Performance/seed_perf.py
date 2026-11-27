"""Create 'perf_user' with 100 tasks on the running app (http://127.0.0.1:5000)."""
from datetime import date, timedelta

import requests

BASE = "http://127.0.0.1:5000"
s = requests.Session()
r = s.post(f"{BASE}/api/register", json={"username": "perf_user", "password": "Passw0rd123"})
if r.status_code != 201:
    s.post(f"{BASE}/api/login", json={"username": "perf_user", "password": "Passw0rd123"})
for i in range(100):
    due = (date.today() + timedelta(days=(i % 15) - 5)).isoformat()
    s.post(f"{BASE}/api/tasks", json={"title": f"Seed task {i}", "category_id": (i % 4) + 1, "due_date": due})
print("perf_user tasks:", s.get(f"{BASE}/api/dashboard").json())
