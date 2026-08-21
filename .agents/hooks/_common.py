"""Shared helpers for FixIt's agent hooks."""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def event() -> dict:
    """The event the agent harness sends on standard input."""
    return json.load(sys.stdin)


def project_python() -> str:
    """The Python that has FixIt's dependencies (not necessarily the agent's own).

    Order: $FIXIT_PYTHON, then .venv in the project, then the current interpreter.
    """
    if os.getenv("FIXIT_PYTHON"):
        return os.environ["FIXIT_PYTHON"]
    for candidate in (ROOT / ".venv" / "Scripts" / "python.exe", ROOT / ".venv" / "bin" / "python"):
        if candidate.is_file():
            return str(candidate)
    return sys.executable


def block(message: str) -> None:
    """Refuse the action; the message goes back to the model."""
    print(message, file=sys.stderr)
    sys.exit(2)
