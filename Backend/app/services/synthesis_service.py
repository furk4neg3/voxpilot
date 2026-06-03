"""Synthesis orchestration service.

Ties together the TTS engine, cache, metrics, repository, and settings
into a single ``synthesize`` call that handles the full request lifecycle.
"""

from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from app.schemas import SynthesizeResponse
from app.storage.models import GenerationRun
from app.utils.audio import get_audio_duration, save_audio_file
from app.utils.hashing import generate_cache_key
from app.utils.time import Timer

if TYPE_CHECKING:
    from app.config import Settings
    from app.services.cache_service import CacheService
    from app.services.metrics_service import MetricsService
    from app.storage.repository import RunRepository
    from app.tts.base import TTSEngine

logger = logging.getLogger(__name__)


class SynthesisService:
    """High-level service that orchestrates a single text-to-speech request.

    Parameters
    ----------
    engine:
        The TTS back-end to use for audio generation.
    cache:
        In-memory cache for de-duplicating identical requests.
    metrics:
        Metrics collector for observability.
    repository:
        Persistence layer for storing generation run records.
    settings:
        Application-wide settings (paths, limits, etc.).
    """

    def __init__(
        self,
        engine: "TTSEngine",
        cache: "CacheService",
        metrics: "MetricsService",
        repository: "RunRepository",
        settings: "Settings",
    ) -> None:
        self._engine = engine
        self._cache = cache
        self._metrics = metrics
        self._repository = repository
        self._settings = settings

    @property
    def engine(self) -> "TTSEngine":
        """Return the active TTS engine."""
        return self._engine

    @engine.setter
    def engine(self, value: "TTSEngine") -> None:
        """Replace the active TTS engine for dependency-injected tests."""
        self._engine = value

    # ── Main entry-point ──────────────────────────────────────────────

    async def synthesize(
        self,
        text: str,
        voice: str = "default",
        language: str = "en",
        metadata: Optional[dict] = None,
    ) -> SynthesizeResponse:
        """Run the full synthesis pipeline and return a ``SynthesizeResponse``.

        Parameters
        ----------
        text:
            Input text to synthesise.
        voice:
            Voice preset identifier.
        language:
            BCP-47 language code.
        metadata:
            Arbitrary caller-supplied metadata dict.

        Raises
        ------
        ValueError
            If *text* is blank or exceeds ``max_text_length``.
        """
        run_id = uuid.uuid4().hex
        text = text.strip()

        # ── Validate inputs ───────────────────────────────────────────
        if not text:
            raise ValueError("Text is required and cannot be blank.")

        if len(text) > self._settings.max_text_length:
            raise ValueError(
                f"Text length {len(text)} exceeds maximum "
                f"({self._settings.max_text_length})."
            )

        # ── Cache lookup ──────────────────────────────────────────────
        engine_name = self._engine.get_engine_name()
        cache_key = generate_cache_key(text, voice, language, engine_name)

        with Timer() as timer:
            cached_path = self._cache.get(cache_key)

            if cached_path is not None:
                # ── Cache HIT ─────────────────────────────────────────
                duration = get_audio_duration(
                    Path(cached_path).read_bytes(),
                    sample_rate=22050,
                )
                self._metrics.record_request(
                    latency_ms=timer.elapsed_ms,
                    success=True,
                    voice=voice,
                    cache_hit=True,
                )
                self._save_run(
                    run_id=run_id,
                    text=text,
                    language=language,
                    voice=voice,
                    engine=engine_name,
                    latency_ms=timer.elapsed_ms,
                    duration=duration,
                    cache_hit=True,
                    success=True,
                )
                return SynthesizeResponse(
                    success=True,
                    run_id=run_id,
                    audio_path=cached_path,
                    audio_url=f"/audio/{os.path.basename(cached_path)}",
                    latency_ms=self._format_latency(timer.elapsed_ms),
                    audio_duration_seconds=round(duration, 3),
                    real_time_factor=self._rtf(timer.elapsed_ms, duration),
                    cache_hit=True,
                    engine=engine_name,
                    voice=voice,
                    language=language,
                )

            # ── Cache MISS — synthesise ───────────────────────────────
            try:
                result = self._engine.synthesize(text, voice=voice, language=language)
            except Exception as exc:
                # Record failure & persist run record.
                self._metrics.record_request(
                    latency_ms=timer.elapsed_ms,
                    success=False,
                    voice=voice,
                    cache_hit=False,
                )
                error_msg = str(exc)
                self._save_run(
                    run_id=run_id,
                    text=text,
                    language=language,
                    voice=voice,
                    engine=engine_name,
                    latency_ms=timer.elapsed_ms,
                    duration=0.0,
                    cache_hit=False,
                    success=False,
                    error=error_msg,
                )
                logger.error(
                    "Synthesis failed for run %s: %s",
                    run_id,
                    error_msg,
                    extra={"run_id": run_id},
                )
                return SynthesizeResponse(
                    success=False,
                    run_id=run_id,
                    error=error_msg,
                    engine=engine_name,
                    voice=voice,
                    language=language,
                    latency_ms=self._format_latency(timer.elapsed_ms),
                )

        # ── Persist audio ─────────────────────────────────────────────
        filename = f"{run_id}.wav"
        audio_path = os.path.join(self._settings.audio_dir, filename)
        save_audio_file(result.audio_data, audio_path)

        # ── Update cache ──────────────────────────────────────────────
        self._cache.put(cache_key, audio_path)

        # ── Record metrics & persist run ──────────────────────────────
        latency = timer.elapsed_ms
        self._metrics.record_request(
            latency_ms=latency,
            success=True,
            voice=voice,
            cache_hit=False,
        )
        self._save_run(
            run_id=run_id,
            text=text,
            language=language,
            voice=voice,
            engine=engine_name,
            latency_ms=latency,
            duration=result.duration_seconds,
            cache_hit=False,
            success=True,
        )

        logger.info(
            "Synthesis completed for run %s (%.1f ms, %.2f s audio)",
            run_id,
            latency,
            result.duration_seconds,
            extra={
                "run_id": run_id,
                "latency_ms": latency,
                "engine": engine_name,
                "cache_hit": False,
                "voice": voice,
            },
        )

        return SynthesizeResponse(
            success=True,
            run_id=run_id,
            audio_path=audio_path,
            audio_url=f"/audio/{filename}",
            latency_ms=self._format_latency(latency),
            audio_duration_seconds=round(result.duration_seconds, 3),
            real_time_factor=self._rtf(latency, result.duration_seconds),
            cache_hit=False,
            engine=engine_name,
            voice=voice,
            language=language,
        )

    # ── Helpers ───────────────────────────────────────────────────────

    def _save_run(
        self,
        *,
        run_id: str,
        text: str,
        language: str,
        voice: str,
        engine: str,
        latency_ms: float,
        duration: float,
        cache_hit: bool,
        success: bool,
        error: Optional[str] = None,
    ) -> None:
        """Persist a ``GenerationRun`` record, swallowing DB errors."""
        try:
            run = GenerationRun(
                run_id=run_id,
                text=text[:100],
                language=language,
                voice=voice,
                engine=engine,
                latency_ms=self._format_latency(latency_ms),
                audio_duration_seconds=round(duration, 3),
                real_time_factor=self._rtf(latency_ms, duration),
                cache_hit=cache_hit,
                success=success,
                error=error,
                text_length=len(text),
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            self._repository.save_run(run)
        except Exception:
            logger.exception("Failed to persist run record %s", run_id)

    @staticmethod
    def _rtf(latency_ms: float, duration_seconds: float) -> Optional[float]:
        """Compute real-time factor (latency / audio duration).

        Returns ``None`` when *duration_seconds* is zero to avoid division
        errors.
        """
        if duration_seconds > 0:
            return round((latency_ms / 1000.0) / duration_seconds, 3)
        return None

    @staticmethod
    def _format_latency(latency_ms: float) -> float:
        """Round latency for display while preserving tiny positive timings."""
        return max(round(latency_ms, 2), 0.01)
