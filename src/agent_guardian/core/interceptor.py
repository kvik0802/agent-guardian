"""@guardian.watch decorator — intercept, score, simulate, approve, execute."""

from __future__ import annotations

import asyncio
import functools
import time
import uuid
from collections.abc import Callable
from typing import Any

from agent_guardian.core.approver import request_approval
from agent_guardian.core.audit import log_action
from agent_guardian.core.policy import requires_approval, requires_simulation, should_block
from agent_guardian.core.risk_scorer import score_action
from agent_guardian.core.rollback import snapshot_state
from agent_guardian.core.simulator import simulate_action

_last_snapshots: dict[str, str] = {}


def get_last_snapshot(action_id: str) -> str | None:
    return _last_snapshots.get(action_id)


class GuardianDecorator:
    """Wraps any callable tool; intercepts before execution."""

    def watch(self, func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            action_id = str(uuid.uuid4())[:8]
            call_repr = f"{func.__name__}(args={args!r}, kwargs={kwargs!r})"
            t0 = time.monotonic()

            risk = await score_action(call_repr)
            latency_ms = int((time.monotonic() - t0) * 1000)
            risk["latency_ms"] = latency_ms

            await log_action(action_id, call_repr, risk, status="pending")

            if should_block(risk):
                await log_action(action_id, call_repr, risk, status="blocked")
                raise PermissionError(f"[Guardian] BLOCKED critical action: {call_repr}")

            if requires_simulation(risk):
                sim = await simulate_action(func, args, kwargs)
                risk["simulation"] = sim

            snap_id: str | None = None
            if requires_approval(risk):
                snap_id = await snapshot_state()
                _last_snapshots[action_id] = snap_id
                approved = await request_approval(action_id, call_repr, risk)
                if not approved:
                    await log_action(
                        action_id,
                        call_repr,
                        risk,
                        status="denied",
                        extra={"snapshot_id": snap_id},
                    )
                    raise PermissionError(f"[Guardian] DENIED by human: {call_repr}")

            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            await log_action(
                action_id,
                call_repr,
                risk,
                status="executed",
                extra={"snapshot_id": snap_id, "result_preview": str(result)[:200]},
            )
            return result

        return wrapper


guardian = GuardianDecorator()
watch = guardian.watch
