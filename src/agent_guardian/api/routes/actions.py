import time

from fastapi import APIRouter

from agent_guardian import __version__
from agent_guardian.api.models import ActionRecord, ScoreRequest, ScoreResponse
from agent_guardian.core.audit import export_audit_json, get_audit_log
from agent_guardian.core.risk_scorer import score_action

router = APIRouter()


@router.get("", response_model=list[ActionRecord])
async def list_actions(limit: int = 50) -> list[ActionRecord]:
    entries = get_audit_log(limit=limit)
    return [
        ActionRecord(
            action_id=e["action_id"],
            call_repr=e["call_repr"],
            risk_score=int(e.get("risk_score", 0)),
            category=str(e.get("category", "unknown")),
            status=str(e.get("status", "unknown")),
            timestamp=str(e.get("timestamp", "")),
            explanation=str(e.get("explanation", "")),
        )
        for e in entries
    ]


@router.post("/score", response_model=ScoreResponse)
async def score_action_endpoint(body: ScoreRequest) -> ScoreResponse:
    t0 = time.monotonic()
    risk = await score_action(body.action)
    latency_ms = int((time.monotonic() - t0) * 1000)
    risk["latency_ms"] = latency_ms
    return ScoreResponse(risk=risk, latency_ms=latency_ms)


@router.get("/export")
async def export_audit() -> dict[str, str]:
    return {"audit_json": export_audit_json(), "version": __version__}


@router.get("/stats")
async def action_stats() -> dict[str, int | float]:
    entries = get_audit_log(limit=1000)
    if not entries:
        return {"total": 0, "blocked": 0, "executed": 0, "avg_risk": 0.0}
    blocked = sum(1 for e in entries if e.get("status") == "blocked")
    executed = sum(1 for e in entries if e.get("status") == "executed")
    avg_risk = sum(int(e.get("risk_score", 0)) for e in entries) / len(entries)
    return {
        "total": len(entries),
        "blocked": blocked,
        "executed": executed,
        "avg_risk": round(avg_risk, 1),
    }
