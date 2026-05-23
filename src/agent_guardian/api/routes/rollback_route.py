from fastapi import APIRouter, HTTPException

from agent_guardian.api.models import RollbackRequest
from agent_guardian.core.audit import get_action, log_action
from agent_guardian.core.rollback import cascade_rollback, rollback

router = APIRouter()


@router.post("/{action_id}")
async def rollback_action(action_id: str) -> dict[str, str | bool]:
    entry = get_action(action_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Action not found")

    snap_id = (entry.get("snapshot_id") or entry.get("extra", {}) or {}).get("snapshot_id")
    if isinstance(entry.get("extra"), dict):
        snap_id = entry["extra"].get("snapshot_id", snap_id)

    if not snap_id:
        raise HTTPException(status_code=400, detail="No snapshot for this action")

    success = await rollback(str(snap_id))
    await log_action(
        action_id,
        entry.get("call_repr", ""),
        entry.get("risk", {}),
        status="rolled_back" if success else "rollback_failed",
    )
    return {"action_id": action_id, "snapshot_id": str(snap_id), "success": success}


@router.post("")
async def rollback_by_snapshot(body: RollbackRequest) -> dict[str, bool]:
    success = await rollback(body.snapshot_id)
    return {"snapshot_id": body.snapshot_id, "success": success}


@router.post("/cascade")
async def cascade(snapshot_ids: list[str]) -> dict[str, bool]:
    results = await cascade_rollback(snapshot_ids)
    return results
