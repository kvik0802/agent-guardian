import asyncio
from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest

from agent_guardian.core import audit


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def clear_audit() -> Generator[None, None, None]:
    audit.clear_audit_log()
    yield
    audit.clear_audit_log()


@pytest.fixture
def mock_openai() -> Generator:
    mock_response = type(
        "R",
        (),
        {
            "choices": [
                type(
                    "C",
                    (),
                    {
                        "message": type(
                            "M",
                            (),
                            {
                                "content": (
                                    '{"score":30,"category":"benign",'
                                    '"confidence":0.9,"explanation":"safe action"}'
                                )
                            },
                        )()
                    },
                )()
            ]
        },
    )()
    with patch("agent_guardian.core.risk_scorer._get_client") as get_client:
        client = AsyncMock()
        client.chat.completions.create = AsyncMock(return_value=mock_response)
        get_client.return_value = client
        yield client


@pytest.fixture
def mock_redis() -> Generator:
    with (
        patch("agent_guardian.core.rollback._redis_set", new_callable=AsyncMock) as mock_set,
        patch("agent_guardian.core.rollback._redis_get", new_callable=AsyncMock) as mock_get,
    ):
        mock_get.return_value = None
        yield mock_set
