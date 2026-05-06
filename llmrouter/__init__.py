from .router import complexity_score, pick_model
from .tracker import CostTracker


def RouterClient(tracker: CostTracker | None = None, baseline_model: str = "gpt-4o", **kwargs):
    from openai import OpenAI

    client = OpenAI(**kwargs)
    _tracker = tracker or CostTracker()
    original_create = client.chat.completions.create

    def wrapped_create(*args, **kw):
        if "model" not in kw:
            messages = kw.get("messages", [])
            score = complexity_score(messages)
            kw["model"] = pick_model(score)
        resp = original_create(*args, **kw)
        usage = getattr(resp, "usage", None)
        if usage:
            _tracker.record(
                prompt_tokens=getattr(usage, "prompt_tokens", 0),
                completion_tokens=getattr(usage, "completion_tokens", 0),
                routed_model=kw["model"],
                baseline_model=baseline_model,
            )
        return resp

    client.chat.completions.create = wrapped_create
    return client
