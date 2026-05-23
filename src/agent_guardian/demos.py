"""Example entry points (work after pip install -e .)."""

from __future__ import annotations

import runpy
from pathlib import Path

_EXAMPLES = Path(__file__).resolve().parents[2] / "examples"


def _run(script: str) -> None:
    path = _EXAMPLES / script
    if not path.is_file():
        raise FileNotFoundError(f"Example script not found: {path}")
    runpy.run_path(str(path), run_name="__main__")


def run_quickstart() -> None:
    _run("quickstart_no_agent.py")
