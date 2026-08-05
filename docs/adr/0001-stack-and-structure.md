# ADR 0001 — Stack and structure

Status: accepted · Date: (your date) · Deciders: (your names)

## Context
FixIt must be small, cheap to run, easy for students and agents to change, and fast to
test. The team already knows Python and FastAPI from the CampusHub labs.

## Options considered
1. **FastAPI + SQLAlchemy + SQLite, rules in a pure module** — one process, no
   server to install; tests run in memory in seconds.
2. Django with its admin site — fast to start, but more framework to learn and a slower
   test suite; much of the admin would be unused.
3. A spreadsheet plus a form service — no code, but no access control per ticket and no
   way to compute deadlines and reports reliably.

## Decision
Option 1. Business rules live in `app/rules.py` as pure functions (no database, no web
framework), so they can be tested exhaustively, including property-based tests.
`app/services.py` applies the rules to the database; `app/routers/` only translate
HTTP to service calls. SQLite is enough for one campus; SQLAlchemy keeps the door open
to PostgreSQL.

## Consequences
- Agents get a clear place for every kind of change (router, service, rule).
- No background job runner in release 1: "overdue" is computed when asked.
- Moving to PostgreSQL later needs only a new `FIXIT_DB` URL and a migration tool.
