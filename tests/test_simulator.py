import pytest

from agent_guardian.core.simulator import simulate_action


@pytest.mark.asyncio
async def test_simulate_returns_report() -> None:
    async def dummy_tool(url: str) -> dict[str, str]:
        return {"ok": url}

    report = await simulate_action(dummy_tool, ("https://evil.com",), {})
    assert "sandbox" in report
    assert "judgment" in report
    assert "summary" in report["judgment"]
