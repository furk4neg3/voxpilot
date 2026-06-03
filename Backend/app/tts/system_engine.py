"""Local operating-system TTS engine.

On macOS this wraps the built-in ``say`` command and converts its AIFF output
to WAV with ``afconvert``. It gives VoxPilot a real no-network speech option
when SpeechT5 dependencies or model downloads are not available.
"""

from __future__ import annotations

import logging
import re
import shutil
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.tts.base import TTSEngine, TTSResult
from app.utils.audio import get_audio_duration

logger = logging.getLogger(__name__)

_SAMPLE_RATE = 22_050

_VOICE_PRESETS: dict[str, dict[str, Any]] = {
    "default": {
        "system_voice": "Samantha",
        "name": "Samantha",
        "language": "en",
        "gender": "female",
        "description": "Built-in macOS English voice.",
    },
    "samantha": {
        "system_voice": "Samantha",
        "name": "Samantha",
        "language": "en",
        "gender": "female",
        "description": "Built-in macOS English voice.",
    },
    "daniel": {
        "system_voice": "Daniel",
        "name": "Daniel",
        "language": "en",
        "gender": "male",
        "description": "Built-in macOS British English voice.",
    },
    "fred": {
        "system_voice": "Fred",
        "name": "Fred",
        "language": "en",
        "gender": "male",
        "description": "Built-in macOS classic English voice.",
    },
    "yelda": {
        "system_voice": "Yelda",
        "name": "Yelda",
        "language": "tr",
        "gender": "female",
        "description": "Built-in macOS Turkish voice.",
    },
}


class SystemSayEngine(TTSEngine):
    """Real local speech engine backed by macOS ``say``."""

    def __init__(self) -> None:
        if not self.is_available():
            raise RuntimeError(
                "SystemSayEngine requires macOS commands 'say' and 'afconvert'."
            )

    @staticmethod
    def is_available() -> bool:
        """Return whether the required macOS TTS commands are available."""
        return shutil.which("say") is not None and shutil.which("afconvert") is not None

    def synthesize(
        self,
        text: str,
        voice: str = "default",
        language: str = "en",
    ) -> TTSResult:
        system_voice = self._resolve_system_voice(voice, language)

        with tempfile.TemporaryDirectory(prefix="voxpilot_say_") as tmpdir:
            aiff_path = Path(tmpdir) / "speech.aiff"
            wav_path = Path(tmpdir) / "speech.wav"

            say_timeout = max(20, min(120, 5 + len(text) // 10))
            subprocess.run(
                ["say", "-v", system_voice, "-o", str(aiff_path), text],
                check=True,
                capture_output=True,
                timeout=say_timeout,
            )
            subprocess.run(
                [
                    "afconvert",
                    "-f",
                    "WAVE",
                    "-d",
                    f"LEI16@{_SAMPLE_RATE}",
                    str(aiff_path),
                    "-o",
                    str(wav_path),
                ],
                check=True,
                capture_output=True,
                timeout=20,
            )
            audio_data = wav_path.read_bytes()

        return TTSResult(
            audio_data=audio_data,
            sample_rate=_SAMPLE_RATE,
            duration_seconds=round(get_audio_duration(audio_data, _SAMPLE_RATE), 3),
            engine_name=self.get_engine_name(),
        )

    def get_voices(self) -> list[dict]:
        available = _available_voice_names()
        voices = []
        for voice_id, meta in _VOICE_PRESETS.items():
            if meta["system_voice"] in available:
                voices.append(
                    {
                        "id": voice_id,
                        "name": meta["name"],
                        "language": meta["language"],
                        "gender": meta["gender"],
                        "description": meta["description"],
                    }
                )
        return voices or [
            {
                "id": "default",
                "name": "System Default",
                "language": "en",
                "gender": "neutral",
                "description": "Default built-in macOS speech voice.",
            }
        ]

    def get_engine_name(self) -> str:
        return "macos-say"

    def _resolve_system_voice(self, voice: str, language: str) -> str:
        available = _available_voice_names()

        if language.lower().startswith("tr") and "Yelda" in available:
            return "Yelda"

        preset = _VOICE_PRESETS.get(voice, _VOICE_PRESETS["default"])
        system_voice = preset["system_voice"]
        if system_voice in available:
            return system_voice

        for fallback in ("Samantha", "Daniel", "Fred"):
            if fallback in available:
                return fallback

        # Let say choose its system default if parsing failed.
        return system_voice


@lru_cache(maxsize=1)
def _available_voice_names() -> set[str]:
    """Parse ``say -v ?`` into a set of installed voice names."""
    if shutil.which("say") is None:
        return set()

    try:
        result = subprocess.run(
            ["say", "-v", "?"],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Unable to list macOS voices: %s", exc)
        return set()

    names: set[str] = set()
    pattern = re.compile(r"^(.+?)\s+[a-z]{2}_[A-Z0-9]{2,3}\s+#")
    for line in result.stdout.splitlines():
        match = pattern.match(line)
        if match:
            names.add(match.group(1).strip())
    return names
