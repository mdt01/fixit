---
name: add-endpoint
description: Add or change a FixIt API endpoint the project's way - schema, rule, service, router and tests, test first. Use when asked for a new endpoint, a new filter or field in an API response, or a new report.
---
# Adding an endpoint to FixIt

1. Find the requirement in `docs/spec.md` (or ask the user to add one). Note its id.
2. Write the tests first in the matching `tests/test_*.py`, using the `people` and
   `ticket` fixtures. Cover: the happy path, every role that must be refused (403 for
   a wrong role, 404 for a ticket the user may not see), and invalid input (422).
   Run them and confirm they fail for the right reason.
3. Business rule? Add a pure function to `app/rules.py` with its own unit test.
4. Add the service function in `app/services.py` (takes `db`, the user and `now`).
5. Add the route in `app/routers/`: a schema from `app/schemas.py`, the right
   `require(...)` dependency, and no logic beyond calling the service.
6. Run `make check`. Fix the code, not the tests.
7. Report: the spec id, files changed, test names, and the `make check` summary line.

Never return data from tickets the user may not see. Never use `datetime.now()`.
