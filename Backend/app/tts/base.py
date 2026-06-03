"""Abstract base classes for TTS engines.

Every TTS engine in VoxPilot implements :class:`TTSEngine`.  The shared
:dataclass:`TTSResult` is the canonical return type for all synthesis calls.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TTSResult:
    """Immutable value object returned by every ``TTSEngine.synthesize`` call.

    Attributes
    ----------
    audio_data:
        Raw WAV bytes ready to be written to disk or streamed.
    sample_rate:
        Sample rate in Hz of the audio payload.
    duration_seconds:
        Duration of the generated audio in seconds.
    engine_name:
        Identifier of the engine that produced this result.
    """

    audio_data: bytes
    sample_rate: int
    duration_seconds: float
    engine_name: str


class TTSEngine(ABC):
    """Contract that every TTS back-end must satisfy."""

    @abstractmethod
    def synthesize(
        self,
        text: str,
        voice: str = "default",
        language: str = "en",
    ) -> TTSResult:
        """Synthesise *text* into audio.

        Parameters
        ----------
        text:
            Input text to convert to speech.
        voice:
            Voice preset identifier (engine-specific).
        language:
            BCP-47 language code.

        Returns
        -------
        TTSResult
        """
        ...

    @abstractmethod
    def get_voices(self) -> list[dict]:
        """Return a list of available voice presets.

        Each dict should contain at least ``id``, ``name``, ``language`` keys.
        """
        ...

    @abstractmethod
    def get_engine_name(self) -> str:
        """Return a human-readable engine identifier."""
        ...
