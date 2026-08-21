"""pre_tool hook: never let an agent touch secrets, CI, migrations or its own guardrails.

Prose in AGENTS.md can be forgotten or ignored; this check runs every time.
"""

import fnmatch
import re

from _common import block, event

PROTECTED = [
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "migrations/*",
    ".github/workflows/*",
    ".agents/hooks/*",
    ".agents/hooks.json",
    ".agents/permissions.json",
]
DANGEROUS_SHELL = [r"\.env\b", r"\bgit\s+push\b", r"\bmigrations/", r"\.agents/"]

e = event()
args = e.get("arguments", {})
if e["tool"] == "edit_file":
    path = args.get("path", "").replace("\\", "/").removeprefix("./")
    for pattern in PROTECTED:
        if fnmatch.fnmatch(path, pattern):
            block(
                f"'{path}' is protected (matches {pattern}). Do not edit it; "
                "explain to the user what change is needed instead."
            )
elif e["tool"] == "run_bash":
    command = args.get("command", "")
    if re.search(r"(>|>>|\bsed\s+-i|\brm\b|\bmv\b)", command):  # writes or deletes
        for pattern in DANGEROUS_SHELL:
            if re.search(pattern, command):
                block(
                    f"This command would modify a protected file or push code: "
                    f"'{command}'. Ask the user to do it."
                )
    if re.search(r"\bgit\s+push\b", command):
        block("Agents do not push in this project. Commit locally and tell the user.")
