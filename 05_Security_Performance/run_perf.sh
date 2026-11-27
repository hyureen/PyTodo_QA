#!/usr/bin/env bash
# Runs the load experiment at 1, 10, 25 and 50 users (40 s each).
# App must be running:  cd app && python app.py
set -e
cd "$(dirname "$0")"
mkdir -p perf_results
python seed_perf.py
for USERS in 1 10 25 50; do
  echo "== $USERS users =="
  locust -f locustfile.py --headless --host http://127.0.0.1:5000 \
         -u "$USERS" -r "$USERS" -t 40s --csv "perf_results/u${USERS}" --only-summary
done
