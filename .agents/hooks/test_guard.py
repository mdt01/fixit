"""stop hook: the agent may not finish if it deleted, skipped or weakened a test.

Compares every test in tests/ with the last commit (git HEAD). New tests are welcome;
fewer assertions, new skips or "assert True" are not. Exit 2 = not finished yet.
If a test really must change, the user commits that change first.
"""

import ast
import subprocess

from _common import ROOT, block, event


def fingerprint(source: str) -> dict[str, tuple[int, bool, bool]]:
    """{test name: (assertions, skipped, trivial)} for one test file."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {}
    tests = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test"):
            asserts = [n for n in ast.walk(node) if isinstance(n, ast.Assert)]
            raises = [
                n for n in ast.walk(node) if isinstance(n, ast.Attribute) and n.attr == "raises"
            ]
            marks = " ".join(ast.unparse(d) for d in node.decorator_list)
            skipped = "skip" in marks or "xfail" in marks or "pytest.skip(" in ast.unparse(node)
            trivial = any(isinstance(a.test, ast.Constant) and a.test.value for a in asserts)
            tests[node.name] = (len(asserts) + len(raises), skipped, trivial)
    return tests


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout


event()  # read the event; we check every time
problems = []
for path in git("ls-tree", "-r", "--name-only", "HEAD", "tests/").split():
    if not path.endswith(".py"):
        continue
    old = fingerprint(git("show", f"HEAD:{path}"))
    file = ROOT / path
    new = fingerprint(file.read_text(encoding="utf-8")) if file.is_file() else {}
    for name, (asserts, skipped, trivial) in old.items():
        if name not in new:
            problems.append(f"{path}::{name} was deleted")
        elif new[name][1] and not skipped:
            problems.append(f"{path}::{name} is now skipped")
        elif new[name][0] < asserts:
            problems.append(f"{path}::{name} lost assertions ({asserts} -> {new[name][0]})")
        elif new[name][2] and not trivial:
            problems.append(f"{path}::{name} now asserts a constant")
if problems:
    block(
        "You weakened the test suite:\n- "
        + "\n- ".join(problems)
        + "\nRestore these tests and fix the code instead. If a test is really "
        "wrong, stop and explain why to the user."
    )
