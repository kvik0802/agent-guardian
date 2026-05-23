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
    """Seed sample audit entries so the dashboard has data on first run."""
    if not get_audit_log():
        await log_action(
            "sample01",
            "list_files(folder='/tmp')",
            {"score": 12, "category": "benign", "confidence": 0.9, "explanation": "Read-only listing"},
            status="executed",
        )
        await log_action(
            "sample02",
            "run_shell_command(cmd='rm -rf /data')",
            {"score": 98, "category": "file_deletion", "confidence": 0.99, "explanation": "Destructive shell command"},
            status="blocked",
        )
        await log_action(
            "sample03",
            "send_email(to='team@company.com', subject='Report')",
            {"score": 45, "category": "email", "confidence": 0.8, "explanation": "Single outbound email"},
            status="executed",
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
