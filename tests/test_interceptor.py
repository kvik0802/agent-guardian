from unittest.mock import AsyncMock, patch

import pytest

from agent_guardian.core.interceptor import guardian


@pytest.mark.asyncio
async def test_watch_executes_safe_action(mock_openai: object, mock_redis: object) -> None:
    with patch("agent_guardian.core.interceptor.score_action", new_callable=AsyncMock) as mock_score:
        mock_score.return_value = {
            "score": 20,
            "category": "benign",
            "confidence": 0.9,
            "explanation": "safe",
        }

        @guardian.watch
        async def safe_tool(x: int) -> int:
            return x * 2

        result = await safe_tool(5)
        assert result == 10


@pytest.mark.asyncio
async def test_watch_blocks_critical_action(mock_redis: object) -> None:
    with patch("agent_guardian.core.interceptor.score_action", new_callable=AsyncMock) as mock_score:
        mock_score.return_value = {
            "score": 97,
            "category": "file_deletion",
            "confidence": 0.99,
            "explanation": "deletes all files",
        }
        from agent_guardian.config import settings

        original = settings.ALLOW_CRITICAL
        settings.ALLOW_CRITICAL = False
        try:

            @guardian.watch
            async def dangerous_tool() -> None:
                pass

            with pytest.raises(PermissionError, match="BLOCKED"):
                await dangerous_tool()
        finally:
            settings.ALLOW_CRITICAL = original
