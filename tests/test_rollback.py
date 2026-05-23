from unittest.mock import AsyncMock, patch

import pytest

from agent_guardian.core.rollback import rollback, snapshot_state


@pytest.mark.asyncio
async def test_snapshot_returns_id(mock_redis: object) -> None:
    snap_id = await snapshot_state(base_dir=".")
    assert snap_id is not None
    assert len(snap_id) > 8


@pytest.mark.asyncio
async def test_rollback_returns_false_on_missing_snapshot() -> None:
    with patch("agent_guardian.core.rollback._redis_get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        result = await rollback("nonexistent_id")
        assert result is False
