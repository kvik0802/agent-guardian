"""Central security policy — single source of truth for block/approve decisions."""

from __future__ import annotations

from typing import Any

from agent_guardian.config import settings

CRITICAL_CATEGORIES = frozenset({"file_deletion", "shell", "database"})


def should_block(risk: dict[str, Any]) -> bool:
    """Return True if the action must not execute."""
    if settings.ALLOW_CRITICAL:
        return False

    score = int(risk.get("score", 0))
    category = str(risk.get("category", ""))
    source = str(risk.get("source", ""))

    if score >= 95:
        return True
    if source == "rule_engine" and score >= 80:
        return True
    if category in CRITICAL_CATEGORIES and score >= 85:
        return True
    return False


def requires_approval(risk: dict[str, Any]) -> bool:
    return int(risk.get("score", 0)) >= 70


def requires_simulation(risk: dict[str, Any]) -> bool:
    return int(risk.get("score", 0)) >= 50
