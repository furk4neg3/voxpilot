"""Fallback TTS engine — generates sine-wave tones using only the stdlib.

Used when no ML-backed engine is available (e.g. missing ``torch``).  The
output is a valid WAV file whose frequency varies per voice preset, giving
a recognisable (if robotic) audio signal.
"""

from __future__ import annotations

import io
import math
import struct
import wave

from app.tts.base import TTSEngine, TTSResult

# ── Frequency map per voice ─────────────────────────────────────────────────
_VOICE_FREQUENCIES: dict[str, float] = {
    "default": 440.0,    # A4
    "low":     261.63,   # C4
    "mid":     329.63,   # E4
    "high":    523.25,   # C5
}

_SAMPLE_RATE = 22_050


class FallbackEngine(TTSEngine):
    """Zero-dependency TTS engine that produces audible sine-wave WAV files.

    Duration scales linearly with input text length so that short texts
    produce short tones and long texts produce longer ones.
    """

    def synthesize(
        self,
        text: str,
        voice: str = "default",
        language: str = "en",
    ) -> TTSResult:
        frequency = _VOICE_FREQUENCIES.get(voice, _VOICE_FREQUENCIES["default"])
        duration = self._text_to_duration(text)

        num_samples = int(_SAMPLE_RATE * duration)
        samples: list[int] = []

        for i in range(num_samples):
            t = i / _SAMPLE_RATE
            # Apply a gentle fade-in / fade-out envelope to avoid clicks.
            envelope = 1.0
            fade_samples = min(int(0.01 * _SAMPLE_RATE), num_samples // 4)
            if i < fade_samples:
                envelope = i / fade_samples
            elif i > num_samples - fade_samples:
                envelope = (num_samples - i) / fade_samples

            value = envelope * 0.5 * math.sin(2.0 * math.pi * frequency * t)
            samples.append(int(value * 32767))

        # ── Encode WAV ────────────────────────────────────────────────
        raw_data = struct.pack(f"<{len(samples)}h", *samples)

        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(_SAMPLE_RATE)
            wf.writeframes(raw_data)

        wav_bytes = buf.getvalue()
        actual_duration = num_samples / _SAMPLE_RATE

        return TTSResult(
            audio_data=wav_bytes,
            sample_rate=_SAMPLE_RATE,
            duration_seconds=round(actual_duration, 3),
            engine_name=self.get_engine_name(),
        )

    def get_voices(self) -> list[dict]:
        descriptions = {
            "default": "440 Hz sine-wave tone (A4). Fallback engine.",
            "low": "261.63 Hz sine-wave tone (C4). Fallback engine.",
            "mid": "329.63 Hz sine-wave tone (E4). Fallback engine.",
            "high": "523.25 Hz sine-wave tone (C5). Fallback engine.",
        }
        return [
            {
                "id": voice_id,
                "name": f"{voice_id.title()} Tone",
                "language": "en",
                "gender": "neutral",
                "description": descriptions[voice_id],
            }
            for voice_id in _VOICE_FREQUENCIES
        ]

    def get_engine_name(self) -> str:
        return "fallback-tone-generator"

    # ── Internals ─────────────────────────────────────────────────────

    @staticmethod
    def _text_to_duration(text: str) -> float:
        """Map text length to a reasonable audio duration (seconds)."""
        raw = len(text) * 0.05
        return max(0.5, min(raw, 10.0))
