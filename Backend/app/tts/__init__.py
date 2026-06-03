"""TTS sub-package — engine registry and factory.

Re-exports the core abstractions and provides :func:`create_engine`
which instantiates the requested back-end, falling back to
:class:`FallbackEngine` when the primary engine cannot be loaded.
"""

from __future__ import annotations

import logging

from app.tts.base import TTSEngine, TTSResult
from app.tts.fallback_engine import FallbackEngine
from app.tts.system_engine import SystemSayEngine

logger = logging.getLogger(__name__)

__all__ = [
    "TTSEngine",
    "TTSResult",
    "create_engine",
]


def create_engine(engine_name: str) -> TTSEngine:
    """Instantiate the TTS engine identified by *engine_name*.

    Falls back to :class:`FallbackEngine` when the requested engine
    cannot be loaded (missing dependencies, model download failure, etc.).

    Parameters
    ----------
    engine_name:
        One of ``"speecht5"``, ``"fallback"``, ``"fake"``.

    Returns
    -------
    TTSEngine
        A ready-to-use engine instance.
    """
    engine_name_lower = engine_name.strip().lower()

    if engine_name_lower == "fake":
        from app.tts.fake_engine import FakeTTSEngine

        logger.info("Using FakeTTSEngine (test mode).")
        return FakeTTSEngine()

    if engine_name_lower == "fallback":
        logger.info("Using FallbackEngine (explicit selection).")
        return FallbackEngine()

    if engine_name_lower in {"system", "say", "macos", "macos-say"}:
        logger.info("Using SystemSayEngine (explicit selection).")
        return SystemSayEngine()

    if engine_name_lower == "speecht5":
        try:
            from app.tts.engine import SpeechT5Engine

            engine = SpeechT5Engine()
            logger.info("SpeechT5Engine loaded successfully.")
            return engine
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Failed to load SpeechT5Engine (%s). Trying local system speech.",
                exc,
            )
            if SystemSayEngine.is_available():
                return SystemSayEngine()
            logger.warning("Local system speech unavailable. Falling back to FallbackEngine.")
            return FallbackEngine()

    # Unknown engine name → fallback.
    logger.warning(
        "Unknown engine '%s'. Falling back to FallbackEngine.",
        engine_name,
    )
    return FallbackEngine()
