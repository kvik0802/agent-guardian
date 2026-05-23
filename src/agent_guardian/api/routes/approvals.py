from fastapi import APIRouter, HTTPException

from agent_guardian.api.models import ActionIdRequest
from agent_guardian.core.audit import get_action
from agent_guardian.core.rollback import set_approval

router = APIRouter()


@router.post("/approve")
async def approve_action(body: ActionIdRequest) -> dict[str, str]:
    await set_approval(body.action_id, "approved")
    return {"action_id": body.action_id, "decision": "approved"}


@router.post("/deny")
async def deny_action(body: ActionIdRequest) -> dict[str, str]:
    await set_approval(body.action_id, "denied")
    return {"action_id": body.action_id, "decision": "denied"}


@router.get("/pending")
async def pending_approvals() -> list[dict[str, str]]:
    from agent_guardian.core.audit import get_audit_log

    return [
        {
            "action_id": e["action_id"],
            "call_repr": e["call_repr"],
            "risk_score": str(e.get("risk_score", 0)),
        }
        for e in get_audit_log(100)
        if e.get("status") == "pending"
    ]


@router.get("/{action_id}")
async def get_action_detail(action_id: str) -> dict:
    entry = get_action(action_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Action not found")
    return entry
