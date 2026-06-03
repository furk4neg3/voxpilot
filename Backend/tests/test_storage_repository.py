"""Tests for SQLite run repository behavior."""

from datetime import datetime, timezone

from app.storage.database import Database
from app.storage.models import FeedbackRecord, GenerationRun
from app.storage.repository import RunRepository


def _repository(tmp_path) -> RunRepository:
    database = Database(str(tmp_path / "runs.db"))
    database.init_db()
    return RunRepository(database)


def _run(run_id: str, *, success: bool = True, cache_hit: bool = False) -> GenerationRun:
    return GenerationRun(
        run_id=run_id,
        text="Stored repository text",
        language="en",
        voice="default",
        engine="fake-test-engine",
        latency_ms=12.3,
        audio_duration_seconds=0.1,
        real_time_factor=0.123,
        cache_hit=cache_hit,
        success=success,
        error=None if success else "boom",
        text_length=22,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def test_repository_returns_json_friendly_booleans_and_aliases(tmp_path):
    repository = _repository(tmp_path)
    repository.save_run(_run("run-success", success=True, cache_hit=True))

    rows = repository.get_runs()

    assert len(rows) == 1
    row = rows[0]
    assert row["success"] is True
    assert row["cache_hit"] is True
    assert row["status"] == "success"
    assert row["timestamp"] == row["created_at"]


def test_repository_filters_failed_and_error_status_alias(tmp_path):
    repository = _repository(tmp_path)
    repository.save_run(_run("run-success", success=True))
    repository.save_run(_run("run-failed", success=False))

    failed = repository.get_runs(status="failed")
    error = repository.get_runs(status="error")

    assert [row["run_id"] for row in failed] == ["run-failed"]
    assert [row["run_id"] for row in error] == ["run-failed"]
    assert failed[0]["success"] is False
    assert failed[0]["status"] == "failed"


def test_repository_persists_feedback_and_summary(tmp_path):
    repository = _repository(tmp_path)
    repository.save_run(_run("run-feedback", success=True))

    stored = repository.save_feedback(
        FeedbackRecord(
            run_id="run-feedback",
            rating=5,
            naturalness=4,
            clarity=5,
            latency_acceptability=True,
            comment="Clear output for the requested text.",
        )
    )
    summary = repository.get_feedback_summary()

    assert stored["success"] is True
    assert stored["feedback_id"] > 0
    assert stored["latency_acceptability"] is True
    assert summary["feedback_count"] == 1
    assert summary["average_rating"] == 5.0
    assert summary["average_naturalness"] == 4.0
    assert summary["average_clarity"] == 5.0
    assert summary["latency_acceptability_rate"] == 1.0
