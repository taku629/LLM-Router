from fastapi import FastAPI

from llmrouter.tracker import CostTracker

app = FastAPI(title="LLM Router Dashboard")


@app.get("/")
def index():
    totals = CostTracker().totals()
    return {
        "requests": int(totals["requests"]),
        "routed_cost": totals["routed_cost"],
        "baseline_cost": totals["baseline_cost"],
        "saved_cost": totals["saved_cost"],
    }
