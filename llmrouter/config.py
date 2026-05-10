import os
from dataclasses import dataclass, field
from pathlib import Path

from .router import (
    DEFAULT_COMPLEXITY_THRESHOLD,
    DEFAULT_HIGH_COMPLEXITY_MODEL,
    DEFAULT_LOW_COMPLEXITY_MODEL,
)


def default_db_path() -> Path:
    env_path = os.getenv("LLMROUTER_DB_PATH")
    if env_path:
        return Path(env_path)

    home_candidate = Path.home() / ".llmrouter" / "usage.db"
    try:
        home_candidate.parent.mkdir(parents=True, exist_ok=True)
        return home_candidate
    except OSError:
        fallback = Path.cwd() / ".llmrouter" / "usage.db"
        fallback.parent.mkdir(parents=True, exist_ok=True)
        return fallback


@dataclass(frozen=True)
class RouterConfig:
    db_path: Path = field(default_factory=default_db_path)
    baseline_model: str = DEFAULT_HIGH_COMPLEXITY_MODEL
    routing_threshold: int = DEFAULT_COMPLEXITY_THRESHOLD
    low_complexity_model: str = DEFAULT_LOW_COMPLEXITY_MODEL
    high_complexity_model: str = DEFAULT_HIGH_COMPLEXITY_MODEL

    def __post_init__(self) -> None:
        if not 0 <= self.routing_threshold <= 100:
            raise ValueError("routing_threshold must be between 0 and 100")
        if not self.low_complexity_model:
            raise ValueError("low_complexity_model must not be empty")
        if not self.high_complexity_model:
            raise ValueError("high_complexity_model must not be empty")
        if not self.baseline_model:
            raise ValueError("baseline_model must not be empty")

    @classmethod
    def from_env(cls) -> "RouterConfig":
        threshold = os.getenv("LLMROUTER_ROUTING_THRESHOLD")
        return cls(
            db_path=default_db_path(),
            baseline_model=os.getenv("LLMROUTER_BASELINE_MODEL", DEFAULT_HIGH_COMPLEXITY_MODEL),
            routing_threshold=int(threshold) if threshold is not None else DEFAULT_COMPLEXITY_THRESHOLD,
            low_complexity_model=os.getenv("LLMROUTER_LOW_COMPLEXITY_MODEL", DEFAULT_LOW_COMPLEXITY_MODEL),
            high_complexity_model=os.getenv("LLMROUTER_HIGH_COMPLEXITY_MODEL", DEFAULT_HIGH_COMPLEXITY_MODEL),
        )

    def as_dict(self) -> dict[str, str | int]:
        return {
            "db_path": str(self.db_path),
            "baseline_model": self.baseline_model,
            "routing_threshold": self.routing_threshold,
            "low_complexity_model": self.low_complexity_model,
            "high_complexity_model": self.high_complexity_model,
        }
