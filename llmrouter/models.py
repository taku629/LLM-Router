import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelPricing:
    name: str
    input_per_1k: float
    output_per_1k: float


def _env_float(key: str, default: float) -> float:
    val = os.environ.get(key)
    if val is None:
        return default
    try:
        return float(val)
    except ValueError:
        return default


OPENAI_LOW = ModelPricing(
    "gpt-4o-mini",
    _env_float("LLMROUTER_MINI_INPUT_PER_1K", 0.00015),
    _env_float("LLMROUTER_MINI_OUTPUT_PER_1K", 0.0006),
)
OPENAI_HIGH = ModelPricing(
    "gpt-4o",
    _env_float("LLMROUTER_HIGH_INPUT_PER_1K", 0.005),
    _env_float("LLMROUTER_HIGH_OUTPUT_PER_1K", 0.015),
)

MODEL_TABLE = {
    OPENAI_LOW.name: OPENAI_LOW,
    OPENAI_HIGH.name: OPENAI_HIGH,
}
