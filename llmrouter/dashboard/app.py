from llmrouter.config import RouterConfig
from llmrouter.models import list_supported_models
from fastapi import FastAPI

from llmrouter.tracker import CostTracker

app = FastAPI(title="LLM Router Dashboard")


@app.get("/")
def index():
    config = RouterConfig.from_env()
    tracker = CostTracker(str(config.db_path))
    totals = tracker.totals()
    return {
        "config": config.as_dict(),
        "totals": {
            "requests": int(totals["requests"]),
            "priced_requests": int(totals["priced_requests"]),
            "unpriced_requests": int(totals["unpriced_requests"]),
            "routed_cost": totals["routed_cost"],
            "baseline_cost": totals["baseline_cost"],
            "saved_cost": totals["saved_cost"],
            "average_routed_cost": totals["average_routed_cost"],
            "average_saved_cost": totals["average_saved_cost"],
            "average_complexity_score": totals["average_complexity_score"],
        },
        "models": tracker.model_breakdown(),
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/supported-models")
def supported_models():
    return [
        {
            "name": model.name,
            "input_per_1k": model.input_per_1k,
            "output_per_1k": model.output_per_1k,
        }
        for model in list_supported_models()
    ]
