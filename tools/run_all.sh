#!/usr/bin/env bash
# Runs every automated suite, saves logs + coverage, then rebuilds all test-management artefacts.
# UI tests need the app running (cd app && python app.py) - they are skipped otherwise.
set -u
cd "$(dirname "$0")/.."
mkdir -p 07_Test_Management/results
python3 -m pytest -m "not ui" --cov=app --cov-branch \
    --cov-report=html:02_White_Box_Coverage/htmlcov_full --cov-report=json:07_Test_Management/results/coverage_full.json \
    --junitxml=07_Test_Management/results/junit_core.xml -q -rA > 07_Test_Management/results/pytest_core_log.txt 2>&1
python3 -m pytest 02_White_Box_Coverage -m unit --cov=app --cov-branch \
    --cov-report=html:02_White_Box_Coverage/htmlcov_helpers --cov-report=json:07_Test_Management/results/coverage_helpers.json \
    --cov-report=term-missing -q > 07_Test_Management/results/pytest_whitebox_log.txt 2>&1
python3 -m pytest -m ui --junitxml=07_Test_Management/results/junit_ui.xml -q -rA \
    > 07_Test_Management/results/pytest_ui_log.txt 2>&1
python3 -m pytest -m regression --junitxml=07_Test_Management/results/junit_regression.xml -q -rA \
    > 07_Test_Management/results/pytest_regression_log.txt 2>&1
python3 tools/build_artefacts.py
python3 tools/build_folder_deliverables.py
