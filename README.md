# FixIt

Campus maintenance requests: students report problems, wardens assign them,
technicians fix them, and everyone can see where each ticket stands.
FixIt is the capstone project of *The Modern Software Developer*.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
make seed                          # demo accounts, password: demo-pass-2026
make run                           # http://127.0.0.1:8000  (API docs: /docs)
make check                         # lint, types, tests, security scan
```

No `make` on Windows? Run the commands from the `Makefile` directly, for example
`python -m pytest`.

Demo accounts: `asha@campus.example` and `rohan@campus.example` (students),
`kiran@campus.example` and `meena@campus.example` (technicians),
`warden@campus.example` (warden).

## Documents
- `docs/brief.md` - the problem and the users
- `docs/spec.md` - requirements with ids (tests refer to them)
- `docs/plan.md` - delivery slices
- `docs/adr/` - architecture decisions
- `AGENTS.md` - instructions for coding agents (and new teammates)

## Layout
```
app/rules.py      business rules (pure functions)      app/services.py   rules + database
app/routers/      HTTP endpoints                       app/security.py   passwords, tokens, roles
app/static/       the web page                         tests/            pytest suite
mcp_server/       MCP server for agents                specs/            factory specifications
.agents/          commands, hooks, skills, subagents, review rules, loops
```

## AI assistance
Built with coding agents under the practices of the book: specs and tests first,
small reviewed pull requests, every change verified by `make check`.
