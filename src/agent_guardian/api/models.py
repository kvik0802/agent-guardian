from typing import Any

from pydantic import BaseModel, Field


class RiskModel(BaseModel):
    score: int = Field(ge=0, le=100)
    category: str
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str
    source: str | None = None


class ActionRecord(BaseModel):
    action_id: str
    call_repr: str
    risk_score: int
    category: str
    status: str
    timestamp: str
    explanation: str = ""


class ScoreRequest(BaseModel):
    action: str


class ScoreResponse(BaseModel):
    risk: dict[str, Any]
    latency_ms: int | None = None


class ActionIdRequest(BaseModel):
    action_id: str


class RollbackRequest(BaseModel):
    snapshot_id: str


class HealthResponse(BaseModel):
    status: str
    version: str
    pillars: list[str]
