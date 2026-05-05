from .router import complexity_score, pick_model
from .tracker import CostTracker


class RouterClient:  # lazy OpenAI-compatible wrapper
    def __new__(cls, *args, tracker: CostTracker | None = None, baseline_model: str = "gpt-4o", **kwargs):
        from openai import OpenAI

        client = OpenAI(*args, **kwargs)
        _tracker = tracker or CostTracker()
        original_create = client.chat.completions.create

        def wrapped_create(*c_args, **c_kwargs):
            if "model" not in c_kwargs:
                messages = c_kwargs.get("messages", [])
                score = complexity_score(messages)
                c_kwargs["model"] = pick_model(score)
            resp = original_create(*c_args, **c_kwargs)
            usage = getattr(resp, "usage", None)
            if usage:
                _tracker.record(
                    prompt_tokens=getattr(usage, "prompt_tokens", 0),
                    completion_tokens=getattr(usage, "completion_tokens", 0),
                    routed_model=c_kwargs["model"],
                    baseline_model=baseline_model,
                )
            return resp

        client.chat.completions.create = wrapped_create
        return client
