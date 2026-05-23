from agent_guardian.core.policy import should_block


def test_rule_engine_blocks() -> None:
    risk = {
        "score": 98,
        "category": "file_deletion",
        "source": "rule_engine",
    }
    assert should_block(risk) is True


def test_offline_delete_heuristic_blocks() -> None:
    risk = {"score": 96, "category": "file_deletion", "source": "fallback"}
    assert should_block(risk) is True


def test_benign_not_blocked() -> None:
    risk = {"score": 20, "category": "benign", "source": "openai"}
    assert should_block(risk) is False
