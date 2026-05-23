from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from agent_guardian.api.main import app


@pytest.mark.asyncio
async def test_health() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert len(data["pillars"]) == 5


@pytest.mark.asyncio
async def test_score_endpoint() -> None:
    with patch("agent_guardian.api.routes.actions.score_action", new_callable=AsyncMock) as mock:
        mock.return_value = {
            "score": 42,
            "category": "network",
            "confidence": 0.8,
            "explanation": "test",
        }
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/actions/score", json={"action": "read_local_config()"})
            assert resp.status_code == 200
            assert resp.json()["risk"]["score"] == 42
