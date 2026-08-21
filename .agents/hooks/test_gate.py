"""stop hook: the agent may not finish while FixIt's tests fail.

Runs only if the agent changed files in this turn. Re-runs only the failed tests once,
so that a single flaky failure does not block; if they fail again, the agent is blocked.
Exit 2 = not finished yet.
"""

import subprocess

from _common import ROOT, block, event, project_python

e = event()
if not e.get("changed_files"):
    raise SystemExit(0)  # nothing changed, nothing to check

python = project_python()
run = subprocess.run(
    [python, "-m", "pytest", "-q", "--disable-warnings"], cwd=ROOT, capture_output=True, text=True
)
if run.returncode != 0:
    rerun = subprocess.run(
        [python, "-m", "pytest", "-q", "--lf", "--disable-warnings"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if rerun.returncode != 0:
        tail = "\n".join(rerun.stdout.strip().splitlines()[-15:])
        block(
            f"The test suite fails after your changes. Fix the code (not the tests) "
            f"and finish again.\n{tail}"
        )
print("test gate: " + run.stdout.strip().splitlines()[-1] if run.stdout.strip() else "")
