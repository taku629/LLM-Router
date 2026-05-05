from llmrouter.tracker import CostTracker


def test_tracker_records_and_aggregates(tmp_path):
    db = tmp_path / "u.db"
    t = CostTracker(str(db))
    t.record(prompt_tokens=1000, completion_tokens=1000, routed_model="gpt-4o-mini")
    totals = t.totals()
    assert totals["requests"] == 1
    assert totals["saved_cost"] > 0
