# FixIt — notes for coding agents

FixIt tracks campus maintenance tickets: students report, wardens assign,
technicians fix. Python 3.12, FastAPI, SQLAlchemy 2, SQLite. Read `docs/spec.md`
before changing behaviour; requirement ids (T-3, A-2 ...) appear in tests.

## Commands
- Set up: `python -m venv .venv`, activate it, `pip install -r requirements-dev.txt`
- Run: `make seed` then `make run` (http://127.0.0.1:8000, API docs at /docs)
- Check everything: `make check` (ruff, mypy, pytest, bandit). Must pass before "done".
- One test file: `python -m pytest tests/test_tickets.py -q`

## Where things go
- `app/rules.py` — business rules as pure functions. No database, no FastAPI.
- `app/services.py` — applies rules to the database. Every function takes `now` if
  time matters.
- `app/routers/` — HTTP only: parse, call a service, return. No rules here.
- `tests/` — one file per area; fixtures in `tests/conftest.py` (`people`, `ticket`).

## Rules
- Every endpoint checks the user's role and whether they may see the ticket.
  Hidden tickets answer 404, never 403 (spec T-7).
- Times are UTC (`rules.utcnow()`); never call `datetime.now()` in app code.
- Write the failing test first; never delete or weaken a test to make it pass.
- No new dependencies without asking. No secrets in code; settings via `app/config.py`.
- Keep pull requests small: one slice of `docs/plan.md` at a time.

See `app/AGENTS.md` for code conventions inside the app.
