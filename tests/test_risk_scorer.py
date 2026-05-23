import pytest

from agent_guardian.core.risk_scorer import score_action
from agent_guardian.core.rule_engine import check_rules


@pytest.mark.asyncio
async def test_score_benign_action(mock_openai: object) -> None:
    result = await score_action("list_files(path='/tmp')")
    assert "score" in result
    assert 0 <= result["score"] <= 100
    assert "category" in result
    assert "explanation" in result


@pytest.mark.asyncio
async def test_score_returns_dict(mock_openai: object) -> None:
    result = await score_action("delete_file(path='/home/user/data.csv')")
    assert isinstance(result, dict)
    assert isinstance(result["score"], (int, float))


@pytest.mark.asyncio
async def test_score_has_confidence(mock_openai: object) -> None:
    result = await score_action("send_email(to='all@company.com')")
    assert "confidence" in result
    assert 0.0 <= result["confidence"] <= 1.0


def test_rule_engine_rm_rf() -> None:
    hit = check_rules("rm -rf /home/user/projects")
    assert hit is not None
    assert hit["score"] >= 95
    assert hit["category"] == "file_deletion"


def test_rule_engine_benign() -> None:
    assert check_rules("read_config()") is None
