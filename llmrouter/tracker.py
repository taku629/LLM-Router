import sqlite3
from pathlib import Path

from .models import MODEL_TABLE


class CostTracker:
    def __init__(self, db_path: str | None = None) -> None:
        default = Path.home() / ".llmrouter" / "usage.db"
        self.db_path = Path(db_path) if db_path else default
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS usage (
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

    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        p = MODEL_TABLE[model]
        return (prompt_tokens / 1000) * p.input_per_1k + (completion_tokens / 1000) * p.output_per_1k

    def record(self, prompt_tokens: int, completion_tokens: int, routed_model: str, baseline_model: str = "gpt-4o") -> None:
        routed = self.calculate_cost(routed_model, prompt_tokens, completion_tokens)
        baseline = self.calculate_cost(baseline_model, prompt_tokens, completion_tokens)
        saved = baseline - routed
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO usage(prompt_tokens, completion_tokens, routed_model, baseline_model, routed_cost, baseline_cost, saved_cost)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (prompt_tokens, completion_tokens, routed_model, baseline_model, routed, baseline, saved),
            )

    def totals(self) -> dict[str, float]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*), COALESCE(SUM(routed_cost),0), COALESCE(SUM(baseline_cost),0), COALESCE(SUM(saved_cost),0) FROM usage"
            ).fetchone()
        return {
            "requests": float(row[0]),
            "routed_cost": float(row[1]),
            "baseline_cost": float(row[2]),
            "saved_cost": float(row[3]),
        }
