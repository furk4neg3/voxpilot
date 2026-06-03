"""Unit tests for synthesis orchestration services."""

import asyncio
from pathlib import Path

from app.config import Settings
from app.services.cache_service import CacheService
from app.services.metrics_service import MetricsService
from app.services.synthesis_service import SynthesisService
from app.storage.database import Database
from app.storage.repository import RunRepository
from app.tts.fake_engine import FakeTTSEngine


def _build_service(tmp_path: Path) -> tuple[SynthesisService, RunRepository, MetricsService]:
    settings = Settings(
        engine="fake",
        audio_dir=str(tmp_path / "generated"),
        db_path=str(tmp_path / "voxpilot.db"),
    )
    settings.ensure_directories()
    database = Database(settings.db_path)
    database.init_db()
    repository = RunRepository(database)
    metrics = MetricsService()
    service = SynthesisService(
        engine=FakeTTSEngine(),
        cache=CacheService(settings.audio_dir),
        metrics=metrics,
        repository=repository,
        settings=settings,
    )
    return service, repository, metrics


def test_synthesis_service_persists_audio_and_run(tmp_path):
    service, repository, metrics = _build_service(tmp_path)

    result = asyncio.run(service.synthesize("Direct service synthesis"))

    assert result.success is True
    assert Path(result.audio_path).is_file()
    assert result.cache_hit is False
    assert repository.count_runs() == 1
    assert metrics.total_requests == 1
    assert metrics.successful_requests == 1


def test_synthesis_service_serves_repeated_request_from_cache(tmp_path):
    service, repository, metrics = _build_service(tmp_path)

    first = asyncio.run(service.synthesize("Repeatable cache request"))
    second = asyncio.run(service.synthesize("Repeatable cache request"))

    assert first.cache_hit is False
    assert second.cache_hit is True
    assert second.audio_path == first.audio_path
    assert repository.count_runs() == 2
    assert metrics.total_requests == 2
    assert metrics.get_metrics("fake-test-engine")["cache_hit_count"] == 1


def test_synthesis_service_rejects_blank_text_without_side_effects(tmp_path):
    service, repository, metrics = _build_service(tmp_path)

    try:
        asyncio.run(service.synthesize("   "))
    except ValueError as exc:
        assert "Text is required" in str(exc)
    else:
        raise AssertionError("Expected ValueError for blank text")

    assert repository.count_runs() == 0
    assert metrics.total_requests == 0
