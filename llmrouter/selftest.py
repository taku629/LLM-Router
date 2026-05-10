import logging
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from types import ModuleType, SimpleNamespace

from . import RouterClient
from .config import RouterConfig
from .router import complexity_score, pick_model
from .tracker import CostTracker


class _ExplodingTracker(CostTracker):
    def __init__(self) -> None:
        pass

    def record(self, *args, **kwargs):
        raise RuntimeError("tracking failed")


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_selftest() -> None:
    config = RouterConfig.from_env()
    _assert(config.routing_threshold >= 0, "config did not load")

    structured_messages = [
        {
            "role": "user",
            "content": [{"type": "text", "text": "Analyze and compare this architecture in detail."}],
        }
    ]
    structured_score = complexity_score(structured_messages)
    _assert(structured_score > 0, "structured content did not affect complexity score")
    _assert(
        pick_model(24, threshold=20, low_complexity_model="gpt-4.1-mini", high_complexity_model="gpt-4.1")
        == "gpt-4.1",
        "custom routing threshold did not choose the expected model",
    )

    with TemporaryDirectory() as temp_dir:
        tracker = CostTracker(str(Path(temp_dir) / "usage.db"))
        _assert(tracker.record(1000, 1000, "gpt-4.1-mini") is True, "priced model was not tracked")
        _assert(tracker.record(1000, 1000, "custom-deployment") is False, "unpriced model should return False")
        totals = tracker.totals()
        _assert(totals["priced_requests"] == 1, "priced request count is wrong")
        _assert(totals["unpriced_requests"] == 1, "unpriced request count is wrong")
        _assert(totals["average_complexity_score"] == 0, "empty complexity score average should be zero")
        _assert(len(tracker.model_breakdown()) == 2, "model breakdown should include both priced and unpriced models")

    fake_openai = ModuleType("openai")

    class FakeCompletions:
        def create(self, *args, **kwargs):
            return SimpleNamespace(usage=SimpleNamespace(prompt_tokens=10, completion_tokens=5))

    class FakeOpenAI:
        def __init__(self, *args, **kwargs):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    fake_openai.OpenAI = FakeOpenAI
    original_openai = sys.modules.get("openai")
    package_logger = logging.getLogger("llmrouter")
    original_disabled = package_logger.disabled
    sys.modules["openai"] = fake_openai
    try:
        package_logger.disabled = True
        client = RouterClient(tracker=_ExplodingTracker())
        response = client.chat.completions.create(messages=[{"role": "user", "content": "hello"}])
        _assert(response.usage.prompt_tokens == 10, "tracking failure should not break successful completions")
    finally:
        package_logger.disabled = original_disabled
        if original_openai is None:
            del sys.modules["openai"]
        else:
            sys.modules["openai"] = original_openai

    print("selftest: ok")


if __name__ == "__main__":
    run_selftest()
