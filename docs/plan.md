# FixIt — delivery plan (release 1)

Each slice is one pull request: tests first, then code, then review. A slice is done
when `make check` passes and a teammate has reviewed it.

| Slice | Scope | Spec ids | Tests first |
|---|---|---|---|
| S0 | Walking skeleton: app, `/health`, Makefile, CI | Q-1, Q-3 | `test_health` |
| S1 | Rules module: SLA, life cycle, overdue | T-2, T-3, T-8, Q-2 | `tests/test_rules.py` incl. properties |
| S2 | Accounts: users, password hashing, login, tokens, roles | A-1..A-4 | `tests/test_auth.py` |
| S3 | Tickets API: report, list, detail, assign, status, comments | T-1..T-7 | `tests/test_tickets.py` |
| S4 | Reports: overdue, workload | R-1, R-2 | `tests/test_reports.py` |
| S5 | Web page: log in, report, list | T-1, T-7 | manual check + smoke script |
| S6 | Agent tooling: agent files, hooks, skill, MCP server | — | `mcp_server/tests` |

## Risks
- Access control mistakes (students seeing others' tickets) → tests for every role in
  S3; review rule; security scan.
- Time-zone bugs → UTC everywhere (Q-2); every rule takes `now` as an argument.
- Scope creep (notifications, photos) → out of scope in the brief; new ideas go to issues.
