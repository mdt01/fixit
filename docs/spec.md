# FixIt — specification (release 1)

Each requirement has an id. Tests name the requirement they check (for example,
`test_full_life_cycle` checks T-3 to T-6).

## Accounts and access
- **A-1** Users log in with e-mail and password and receive a token valid for 12 hours.
- **A-2** A wrong password and an unknown e-mail give the same 401 answer.
- **A-3** Passwords and tokens are stored only as hashes.
- **A-4** Every endpoint except `/health`, `/` and `/auth/login` needs a valid token.

## Tickets
- **T-1** Only students report tickets: title (5–120 chars), description (10–2000),
  category, location and priority (normal or urgent).
- **T-2** The deadline is `created_at + SLA`: electrical 24 h, plumbing 24 h,
  internet 48 h, furniture 72 h, cleaning 12 h, other 72 h. Urgent tickets get a quarter
  of that, but never less than 4 hours.
- **T-3** Life cycle: open → assigned → in_progress → resolved → closed. A warden can
  cancel a ticket that is open or assigned; a student can cancel their own ticket only
  while it is open; a warden can un-assign (assigned → open). Work in progress is
  finished by resolving it, not cancelled.
- **T-4** Only a warden assigns, and only to a technician.
- **T-5** Only the assigned technician starts and resolves a ticket; resolving needs a
  note saying what was fixed (stored as a comment).
- **T-6** The reporting student or a warden closes a resolved ticket.
- **T-7** Students see only their own tickets, technicians only tickets assigned to them,
  wardens all tickets. A ticket the user may not see answers 404, exactly like one that
  does not exist.
- **T-8** A ticket is overdue when it is open, assigned or in progress after its deadline.
- **T-9** The reporting student can reopen a resolved or closed ticket within 7 days of
  `resolved_at`. A reopened ticket is unassigned and gets a fresh deadline.

## Reports (wardens only)
- **R-1** `GET /reports/overdue`: overdue tickets, earliest deadline first.
- **R-2** `GET /reports/workload`: per technician, active and overdue tickets.
- **R-3** `GET /reports/overdue.csv`: the overdue report as CSV for spreadsheets.

## Quality
- **Q-1** `make check` (lint, types, tests, security scan) passes on every commit.
- **Q-2** All times are stored and returned in UTC.
- **Q-3** No secret is committed; settings come from environment variables.
