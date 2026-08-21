# Inside app/

- Raise `RuleError("message for the user")` for broken business rules; `app/main.py`
  turns it into HTTP 400. Raise `services.NotFound` for missing or hidden tickets (404).
- Use `require(Role.WARDEN)` or `current_user` from `app/security.py` on every route.
- New request bodies get a Pydantic model in `app/schemas.py` with length limits
  (`Field(min_length=..., max_length=...)`).
- Return `services.to_out(ticket, now)` so the `overdue` flag is always computed.
- Type hints on every function; `make types` must stay clean.
