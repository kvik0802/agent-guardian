from unittest.mock import AsyncMock, patch

import pytest

from agent_guardian.core.approver import request_approval


@pytest.mark.asyncio
async def test_dev_mode_denies_by_default() -> None:
    from agent_guardian.config import settings

    settings.SLACK_BOT_TOKEN = ""
    settings.SLACK_CHANNEL_ID = ""
    settings.GUARDIAN_DEV_MODE = True
    settings.GUARDIAN_AUTO_APPROVE = False
    risk = {"score": 75, "category": "email", "explanation": "bulk send"}
    approved = await request_approval("abc12345", "send_email()", risk)
    assert approved is False


@pytest.mark.asyncio
async def test_dev_mode_auto_approve_when_enabled() -> None:
    from agent_guardian.config import settings

    settings.SLACK_BOT_TOKEN = ""
    settings.SLACK_CHANNEL_ID = ""
    settings.GUARDIAN_DEV_MODE = True
    settings.GUARDIAN_AUTO_APPROVE = True
    risk = {"score": 75, "category": "email", "explanation": "bulk send"}
    approved = await request_approval("abc12345", "send_email()", risk)
    assert approved is True
