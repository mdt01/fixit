# Contributing to FixIt

1. Pick an issue, or a slice of `docs/plan.md`. Comment that you are taking it.
2. Branch from `main`: `git switch -c <issue-number>-<short-name>`.
3. Write or update the requirement in `docs/spec.md`, then the failing tests.
4. Make the change (with or without an agent). Run `make check` until it passes.
5. Open a pull request using the template. Disclose AI assistance. Keep it under
   about 300 changed lines; split bigger work into stacked pull requests.
6. One approving review is required; `.github/CODEOWNERS` adds the right reviewer
   for security-sensitive files.

Agents follow the same rules: see `AGENTS.md`.
