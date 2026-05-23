import json
import logging
from typing import Any

from openai import AsyncOpenAI

from agent_guardian.config import settings
from agent_guardian.core.rule_engine import check_rules

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a security risk analyser for AI agent actions.
Return ONLY valid JSON — no prose, no markdown fences.
Schema: {"score": 0-100, "category": "<category>",
"confidence": 0.0-1.0, "explanation": "<one sentence>"}
Categories: file_deletion | financial | pii | credential |
shell | network | email | database | benign
score 0=safe, 100=catastrophic."""

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY or "sk-test")
    return _client


def _fallback_score(action_repr: str) -> dict[str, Any]:
    """Offline-safe scoring when OpenAI is unavailable."""
    rule = check_rules(action_repr)
    if rule:
        return rule
    lowered = action_repr.lower()
    if any(w in lowered for w in ("delete", "rmtree", "rm -rf")):
        return {
            "score": 96,
            "category": "file_deletion",
            "confidence": 0.85,
            "explanation": "Destructive file operation detected (offline heuristic).",
            "source": "fallback",
        }
    if any(w in lowered for w in ("post", "http", "exfil", "upload")):
        return {
            "score": 75,
            "category": "network",
            "confidence": 0.8,
            "explanation": "Network data transfer detected (offline heuristic).",
            "source": "fallback",
        }
    return {
        "score": 15,
        "category": "benign",
        "confidence": 0.7,
        "explanation": "No obvious risk patterns (offline heuristic).",
        "source": "fallback",
    }


async def score_action(action_repr: str) -> dict[str, Any]:
    """Score an action string; returns risk dict with score 0-100."""
    rule_hit = check_rules(action_repr)
    if rule_hit:
        return rule_hit

    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.startswith("sk-YOUR"):
        return _fallback_score(action_repr)

    try:
        client = _get_client()
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Action: {action_repr}"},
            ],
            max_tokens=120,
        )
        content = resp.choices[0].message.content or "{}"
        result: dict[str, Any] = json.loads(content)
        result["source"] = "openai"
        return result
    except Exception as exc:
        logger.warning("OpenAI scoring failed, using fallback: %s", exc)
        return _fallback_score(action_repr)
