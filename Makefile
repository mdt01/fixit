# One name for each kind of check (agents and people use the same commands).
PY ?= python

.PHONY: run seed test lint format types security audit check

run:
	$(PY) -m uvicorn app.main:app --reload

seed:
	$(PY) -m scripts.seed

test:
	$(PY) -m pytest

lint:
	$(PY) -m ruff check .
	$(PY) -m ruff format --check .

format:
	$(PY) -m ruff format .

types:
	$(PY) -m mypy --strict app

security:
	$(PY) -m bandit -q -r app scripts

audit:                  # needs internet: checks pinned versions for known advisories
	$(PY) -m pip_audit -r requirements.txt

check: lint types test security
