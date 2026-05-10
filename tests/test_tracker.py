from llmrouter.tracker import CostTracker


def test_tracker_records_and_aggregates(tmp_path):
    db = tmp_path / "u.db"
    t = CostTracker(str(db))
    t.record(prompt_tokens=1000, completion_tokens=1000, routed_model="gpt-4o-mini", complexity_score=12)
    totals = t.totals()
    assert totals["requests"] == 1
    assert totals["saved_cost"] > 0
    assert totals["average_complexity_score"] == 12


def test_tracker_records_unknown_models_without_crashing(tmp_path):
    db = tmp_path / "u.db"
    t = CostTracker(str(db))
    recorded_with_pricing = t.record(prompt_tokens=1000, completion_tokens=1000, routed_model="gpt-4.1-mini")
    totals = t.totals()
    assert recorded_with_pricing is True
    assert totals["requests"] == 1
    assert totals["priced_requests"] == 1
    assert totals["unpriced_requests"] == 0
    assert totals["routed_cost"] == 0.002
    assert totals["saved_cost"] > 0


def test_tracker_tracks_unpriced_requests_separately(tmp_path):
    db = tmp_path / "u.db"
    t = CostTracker(str(db))
    recorded_with_pricing = t.record(prompt_tokens=1000, completion_tokens=1000, routed_model="custom-deployment")
    totals = t.totals()
    assert recorded_with_pricing is False
    assert totals["requests"] == 1
    assert totals["priced_requests"] == 0
    assert totals["unpriced_requests"] == 1
    assert totals["routed_cost"] == 0
    assert totals["saved_cost"] == 0


def test_tracker_model_breakdown_groups_requests(tmp_path):
    db = tmp_path / "u.db"
    t = CostTracker(str(db))
    t.record(prompt_tokens=1000, completion_tokens=1000, routed_model="gpt-4o-mini", complexity_score=10)
    t.record(prompt_tokens=1000, completion_tokens=1000, routed_model="gpt-4o-mini", complexity_score=20)
    t.record(prompt_tokens=1000, completion_tokens=1000, routed_model="custom-deployment")
    breakdown = t.model_breakdown()
    assert breakdown[0]["routed_model"] == "gpt-4o-mini"
    assert breakdown[0]["requests"] == 2
    assert breakdown[0]["average_complexity_score"] == 15
    assert breakdown[1]["routed_model"] == "custom-deployment"


def test_tracker_migrates_existing_database_without_complexity_column(tmp_path):
    db = tmp_path / "u.db"
    t = CostTracker(str(db))
    with t._connect() as conn:
        conn.execute("DROP TABLE usage")
        conn.execute(
            """
            CREATE TABLE usage (
                id INTEGER PRIMARY KEY,
                ts DATETIME DEFAULT CURRENT_TIMESTAMP,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                routed_model TEXT,
                baseline_model TEXT,
                routed_cost REAL,
                baseline_cost REAL,
                saved_cost REAL
            )
            """
        )
    migrated = CostTracker(str(db))
    migrated.record(prompt_tokens=1000, completion_tokens=1000, routed_model="gpt-4o-mini", complexity_score=30)
    totals = migrated.totals()
    assert totals["requests"] == 1
    assert totals["average_complexity_score"] == 30
