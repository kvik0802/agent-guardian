"""Hardcoded blocks for obvious catastrophic patterns (<1ms)."""

import re
from typing import Any

CRITICAL_PATTERNS: list[tuple[re.Pattern[str], str, int]] = [
    (re.compile(r"rm\s+-rf\s+[/~]", re.I), "file_deletion", 98),
    (re.compile(r"shutil\.rmtree\s*\(", re.I), "file_deletion", 98),
    (re.compile(r"curl\s+.*\|\s*bash", re.I), "shell", 97),
    (re.compile(r"wget\s+.*\|\s*sh", re.I), "shell", 97),
    (re.compile(r"DROP\s+TABLE", re.I), "database", 96),
    (re.compile(r"eval\s*\(", re.I), "shell", 90),
    (re.compile(r"os\.system\s*\(", re.I), "shell", 88),
    (re.compile(r"subprocess\.call.*shell\s*=\s*True", re.I), "shell", 92),
]

HIGH_PATTERNS: list[tuple[re.Pattern[str], str, int]] = [
    (re.compile(r"password|api[_-]?key|secret|token", re.I), "credential", 75),
    (re.compile(r"post.*user.*data|exfil|external_api", re.I), "pii", 82),
    (re.compile(r"send.*email|bulk_email|smtp", re.I), "email", 72),
    (re.compile(r"transfer.*\$|wire.*fund|stripe\.charges", re.I), "financial", 85),
]


def check_rules(action_repr: str) -> dict[str, Any] | None:
    """Return a risk dict if a rule matches, else None."""
    for pattern, category, score in CRITICAL_PATTERNS + HIGH_PATTERNS:
        if pattern.search(action_repr):
            return {
                "score": score,
                "category": category,
                "confidence": 0.99,
                "explanation": f"Rule engine matched pattern: {pattern.pattern}",
                "source": "rule_engine",
            }
    return None
