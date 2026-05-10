from pathlib import Path

from llmrouter.config import RouterConfig


def test_router_config_from_env(monkeypatch, tmp_path):
    monkeypatch.setenv("LLMROUTER_DB_PATH", str(tmp_path / "usage.db"))
    monkeypatch.setenv("LLMROUTER_BASELINE_MODEL", "gpt-4.1")
    monkeypatch.setenv("LLMROUTER_ROUTING_THRESHOLD", "22")
    monkeypatch.setenv("LLMROUTER_LOW_COMPLEXITY_MODEL", "gpt-4.1-mini")
    monkeypatch.setenv("LLMROUTER_HIGH_COMPLEXITY_MODEL", "gpt-4.1")

    config = RouterConfig.from_env()

    assert config.db_path == Path(tmp_path / "usage.db")
    assert config.baseline_model == "gpt-4.1"
    assert config.routing_threshold == 22
    assert config.low_complexity_model == "gpt-4.1-mini"
    assert config.high_complexity_model == "gpt-4.1"


def test_router_config_validates_threshold(tmp_path):
    try:
        RouterConfig(db_path=tmp_path / "usage.db", routing_threshold=101)
    except ValueError as exc:
        assert "routing_threshold" in str(exc)
    else:
        raise AssertionError("expected RouterConfig to reject invalid threshold")
