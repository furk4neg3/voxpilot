"""Repository for persisting and querying generation run records."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.storage.database import Database
    from app.storage.models import FeedbackRecord, GenerationRun

logger = logging.getLogger(__name__)

_INSERT_RUN = """\
INSERT INTO generation_runs (
    run_id, text, language, voice, engine,
    latency_ms, audio_duration_seconds, real_time_factor,
    cache_hit, success, error, text_length, created_at
) VALUES (
    :run_id, :text, :language, :voice, :engine,
    :latency_ms, :audio_duration_seconds, :real_time_factor,
    :cache_hit, :success, :error, :text_length, :created_at
);
"""

_INSERT_FEEDBACK = """\
INSERT INTO feedback (
    run_id, rating, naturalness, clarity,
    latency_acceptability, comment, created_at
) VALUES (
    :run_id, :rating, :naturalness, :clarity,
    :latency_acceptability, :comment, :created_at
);
"""


class RunRepository:
    """CRUD repository for :class:`GenerationRun` records.

    Parameters
    ----------
    database:
        :class:`Database` instance used to obtain connections.
    """

    def __init__(self, database: "Database") -> None:
        self._db = database

    def save_run(self, run: "GenerationRun") -> None:
        """Insert a :class:`GenerationRun` into the database.

        Boolean fields are coerced to ``int`` for SQLite compatibility.
        """
        conn = self._db.get_connection()
        try:
            params = run.to_dict()
            # SQLite stores booleans as integers.
            params["cache_hit"] = int(params["cache_hit"])
            params["success"] = int(params["success"])
            # Remove auto-generated PK.
            params.pop("id", None)

            conn.execute(_INSERT_RUN, params)
            conn.commit()
            logger.debug("Saved run %s to database.", run.run_id)
        finally:
            conn.close()

    def get_runs(
        self,
        limit: int = 50,
        status: Optional[str] = None,
        voice: Optional[str] = None,
        language: Optional[str] = None,
        cache_hit: Optional[bool] = None,
    ) -> list[dict]:
        """Retrieve recent runs with optional filters.

        Parameters
        ----------
        limit:
            Maximum number of rows to return.
        status:
            Filter by ``"success"`` or ``"failed"``.
        voice:
            Filter by voice preset.
        language:
            Filter by language code.
        cache_hit:
            Filter by cache-hit flag.

        Returns
        -------
        list[dict]
            Rows as dictionaries, most recent first.
        """
        clauses: list[str] = []
        params: dict = {}

        if status == "success":
            clauses.append("success = 1")
        elif status in {"failed", "error"}:
            clauses.append("success = 0")

        if voice is not None:
            clauses.append("voice = :voice")
            params["voice"] = voice

        if language is not None:
            clauses.append("language = :language")
            params["language"] = language

        if cache_hit is not None:
            clauses.append("cache_hit = :cache_hit")
            params["cache_hit"] = int(cache_hit)

        where = ""
        if clauses:
            where = "WHERE " + " AND ".join(clauses)

        query = f"SELECT * FROM generation_runs {where} ORDER BY created_at DESC LIMIT :limit"
        params["limit"] = limit

        conn = self._db.get_connection()
        try:
            rows = conn.execute(query, params).fetchall()
            return [self._row_to_dict(row) for row in rows]
        finally:
            conn.close()

    def count_runs(self) -> int:
        """Return the total number of stored run records."""
        conn = self._db.get_connection()
        try:
            row = conn.execute("SELECT COUNT(*) AS cnt FROM generation_runs").fetchone()
            return row["cnt"] if row else 0
        finally:
            conn.close()

    def run_exists(self, run_id: str) -> bool:
        """Return whether a generation run exists."""
        conn = self._db.get_connection()
        try:
            row = conn.execute(
                "SELECT 1 FROM generation_runs WHERE run_id = :run_id LIMIT 1",
                {"run_id": run_id},
            ).fetchone()
            return row is not None
        finally:
            conn.close()

    def save_feedback(self, feedback: "FeedbackRecord") -> dict:
        """Persist feedback for a generation run and return the stored row."""
        conn = self._db.get_connection()
        try:
            params = feedback.to_dict()
            if params["latency_acceptability"] is not None:
                params["latency_acceptability"] = int(params["latency_acceptability"])
            params.pop("id", None)

            cursor = conn.execute(_INSERT_FEEDBACK, params)
            conn.commit()
            feedback_id = cursor.lastrowid
            row = conn.execute(
                "SELECT * FROM feedback WHERE id = :id",
                {"id": feedback_id},
            ).fetchone()
            return self._feedback_row_to_dict(row)
        finally:
            conn.close()

    def get_feedback_summary(self) -> dict:
        """Return aggregate feedback metrics for dashboard and API use."""
        conn = self._db.get_connection()
        try:
            row = conn.execute(
                """\
                SELECT
                    COUNT(*) AS feedback_count,
                    AVG(rating) AS average_rating,
                    AVG(naturalness) AS average_naturalness,
                    AVG(clarity) AS average_clarity,
                    AVG(CASE
                        WHEN latency_acceptability IS NULL THEN NULL
                        ELSE latency_acceptability
                    END) AS latency_acceptability_rate
                FROM feedback;
                """
            ).fetchone()
            if row is None:
                return self._empty_feedback_summary()

            summary = dict(row)
            summary["feedback_count"] = int(summary.get("feedback_count") or 0)
            for key in (
                "average_rating",
                "average_naturalness",
                "average_clarity",
                "latency_acceptability_rate",
            ):
                value = summary.get(key)
                summary[key] = round(value, 2) if value is not None else None
            return summary
        finally:
            conn.close()

    @staticmethod
    def _row_to_dict(row) -> dict:
        """Convert a SQLite row into API/UI-friendly JSON primitives."""
        data = dict(row)
        for key in ("cache_hit", "success"):
            if key in data:
                data[key] = bool(data[key])
        data["status"] = "success" if data.get("success") else "failed"
        data["timestamp"] = data.get("created_at")
        return data

    @staticmethod
    def _feedback_row_to_dict(row) -> dict:
        """Convert a feedback row into API/UI-friendly JSON primitives."""
        data = dict(row)
        if data.get("latency_acceptability") is not None:
            data["latency_acceptability"] = bool(data["latency_acceptability"])
        data["feedback_id"] = data.pop("id")
        data["success"] = True
        return data

    @staticmethod
    def _empty_feedback_summary() -> dict:
        """Return an empty feedback summary shape."""
        return {
            "feedback_count": 0,
            "average_rating": None,
            "average_naturalness": None,
            "average_clarity": None,
            "latency_acceptability_rate": None,
        }
