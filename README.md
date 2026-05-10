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

`RouterClient`は設定オブジェクトか環境変数で制御できます。

```python
from llmrouter import RouterClient
from llmrouter.config import RouterConfig

client = RouterClient(
    config=RouterConfig(
        routing_threshold=24,
        low_complexity_model="gpt-4.1-mini",
        high_complexity_model="gpt-4.1",
        baseline_model="gpt-4.1",
    )
)
```

環境変数でも同じ設定ができます。

```bash
export LLMROUTER_DB_PATH="$HOME/.llmrouter/usage.db"
export LLMROUTER_ROUTING_THRESHOLD=24
export LLMROUTER_LOW_COMPLEXITY_MODEL="gpt-4.1-mini"
export LLMROUTER_HIGH_COMPLEXITY_MODEL="gpt-4.1"
export LLMROUTER_BASELINE_MODEL="gpt-4.1"
```

## CLI

```bash
llmrouter stats
```

```bash
llmrouter stats --json
```

```bash
llmrouter selftest
```

```bash
llmrouter config
```

```bash
llmrouter models
```

## Dashboard

```bash
uvicorn llmrouter.dashboard.app:app --reload
```

- `GET /` : 設定、集計、モデル別内訳
- `GET /health` : ヘルスチェック
- `GET /supported-models` : 料金テーブル

## Limits

- 複雑度スコアは `0..100` に丸められます。
- デフォルトのルーティングしきい値は `30` です。`score <= 30` は low モデル、`score > 30` は high モデルです。
- 基本点はトークン見積もり由来で最大 `40`、疑問符加点は最大 `10`、接続詞加点は最大 `10`、コードブロックは `+15` です。
- コスト集計は登録済みモデルだけ正確に計算されます。未登録モデルは `unpriced_requests` に計上されます。
- 既存DBに `complexity_score` 列がなくても起動時に自動マイグレーションします。

## Verification

この環境に `pytest` がなくても、標準ライブラリだけで主要回帰を確認できます。

```bash
python3 -m llmrouter.selftest
```
