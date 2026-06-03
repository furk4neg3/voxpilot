"""Fake TTS engine — lightweight stub for unit and integration tests.

Returns a minimal valid WAV file (0.1 s silence at 22 050 Hz) with no
computation.  This keeps test suites fast and free of ML dependencies.
"""

from __future__ import annotations

import io
import struct
import wave

from app.tts.base import TTSEngine, TTSResult

_SAMPLE_RATE = 22_050
_DURATION_SECONDS = 0.1
_NUM_SAMPLES = int(_SAMPLE_RATE * _DURATION_SECONDS)


def _make_silence_wav() -> bytes:
    """Pre-compute a minimal silent WAV to avoid per-call overhead."""
    raw = struct.pack(f"<{_NUM_SAMPLES}h", *([0] * _NUM_SAMPLES))
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(_SAMPLE_RATE)
        wf.writeframes(raw)
    return buf.getvalue()


# Module-level cache so we only build the WAV once.
_SILENCE_WAV: bytes = _make_silence_wav()


class FakeTTSEngine(TTSEngine):
    """Near-instant TTS stub for testing."""

    def synthesize(
        self,
        text: str,
        voice: str = "default",
        language: str = "en",
    ) -> TTSResult:
        return TTSResult(
            audio_data=_SILENCE_WAV,
            sample_rate=_SAMPLE_RATE,
            duration_seconds=_DURATION_SECONDS,
            engine_name=self.get_engine_name(),
        )

    def get_voices(self) -> list[dict]:
        return [
            {
                "id": "default",
                "name": "Test Voice",
                "language": "en",
                "gender": "neutral",
            },
        ]

    def get_engine_name(self) -> str:
        return "fake-test-engine"
