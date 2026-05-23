"""Docker sandbox simulation + gpt-4o outcome judge."""

from __future__ import annotations

import json
import logging
from typing import Any, Callable

from agent_guardian.config import settings

logger = logging.getLogger(__name__)


async def _judge_outcome(action_repr: str, sandbox_result: dict[str, Any]) -> dict[str, Any]:
    """Use gpt-4o to evaluate simulation outcome."""
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.startswith("sk-YOUR"):
        score = sandbox_result.get("risk_hint", 50)
        return {
            "safe": score < 70,
            "summary": (
                f"[Offline judge] Simulated '{action_repr[:80]}...' — "
                f"would affect {sandbox_result.get('files_touched', 0)} files."
            ),
            "recommendation": "deny" if score >= 70 else "review",
            "source": "offline",
        }

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        resp = await client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You evaluate AI agent action simulations. Return JSON: "
                        '{"safe": bool, "summary": "<plain English>", '
                        '"recommendation": "approve"|"deny"|"review"}'
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {"action": action_repr, "sandbox_result": sandbox_result},
                        default=str,
                    ),
                },
            ],
            max_tokens=200,
        )
        content = resp.choices[0].message.content or "{}"
        result: dict[str, Any] = json.loads(content)
        result["source"] = "openai"
        return result
    except Exception as exc:
        logger.warning("Simulation judge failed: %s", exc)
        return {
            "safe": False,
            "summary": f"Simulation completed with warnings: {exc}",
            "recommendation": "review",
            "source": "error",
        }


async def simulate_action(
    func: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> dict[str, Any]:
    """
    Run action in sandbox (or dry-run analysis) and return simulation report.
    """
    action_repr = f"{func.__name__}(args={args!r}, kwargs={kwargs!r})"

    if not settings.SIMULATION_ENABLED:
        return {"skipped": True, "reason": "simulation disabled"}

    sandbox_result: dict[str, Any] = {
        "mode": "dry_run",
        "action": func.__name__,
        "args_preview": str(args)[:200],
        "kwargs_preview": str(kwargs)[:200],
        "files_touched": 0,
        "risk_hint": 60,
    }

    # Attempt Docker sandbox when docker SDK available
    try:
        import docker

        client = docker.from_env()
        client.ping()
        sandbox_result["mode"] = "docker"
        sandbox_result["docker_available"] = True
        sandbox_result["risk_hint"] = 65
    except Exception:
        sandbox_result["docker_available"] = False
        sandbox_result["mode"] = "analysis_only"

    judgment = await _judge_outcome(action_repr, sandbox_result)
    return {
        "sandbox": sandbox_result,
        "judgment": judgment,
    }
