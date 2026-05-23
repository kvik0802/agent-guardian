"""Registered demo entry points (work after pip install -e .)."""

from __future__ import annotations

import asyncio
import runpy
from pathlib import Path

_EXAMPLES = Path(__file__).resolve().parents[2] / "examples"


def _run(script: str) -> None:
    path = _EXAMPLES / script
    if not path.is_file():
        raise FileNotFoundError(f"Demo script not found: {path}")
    runpy.run_path(str(path), run_name="__main__")


def run_destroyer() -> None:
    _run("demo_destroyer.py")


def run_leaker() -> None:
    _run("demo_leaker.py")


def run_undo() -> None:
    _run("demo_undo.py")


def run_quickstart() -> None:
    _run("quickstart_no_agent.py")
