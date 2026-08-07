# One name for each kind of check (agents and people use the same commands).
PY ?= python

.PHONY: run seed test lint types security check

run:
	$(PY) -m uvicorn app.main:app --reload

seed:
	$(PY) -m scripts.seed

test:
	$(PY) -m pytest

lint:
	$(PY) -m ruff check .

types:
	$(PY) -m mypy app

security:
	$(PY) -m bandit -q -r app

check: lint types test security
