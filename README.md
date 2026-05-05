# LLM Cost Router

OpenAI互換の`RouterClient`で、プロンプト複雑度に応じて`gpt-4o-mini`/`gpt-4o`を自動ルーティングします。

## Quick Start

```python
from llmrouter import RouterClient as OpenAI
client = OpenAI()

res = client.chat.completions.create(
    messages=[{"role": "user", "content": "今日の天気は？"}],
)
```

## CLI

```bash
llmrouter stats
```

## Dashboard

```bash
uvicorn llmrouter.dashboard.app:app --reload
```
