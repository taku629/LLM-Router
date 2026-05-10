from dataclasses import dataclass
import re
from typing import Any

LOW_COMPLEXITY_KEYWORDS = {
    "translate", "summarize", "classify", "qa", "q&a",
    "翻訳", "要約", "分類", "教えて",
}
HIGH_COMPLEXITY_KEYWORDS = {
    "explain", "analyze", "write a", "compare", "design", "reason",
    "説明", "分析", "比較", "設計", "考察", "論じ", "評価",
}
DEFAULT_COMPLEXITY_THRESHOLD = 30
DEFAULT_LOW_COMPLEXITY_MODEL = "gpt-4o-mini"
DEFAULT_HIGH_COMPLEXITY_MODEL = "gpt-4o"


@dataclass(frozen=True)
class RoutingDecision:
    score: int
    model: str
    threshold: int
    low_complexity_model: str
    high_complexity_model: str

    @property
    def routed_high(self) -> bool:
        return self.model == self.high_complexity_model


def _collect_text(content: Any, parts: list[str]) -> None:
    if isinstance(content, str):
        parts.append(content)
        return
    if isinstance(content, list):
        for item in content:
            _collect_text(item, parts)
        return
    if isinstance(content, dict):
        content_type = content.get("type")
        if content_type in {"text", "input_text", "output_text"}:
            text = content.get("text")
            if isinstance(text, str):
                parts.append(text)
                return
        for key in ("text", "content"):
            value = content.get(key)
            if value is not None:
                _collect_text(value, parts)


def _extract_text(messages: list[dict[str, Any]]) -> str:
    parts = []
    for m in messages:
        _collect_text(m.get("content", ""), parts)
    return "\n".join(parts)


def complexity_score(messages: list[dict[str, Any]]) -> int:
    text = _extract_text(messages)
    text_lower = text.lower()
    token_estimate = max(1, len(text.split()))
    score = min(40, token_estimate // 5)

    for kw in LOW_COMPLEXITY_KEYWORDS:
        if kw in text_lower:
            score -= 5
    for kw in HIGH_COMPLEXITY_KEYWORDS:
        if kw in text_lower:
            score += 10

    if "```" in text:
        score += 15

    score += min(text.count("?") + text.count("？"), 5) * 2
    score += min(len(re.findall(r"\b(and|but|however|therefore|while)\b", text_lower)) * 2, 10)
    return max(0, min(100, score))


def pick_model(
    score: int,
    threshold: int = DEFAULT_COMPLEXITY_THRESHOLD,
    low_complexity_model: str = DEFAULT_LOW_COMPLEXITY_MODEL,
    high_complexity_model: str = DEFAULT_HIGH_COMPLEXITY_MODEL,
) -> str:
    if score <= threshold:
        return low_complexity_model
    return high_complexity_model


def route_messages(
    messages: list[dict[str, Any]],
    threshold: int = DEFAULT_COMPLEXITY_THRESHOLD,
    low_complexity_model: str = DEFAULT_LOW_COMPLEXITY_MODEL,
    high_complexity_model: str = DEFAULT_HIGH_COMPLEXITY_MODEL,
) -> RoutingDecision:
    score = complexity_score(messages)
    model = pick_model(
        score,
        threshold=threshold,
        low_complexity_model=low_complexity_model,
        high_complexity_model=high_complexity_model,
    )
    return RoutingDecision(
        score=score,
        model=model,
        threshold=threshold,
        low_complexity_model=low_complexity_model,
        high_complexity_model=high_complexity_model,
    )
