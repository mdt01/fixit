# One name for each kind of check (agents and people use the same commands).
PY ?= python

.PHONY: run seed test lint format types security check

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
	$(PY) -m mypy app

security:
	$(PY) -m bandit -q -r app scripts

check: lint types test security
