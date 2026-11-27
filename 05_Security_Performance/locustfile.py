"""
Week 5 - Controlled performance / load experiment with Locust.

Workload (defined BEFORE execution):
  - Each virtual user logs in once as the seeded user 'perf_user' (100 tasks).
  - Then repeats, with 1-2 s think time:
        60%  GET  /api/tasks?per_page=10     (busiest read: task list)
        30%  GET  /api/dashboard             (reads ALL tasks + urgency logic)
        10%  POST /api/tasks                 (write)
  - Load levels: 1, 10, 25, 50 concurrent users, 40 s each (see run_perf.sh).

Seed first:  python 05_Security_Performance/seed_perf.py
"""

import random

from locust import HttpUser, between, task


class TodoUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        self.client.post("/api/login", json={"username": "perf_user", "password": "Passw0rd123"})

    @task(6)
    def list_tasks(self):
        self.client.get("/api/tasks?per_page=10", name="GET /api/tasks")

    @task(3)
    def dashboard(self):
        self.client.get("/api/dashboard", name="GET /api/dashboard")

    @task(1)
    def create(self):
        self.client.post("/api/tasks", json={"title": f"load task {random.randint(1, 99999)}"},
                         name="POST /api/tasks")
