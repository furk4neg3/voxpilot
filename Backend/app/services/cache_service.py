"""In-memory audio cache backed by a simple dict.

Maps deterministic cache keys (SHA-256 hex digests) to file paths on disk.
Tracks hit / miss statistics for observability.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class CacheService:
    """Lightweight in-process cache for generated audio files.

    Parameters
    ----------
    audio_dir:
        Base directory where generated audio files are stored.  Used only
        for documentation / validation — the actual paths are stored as
        provided by the caller.
    """

    def __init__(self, audio_dir: str) -> None:
        self._audio_dir = audio_dir
        self._cache: dict[str, str] = {}
        self._hit_count: int = 0
        self._total_lookups: int = 0

    # ── Public API ────────────────────────────────────────────────────

    def get(self, cache_key: str) -> Optional[str]:
        """Return the cached file path for *cache_key*, or ``None``.

        Only returns a path if the backing file still exists on disk.
        """
        self._total_lookups += 1
        filepath = self._cache.get(cache_key)

        if filepath is not None and Path(filepath).is_file():
            self._hit_count += 1
            logger.debug("Cache HIT for key %s → %s", cache_key[:12], filepath)
            return filepath

        if filepath is not None:
            # Entry exists but file was deleted externally — evict.
            logger.warning(
                "Cache entry %s points to missing file %s; evicting.",
                cache_key[:12],
                filepath,
            )
            del self._cache[cache_key]

        logger.debug("Cache MISS for key %s", cache_key[:12])
        return None

    def put(self, cache_key: str, filepath: str) -> None:
        """Store *filepath* under *cache_key*."""
        self._cache[cache_key] = filepath
        logger.debug("Cache PUT key %s → %s", cache_key[:12], filepath)

    def has(self, cache_key: str) -> bool:
        """Check whether *cache_key* is present **without** affecting stats."""
        filepath = self._cache.get(cache_key)
        return filepath is not None and Path(filepath).is_file()

    @property
    def stats(self) -> dict:
        """Return current cache statistics."""
        hit_rate = (
            self._hit_count / self._total_lookups
            if self._total_lookups > 0
            else 0.0
        )
        return {
            "hit_count": self._hit_count,
            "total_lookups": self._total_lookups,
            "hit_rate": round(hit_rate, 4),
        }
