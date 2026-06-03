"""Domain model for a single generation run."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class GenerationRun:
    """Represents one text-to-speech synthesis invocation.

    Maps directly to a row in the ``generation_runs`` table.  The
    :meth:`to_dict` helper provides a dictionary suitable for JSON
    serialisation or Pydantic model construction.
    """

    run_id: str
    text: str
    language: str
    voice: str
    engine: str
    latency_ms: float
    audio_duration_seconds: float
    cache_hit: bool
    success: bool

    # ── Optional / defaulted fields ───────────────────────────────────
    id: Optional[int] = None
    real_time_factor: Optional[float] = None
    error: Optional[str] = None
    text_length: int = 0
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
    )

    # ── Serialisation ─────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Return a plain dict representation of this run record."""
        return asdict(self)


@dataclass
class FeedbackRecord:
    """Represents product feedback for one generation run."""

    run_id: str
    rating: int
    naturalness: Optional[int] = None
    clarity: Optional[int] = None
    latency_acceptability: Optional[bool] = None
    comment: Optional[str] = None
    id: Optional[int] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
    )

    def to_dict(self) -> dict:
        """Return a plain dict representation of this feedback record."""
        return asdict(self)
