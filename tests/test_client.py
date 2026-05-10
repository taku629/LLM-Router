import sys
from types import ModuleType, SimpleNamespace

from llmrouter import RouterClient
from llmrouter.config import RouterConfig
from llmrouter.tracker import CostTracker


class ExplodingTracker(CostTracker):
    def __init__(self) -> None:
        pass

    def record(self, *args, **kwargs):
        raise RuntimeError("tracking failed")


def test_router_client_does_not_fail_when_tracking_fails(monkeypatch):
    class FakeCompletions:
        def create(self, *args, **kwargs):
            return SimpleNamespace(usage=SimpleNamespace(prompt_tokens=10, completion_tokens=5))

    class FakeOpenAI:
        def __init__(self, *args, **kwargs):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    fake_openai = ModuleType("openai")
    fake_openai.OpenAI = FakeOpenAI
    monkeypatch.setitem(sys.modules, "openai", fake_openai)

    client = RouterClient(tracker=ExplodingTracker())
    response = client.chat.completions.create(messages=[{"role": "user", "content": "hello"}])

    assert response.usage.prompt_tokens == 10


def test_router_client_uses_custom_routing_threshold(monkeypatch):
    class FakeCompletions:
        def __init__(self):
            self.last_kwargs = None

        def create(self, *args, **kwargs):
            self.last_kwargs = kwargs
            return SimpleNamespace(usage=None)

    completions = FakeCompletions()

    class FakeOpenAI:
        def __init__(self, *args, **kwargs):
            self.chat = SimpleNamespace(completions=completions)

    fake_openai = ModuleType("openai")
    fake_openai.OpenAI = FakeOpenAI
    monkeypatch.setitem(sys.modules, "openai", fake_openai)

    client = RouterClient(
        tracker=ExplodingTracker(),
        routing_threshold=20,
        low_complexity_model="gpt-4.1-mini",
        high_complexity_model="gpt-4.1",
    )
    client.chat.completions.create(
        messages=[{"role": "user", "content": "Analyze and compare this architecture in detail."}]
    )

    assert completions.last_kwargs["model"] == "gpt-4.1"


def test_router_client_uses_config_defaults(monkeypatch, tmp_path):
    class FakeCompletions:
        def __init__(self):
            self.last_kwargs = None

        def create(self, *args, **kwargs):
            self.last_kwargs = kwargs
            return SimpleNamespace(usage=None)

    completions = FakeCompletions()

    class FakeOpenAI:
        def __init__(self, *args, **kwargs):
            self.chat = SimpleNamespace(completions=completions)

    fake_openai = ModuleType("openai")
    fake_openai.OpenAI = FakeOpenAI
    monkeypatch.setitem(sys.modules, "openai", fake_openai)

    client = RouterClient(
        config=RouterConfig(
            db_path=tmp_path / "usage.db",
            routing_threshold=20,
            low_complexity_model="gpt-4.1-mini",
            high_complexity_model="gpt-4.1",
            baseline_model="gpt-4.1",
        ),
        tracker=ExplodingTracker(),
    )
    client.chat.completions.create(
        messages=[{"role": "user", "content": "Analyze and compare this architecture in detail."}]
    )

    assert completions.last_kwargs["model"] == "gpt-4.1"
