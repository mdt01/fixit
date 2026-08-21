"""post_tool hook: after every edit, check the file and tell the agent what is wrong.

Always: Python syntax check. If ruff is installed: lint the file too.
Exit 0 with a message = feedback for the model (the edit has already happened).
"""

import py_compile
import shutil
import subprocess

from _common import ROOT, event

e = event()
path = e.get("arguments", {}).get("path", "")
if path.endswith(".py") and (ROOT / path).is_file():
    try:
        py_compile.compile(str(ROOT / path), doraise=True)
    except py_compile.PyCompileError as exc:
        print(f"SYNTAX ERROR in {path} - fix it before anything else:\n{exc.msg}")
        raise SystemExit(0)
    if shutil.which("ruff"):
        lint = subprocess.run(
            ["ruff", "check", "--quiet", path], cwd=ROOT, capture_output=True, text=True
        )
        if lint.returncode != 0:
            print(f"ruff found problems in {path}:\n{lint.stdout.strip()[:1500]}")
