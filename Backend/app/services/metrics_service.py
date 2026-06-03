"""In-memory metrics aggregation for synthesis requests.

All counters and latency histograms are process-local; a restart clears them.
For durable metrics, rely on the SQLite run repository.
"""

from __future__ import annotations

import logging
from collections import Counter
from typing import Optional

logger = logging.getLogger(__name__)


class MetricsService:
    """Tracks request counts, latencies, cache hits, and voice usage."""

    def __init__(self) -> None:
        self.total_requests: int = 0
        self.successful_requests: int = 0
        self.failed_requests: int = 0
        self._latencies: list[float] = []
        self._cache_hits: int = 0
        self._voice_usage: Counter = Counter()

    # ── Recording ─────────────────────────────────────────────────────

    def record_request(
        self,
        latency_ms: float,
        success: bool,
        voice: str,
        cache_hit: bool,
    ) -> None:
        """Record a single synthesis request.

        Parameters
        ----------
        latency_ms:
            Wall-clock latency of the request in milliseconds.
        success:
            ``True`` if the request completed without error.
        voice:
            Voice preset identifier that was used.
        cache_hit:
            ``True`` if the result was served from cache.
        """
        self.total_requests += 1

        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1

        self._latencies.append(latency_ms)

        if cache_hit:
            self._cache_hits += 1

        self._voice_usage[voice] += 1

    # ── Computed properties ───────────────────────────────────────────

    @property
    def average_latency(self) -> float:
        """Mean latency across all recorded requests (ms)."""
        if not self._latencies:
            return 0.0
        return sum(self._latencies) / len(self._latencies)

    @property
    def p95_latency(self) -> Optional[float]:
        """95th-percentile latency (ms), or ``None`` if < 2 samples."""
        if len(self._latencies) < 2:
            return None
        sorted_lats = sorted(self._latencies)
        idx = int(len(sorted_lats) * 0.95)
        idx = min(idx, len(sorted_lats) - 1)
        return sorted_lats[idx]

    @property
    def most_used_voice(self) -> Optional[str]:
        """Voice with the highest total usage, or ``None``."""
        if not self._voice_usage:
            return None
        return self._voice_usage.most_common(1)[0][0]

    # ── Snapshot ──────────────────────────────────────────────────────

    def get_metrics(self, engine_name: str) -> dict:
        """Return a snapshot dict matching the ``MetricsResponse`` schema.

        Parameters
        ----------
        engine_name:
            Name of the active TTS engine (pass-through for context).
        """
        cache_hit_rate: Optional[float] = None
        if self.total_requests > 0:
            cache_hit_rate = round(self._cache_hits / self.total_requests, 4)

        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "average_latency_ms": round(self.average_latency, 2),
            "p95_latency_ms": round(self.p95_latency, 2) if self.p95_latency is not None else None,
            "cache_hit_count": self._cache_hits,
            "cache_hit_rate": cache_hit_rate,
            "most_used_voice": self.most_used_voice,
            "engine": engine_name,
        }
