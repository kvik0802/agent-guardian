"""Scenario 3: The Undo — bulk email with rollback (uses safe mock send)."""

import asyncio
import os

# Allow execution in this demo only (still snapshots + rollback)
os.environ["GUARDIAN_AUTO_APPROVE"] = "true"

from agent_guardian import watch
from agent_guardian.config import settings

settings.GUARDIAN_AUTO_APPROVE = True
from agent_guardian.core.audit import get_audit_log
from agent_guardian.core.rollback import rollback


@watch
async def send_bulk_email(to_list: list[str], subject: str, body: str) -> dict[str, int | str]:
    return {"sent": len(to_list), "subject": subject}


async def main() -> None:
    print("Running Undo scenario...")
    try:
        result = await send_bulk_email(
            to_list=[f"contact{i}@company.com" for i in range(5)],
            subject="WRONG: Internal pricing doc",
            body="This email was sent by mistake.",
        )
        print(f"Sent: {result}")
    except PermissionError as exc:
        print(f"[Guardian] Denied (expected in strict mode): {exc}")

    entries = get_audit_log(limit=5)
    for e in entries:
        extra = e.get("extra") or {}
        snap = extra.get("snapshot_id")
        if snap:
            ok = await rollback(str(snap))
            print(f"[Guardian] Rollback {snap}: {'OK' if ok else 'FAILED'}")
            break


if __name__ == "__main__":
    asyncio.run(main())
