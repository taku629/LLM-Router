from dataclasses import dataclass


@dataclass(frozen=True)
class ModelPricing:
    name: str
    input_per_1k: float
    output_per_1k: float


OPENAI_LOW = ModelPricing("gpt-4o-mini", 0.00015, 0.0006)
OPENAI_HIGH = ModelPricing("gpt-4o", 0.005, 0.015)

MODEL_TABLE = {
    OPENAI_LOW.name: OPENAI_LOW,
    OPENAI_HIGH.name: OPENAI_HIGH,
}
