"""Slack Approve/Deny with dev-mode console fallback."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from agent_guardian.config import settings
from agent_guardian.core.rollback import get_approval, set_approval

logger = logging.getLogger(__name__)

_slack_app = None


def _slack_configured() -> bool:
    return bool(settings.SLACK_BOT_TOKEN and settings.SLACK_CHANNEL_ID)


async def _notify_slack(action_id: str, call_repr: str, risk: dict[str, Any]) -> None:
    from slack_sdk.web.async_client import AsyncWebClient

    score = risk.get("score", 0)
    category = risk.get("category", "?")
    explanation = risk.get("explanation", "")
    sim = risk.get("simulation", {})
    sim_summary = ""
    if sim and "judgment" in sim:
        sim_summary = f"\n_Simulation:_ {sim['judgment'].get('summary', 'N/A')}"

    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*:shield: Agent Guardian — Approval Required*\n"
                    f"Action ID: `{action_id}`\n"
                    f"Risk: *{score}/100* · Category: `{category}`\n"
                    f"> {explanation}{sim_summary}"
                ),
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Approve"},
                    "style": "primary",
                    "value": action_id,
                    "action_id": f"approve_{action_id}",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Deny"},
                    "style": "danger",
                    "value": action_id,
                    "action_id": f"deny_{action_id}",
                },
            ],
        },
    ]

    client = AsyncWebClient(token=settings.SLACK_BOT_TOKEN)
    await client.chat_postMessage(channel=settings.SLACK_CHANNEL_ID, blocks=blocks)


async def _dev_mode_approve(action_id: str, call_repr: str, risk: dict[str, Any]) -> bool:
    """Dev mode without Slack: deny by default; opt-in approve via GUARDIAN_AUTO_APPROVE."""
    score = risk.get("score", 0)
    auto = settings.GUARDIAN_AUTO_APPROVE
    decision = "approved" if auto else "denied"
    print("\n" + "=" * 60)
    print("AGENT GUARDIAN — APPROVAL REQUIRED")
    print(f"  Action ID : {action_id}")
    print(f"  Call      : {call_repr[:120]}")
    print(f"  Risk      : {score}/100 ({risk.get('category', '?')})")
    print(f"  Reason    : {risk.get('explanation', '')}")
    if risk.get("simulation"):
        j = risk["simulation"].get("judgment", {})
        print(f"  Simulation: {j.get('summary', 'N/A')}")
    print(
        f"  [Dev mode] Default: {decision.upper()} "
        f"(set GUARDIAN_AUTO_APPROVE=true to allow execution)"
    )
    print("=" * 60 + "\n")
    await set_approval(action_id, decision)
    return auto


async def request_approval(action_id: str, call_repr: str, risk: dict[str, Any]) -> bool:
    """Send approval request; poll for decision. Returns True if approved."""
    if _slack_configured():
        try:
            await _notify_slack(action_id, call_repr, risk)
        except Exception as exc:
            logger.warning("Slack notify failed: %s", exc)

    if settings.GUARDIAN_DEV_MODE and not _slack_configured():
        return await _dev_mode_approve(action_id, call_repr, risk)

    if _slack_configured():
        for _ in range(settings.APPROVAL_TIMEOUT):
            decision = await get_approval(action_id)
            if decision == "approved":
                return True
            if decision == "denied":
                return False
            await asyncio.sleep(1)
        return False

    return await _dev_mode_approve(action_id, call_repr, risk)
