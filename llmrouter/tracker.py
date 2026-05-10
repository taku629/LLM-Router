import sqlite3
from pathlib import Path

from .config import default_db_path
from .models import get_model_pricing


class CostTracker:
    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = Path(db_path) if db_path else default_db_path()
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
                    complexity_score INTEGER,
                    routed_cost REAL,
                    baseline_cost REAL,
                    saved_cost REAL
                )
                """
            )
            columns = {
                row[1] for row in conn.execute("PRAGMA table_info(usage)").fetchall()
            }
            if "complexity_score" not in columns:
                conn.execute("ALTER TABLE usage ADD COLUMN complexity_score INTEGER")

    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float | None:
        p = get_model_pricing(model)
        if p is None:
            return None
        return (prompt_tokens / 1000) * p.input_per_1k + (completion_tokens / 1000) * p.output_per_1k

    def record(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        routed_model: str,
        baseline_model: str = "gpt-4o",
        complexity_score: int | None = None,
    ) -> bool:
        routed = self.calculate_cost(routed_model, prompt_tokens, completion_tokens)
        baseline = self.calculate_cost(baseline_model, prompt_tokens, completion_tokens)
        saved = None
        if routed is not None and baseline is not None:
            saved = baseline - routed
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO usage(
                    prompt_tokens,
                    completion_tokens,
                    routed_model,
                    baseline_model,
                    complexity_score,
                    routed_cost,
                    baseline_cost,
                    saved_cost
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    prompt_tokens,
                    completion_tokens,
                    routed_model,
                    baseline_model,
                    complexity_score,
                    routed,
                    baseline,
                    saved,
                ),
            )
        return routed is not None and baseline is not None

    def totals(self) -> dict[str, float]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    COUNT(*),
                    COALESCE(SUM(routed_cost), 0),
                    COALESCE(SUM(baseline_cost), 0),
                    COALESCE(SUM(saved_cost), 0),
                    COALESCE(AVG(routed_cost), 0),
                    COALESCE(AVG(saved_cost), 0),
                    COALESCE(AVG(complexity_score), 0),
                    SUM(CASE WHEN routed_cost IS NOT NULL AND baseline_cost IS NOT NULL THEN 1 ELSE 0 END),
                    SUM(CASE WHEN routed_cost IS NULL OR baseline_cost IS NULL THEN 1 ELSE 0 END)
                FROM usage
                """
            ).fetchone()
        return {
            "requests": float(row[0]),
            "routed_cost": float(row[1]),
            "baseline_cost": float(row[2]),
            "saved_cost": float(row[3]),
            "average_routed_cost": float(row[4]),
            "average_saved_cost": float(row[5]),
            "average_complexity_score": float(row[6]),
            "priced_requests": float(row[7] or 0),
            "unpriced_requests": float(row[8] or 0),
        }

    def model_breakdown(self) -> list[dict[str, float | str]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    routed_model,
                    COUNT(*),
                    COALESCE(AVG(complexity_score), 0),
                    COALESCE(SUM(routed_cost), 0),
                    COALESCE(SUM(saved_cost), 0)
                FROM usage
                GROUP BY routed_model
                ORDER BY COUNT(*) DESC, routed_model ASC
                """
            ).fetchall()
        return [
            {
                "routed_model": row[0],
                "requests": float(row[1]),
                "average_complexity_score": float(row[2]),
                "routed_cost": float(row[3]),
                "saved_cost": float(row[4]),
            }
            for row in rows
        ]
