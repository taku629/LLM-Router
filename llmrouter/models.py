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


OPENAI_4O_MINI = ModelPricing(
    "gpt-4o-mini",
    _env_float("LLMROUTER_MINI_INPUT_PER_1K", 0.00015),
    _env_float("LLMROUTER_MINI_OUTPUT_PER_1K", 0.0006),
)
OPENAI_4O = ModelPricing(
    "gpt-4o",
    _env_float("LLMROUTER_HIGH_INPUT_PER_1K", 0.005),
    _env_float("LLMROUTER_HIGH_OUTPUT_PER_1K", 0.015),
)
OPENAI_41_NANO = ModelPricing("gpt-4.1-nano", 0.0001, 0.0004)
OPENAI_41_MINI = ModelPricing("gpt-4.1-mini", 0.0004, 0.0016)
OPENAI_41 = ModelPricing("gpt-4.1", 0.002, 0.008)

MODEL_TABLE = {
    OPENAI_4O_MINI.name: OPENAI_4O_MINI,
    OPENAI_4O.name: OPENAI_4O,
    OPENAI_41_NANO.name: OPENAI_41_NANO,
    OPENAI_41_MINI.name: OPENAI_41_MINI,
    OPENAI_41.name: OPENAI_41,
}


def get_model_pricing(model: str) -> ModelPricing | None:
    return MODEL_TABLE.get(model)


def list_supported_models() -> list[ModelPricing]:
    return list(MODEL_TABLE.values())
