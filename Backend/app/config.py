"""Application configuration using pydantic-settings.

Loads settings from environment variables with the VOXPILOT_ prefix.
Provides a singleton accessor via ``get_settings()``.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration for the VoxPilot application.

    Every field can be overridden via an environment variable prefixed with
    ``VOXPILOT_``.  For example, ``VOXPILOT_ENGINE=speecht5`` sets the
    ``engine`` field.
    """

    # ── TTS engine selection ───────────────────────────────────────────
    engine: str = "speecht5"

    # ── Text limits ────────────────────────────────────────────────────
    max_text_length: int = 1000

    # ── File-system paths ──────────────────────────────────────────────
    audio_dir: str = "data/generated"

    # ── Database ───────────────────────────────────────────────────────
    db_path: str = "data/voxpilot.db"

    # ── Observability ──────────────────────────────────────────────────
    log_level: str = "INFO"

    # ── Server ─────────────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000

    # ── Metadata ───────────────────────────────────────────────────────
    app_version: str = "0.1.0"

    model_config = {
        "env_prefix": "VOXPILOT_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    # ── Helpers ────────────────────────────────────────────────────────

    def ensure_directories(self) -> None:
        """Create required data directories if they do not exist."""
        Path(self.audio_dir).mkdir(parents=True, exist_ok=True)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings singleton."""
    return Settings()
