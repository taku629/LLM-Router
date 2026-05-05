from llmrouter.router import complexity_score, pick_model


def test_simple_prompt_routes_to_mini():
    score = complexity_score([{"role": "user", "content": "What is the weather today?"}])
    assert score <= 30
    assert pick_model(score) == "gpt-4o-mini"


def test_complex_prompt_routes_to_gpt4o():
    msg = "Analyze and compare these approaches and write a full design.```code```"
    score = complexity_score([{"role": "user", "content": msg}])
    assert score > 30
    assert pick_model(score) == "gpt-4o"
