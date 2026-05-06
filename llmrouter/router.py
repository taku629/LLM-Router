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


def _extract_text(messages: list[dict[str, Any]]) -> str:
    parts = []
    for m in messages:
        content = m.get("content", "")
        if isinstance(content, str):
            parts.append(content)
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


def pick_model(score: int) -> str:
    if score <= 30:
        return "gpt-4o-mini"
    return "gpt-4o"
