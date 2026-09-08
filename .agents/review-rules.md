# FixIt review rules

Read by human reviewers and by AI review agents. Severity in brackets.

## Always flag
- [blocker] A route without `current_user` or `require(...)` (except /health, /, /auth/login).
- [blocker] Any way for a user to read or change a ticket that is not theirs
  (insecure direct object reference). Hidden tickets must answer 404.
- [blocker] Secrets, passwords or tokens in code, tests, logs or responses; tokens or
  passwords stored without hashing.
- [blocker] `innerHTML` or string-built HTML with user text in `app/static/`.
- [major] A business rule written in a router or service instead of `app/rules.py`.
- [major] `datetime.now()` or local time in app code (use `rules.utcnow()`, pass `now`).
- [major] New behaviour without a test, or a test weakened in the same change.
- [major] New request fields without length or range limits.

## Do not flag
- Style that ruff checks automatically.
- SQLite-specific choices (a tracked decision: docs/adr/0001).
