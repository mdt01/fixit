"""Check: fail if a change would add files that never belong in Git.

Born from a real factory run: every stage passed, and the commit contained a SQLite
database the tests had created. Every failure becomes a check.
"""

import re
import subprocess
import sys

STRAY = re.compile(r"\.(db|sqlite3?|log|pyc)$|(^|/)(\.env|__pycache__|\.pytest_cache)(/|$)")

status = subprocess.run(
    ["git", "status", "--porcelain", "--untracked-files=all"],
    capture_output=True,
    text=True,
    check=True,
).stdout
paths = [line[3:].strip().strip('"') for line in status.splitlines()]
stray = [p for p in paths if STRAY.search(p)]
if stray:
    print("Files that should not be committed:")
    print("\n".join(f"  {p}" for p in stray))
    print("Delete them, or add a pattern to .gitignore if the tools create them.")
    sys.exit(1)
print(f"no stray files ({len(paths)} changed paths checked)")
