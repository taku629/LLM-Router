from llmrouter.router import complexity_score, pick_model, route_messages


def test_simple_prompt_routes_to_mini():
    score = complexity_score([{"role": "user", "content": "What is the weather today?"}])
    assert score <= 30
    assert pick_model(score) == "gpt-4o-mini"


def test_complex_prompt_routes_to_gpt4o():
    msg = "Analyze and compare these approaches and write a full design.```code```"
    score = complexity_score([{"role": "user", "content": msg}])
    assert score > 30
    assert pick_model(score) == "gpt-4o"


def test_structured_content_contributes_to_complexity():
    messages = [
        {
            "role": "user",
            "content": [{"type": "text", "text": "Analyze and compare this architecture in detail."}],
        }
    ]
    score = complexity_score(messages)
    assert score > 0
    assert pick_model(score) == "gpt-4o-mini"


def test_pick_model_uses_custom_threshold_and_models():
    assert pick_model(24, threshold=20, low_complexity_model="gpt-4.1-mini", high_complexity_model="gpt-4.1") == "gpt-4.1"
    assert pick_model(20, threshold=20, low_complexity_model="gpt-4.1-mini", high_complexity_model="gpt-4.1") == "gpt-4.1-mini"


def test_route_messages_returns_decision_metadata():
    decision = route_messages(
        [{"role": "user", "content": "Analyze and compare this architecture thoroughly."}],
        threshold=20,
        low_complexity_model="gpt-4.1-mini",
        high_complexity_model="gpt-4.1",
    )
    assert decision.score > 0
    assert decision.model == "gpt-4.1"
    assert decision.routed_high is True
