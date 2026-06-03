"""Pydantic schemas for API request / response validation.

These models define the strict contract between the FastAPI endpoints and
any client (Streamlit UI, tests, external callers).
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ────────────────────────────────────────────────────────────────────────────
# Health
# ────────────────────────────────────────────────────────────────────────────


class HealthResponse(BaseModel):
    """Response for the ``/health`` endpoint."""

    model_config = {"protected_namespaces": ()}

    status: str = Field(..., description="Overall service status (ok / degraded).")
    engine: str = Field(..., description="Active TTS engine identifier.")
    model_loaded: bool = Field(..., description="Whether the engine model is loaded.")
    version: str = Field(..., description="Application version string.")
    timestamp: str = Field(..., description="ISO-8601 UTC timestamp.")


# ────────────────────────────────────────────────────────────────────────────
# Voices
# ────────────────────────────────────────────────────────────────────────────


class VoiceInfo(BaseModel):
    """Metadata for a single available voice preset."""

    id: str
    name: str
    language: str
    gender: Optional[str] = None
    description: Optional[str] = None


class VoicesResponse(BaseModel):
    """Response for the ``/voices`` endpoint."""

    voices: list[VoiceInfo]
    engine: str


# ────────────────────────────────────────────────────────────────────────────
# Synthesis
# ────────────────────────────────────────────────────────────────────────────


class SynthesizeRequest(BaseModel):
    """Payload for the ``POST /synthesize`` endpoint."""

    text: str = Field(..., min_length=1, description="Text to synthesize.")
    language: str = Field(default="en", description="BCP-47 language tag.")
    voice: str = Field(default="default", description="Voice preset identifier.")
    style: Optional[str] = Field(default=None, description="Optional style hint.")
    metadata: Optional[dict] = Field(
        default=None,
        description="Arbitrary key-value metadata attached to this run.",
    )


class SynthesizeResponse(BaseModel):
    """Response returned after a synthesis run."""

    success: bool
    run_id: str
    audio_path: str = ""
    audio_url: str = ""
    latency_ms: float = 0.0
    audio_duration_seconds: float = 0.0
    real_time_factor: Optional[float] = None
    cache_hit: bool = False
    engine: str = ""
    voice: str = ""
    language: str = ""
    error: Optional[str] = None


# ────────────────────────────────────────────────────────────────────────────
# Feedback
# ────────────────────────────────────────────────────────────────────────────


class FeedbackRequest(BaseModel):
    """Payload for ``POST /feedback``."""

    run_id: str = Field(..., min_length=1, description="Generation run identifier.")
    rating: int = Field(..., ge=1, le=5, description="Overall rating from 1 to 5.")
    naturalness: Optional[int] = Field(
        default=None,
        ge=1,
        le=5,
        description="Optional naturalness rating from 1 to 5.",
    )
    clarity: Optional[int] = Field(
        default=None,
        ge=1,
        le=5,
        description="Optional clarity rating from 1 to 5.",
    )
    latency_acceptability: Optional[bool] = Field(
        default=None,
        description="Whether latency felt acceptable for the use case.",
    )
    comment: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional free-text feedback.",
    )


class FeedbackResponse(BaseModel):
    """Stored feedback response."""

    success: bool = True
    feedback_id: int
    run_id: str
    rating: int
    naturalness: Optional[int] = None
    clarity: Optional[int] = None
    latency_acceptability: Optional[bool] = None
    comment: Optional[str] = None
    created_at: str


class FeedbackSummaryResponse(BaseModel):
    """Aggregated feedback metrics."""

    feedback_count: int = 0
    average_rating: Optional[float] = None
    average_naturalness: Optional[float] = None
    average_clarity: Optional[float] = None
    latency_acceptability_rate: Optional[float] = None


# ────────────────────────────────────────────────────────────────────────────
# Metrics
# ────────────────────────────────────────────────────────────────────────────


class MetricsResponse(BaseModel):
    """Aggregated service metrics."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_latency_ms: float = 0.0
    p95_latency_ms: Optional[float] = None
    cache_hit_count: int = 0
    cache_hit_rate: Optional[float] = None
    most_used_voice: Optional[str] = None
    engine: str = ""
    feedback_count: int = 0
    average_rating: Optional[float] = None
    average_naturalness: Optional[float] = None
    average_clarity: Optional[float] = None
    latency_acceptability_rate: Optional[float] = None


class ErrorResponse(BaseModel):
    """Common error response shape used by FastAPI documentation."""

    detail: str


# ────────────────────────────────────────────────────────────────────────────
# Storage / Run Records
# ────────────────────────────────────────────────────────────────────────────


class RunRecord(BaseModel):
    """A single generation run as persisted in the database."""

    id: Optional[int] = None
    run_id: str
    text: str = Field(
        ...,
        max_length=100,
        description="First 100 characters of the input text.",
    )
    language: str
    voice: str
    engine: str
    latency_ms: float
    audio_duration_seconds: float
    real_time_factor: Optional[float] = None
    cache_hit: bool
    success: bool
    error: Optional[str] = None
    text_length: int = 0
    created_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO-8601 creation timestamp.",
    )
