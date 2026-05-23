"""Structured audit log — in-memory store with optional persistence hook."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

_audit_log: list[dict[str, Any]] = []


async def log_action(
    action_id: str,
    call_repr: str,
    risk: dict[str, Any],
    status: str = "pending",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Append an audit entry and return it."""
    entry: dict[str, Any] = {
        "action_id": action_id,
        "call_repr": call_repr,
        "risk_score": risk.get("score", 0),
        "category": risk.get("category", "unknown"),
        "confidence": risk.get("confidence", 0.0),
        "explanation": risk.get("explanation", ""),
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "risk": risk,
    }
    if extra:
        entry.update(extra)
    _audit_log.append(entry)
    return entry


def get_audit_log(limit: int = 100) -> list[dict[str, Any]]:
    """Return recent audit entries (newest first)."""
    return list(reversed(_audit_log[-limit:]))


def get_action(action_id: str) -> dict[str, Any] | None:
    """Find a single action by ID."""
    for entry in reversed(_audit_log):
        if entry["action_id"] == action_id:
            return entry
    return None


def clear_audit_log() -> None:
    """Reset audit log (for tests)."""
    _audit_log.clear()


def export_audit_json() -> str:
    """Export full audit trail as JSON."""
    return json.dumps(_audit_log, indent=2, default=str)
