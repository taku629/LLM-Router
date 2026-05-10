import logging

from .config import RouterConfig
from .router import (
    route_messages,
)
from .tracker import CostTracker

logger = logging.getLogger(__name__)
__all__ = ["RouterClient", "RouterConfig", "CostTracker", "route_messages"]


class RouterClient:  # lazy OpenAI-compatible wrapper
    def __new__(
        cls,
        *args,
        config: RouterConfig | None = None,
        tracker: CostTracker | None = None,
        baseline_model: str | None = None,
        routing_threshold: int | None = None,
        low_complexity_model: str | None = None,
        high_complexity_model: str | None = None,
        **kwargs,
    ):
        from openai import OpenAI

        resolved_config = config or RouterConfig.from_env()
        baseline_model = baseline_model or resolved_config.baseline_model
        routing_threshold = routing_threshold if routing_threshold is not None else resolved_config.routing_threshold
        low_complexity_model = low_complexity_model or resolved_config.low_complexity_model
        high_complexity_model = high_complexity_model or resolved_config.high_complexity_model
        client = OpenAI(*args, **kwargs)
        _tracker = tracker or CostTracker(str(resolved_config.db_path))
        original_create = client.chat.completions.create

        def wrapped_create(*c_args, **c_kwargs):
            decision = None
            if "model" not in c_kwargs:
                messages = c_kwargs.get("messages", [])
                decision = route_messages(
                    messages,
                    threshold=routing_threshold,
                    low_complexity_model=low_complexity_model,
                    high_complexity_model=high_complexity_model,
                )
                c_kwargs["model"] = decision.model
            resp = original_create(*c_args, **c_kwargs)
            usage = getattr(resp, "usage", None)
            if usage:
                try:
                    _tracker.record(
                        prompt_tokens=getattr(usage, "prompt_tokens", 0),
                        completion_tokens=getattr(usage, "completion_tokens", 0),
                        routed_model=c_kwargs["model"],
                        baseline_model=baseline_model,
                        complexity_score=None if decision is None else decision.score,
                    )
                except Exception:
                    logger.exception("Failed to record usage for model %s", c_kwargs["model"])
            return resp

        client.chat.completions.create = wrapped_create
        return client
