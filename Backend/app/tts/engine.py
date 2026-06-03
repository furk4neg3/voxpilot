"""SpeechT5 TTS engine — wraps Microsoft SpeechT5 via HuggingFace Transformers.

All heavy imports (``torch``, ``transformers``, ``datasets``) are guarded so
the module can be imported even when those packages are not installed.
"""

from __future__ import annotations

import io
import logging
import re
import struct
import wave
from typing import Any, Optional

from app.tts.base import TTSEngine, TTSResult

logger = logging.getLogger(__name__)

# ── Guard heavy imports ─────────────────────────────────────────────────────
_HAS_DEPS = False
try:
    import numpy as np
    import torch
    from datasets import load_dataset
    from transformers import SpeechT5ForTextToSpeech, SpeechT5HifiGan, SpeechT5Processor

    _HAS_DEPS = True
except ImportError:
    np = None  # type: ignore[assignment]
    torch = None  # type: ignore[assignment]
    logger.warning(
        "SpeechT5 dependencies not installed (torch / transformers / datasets). "
        "SpeechT5Engine will raise on instantiation."
    )

# ── Voice presets ───────────────────────────────────────────────────────────
# Indices into the CMU-ARCTIC xvector dataset (7931 entries).
_VOICE_PRESETS: dict[str, dict[str, Any]] = {
    "default": {
        "index": 7306,
        "name": "Default (Female 1)",
        "language": "en",
        "gender": "female",
        "description": "Clear female voice with neutral intonation.",
    },
    "female-1": {
        "index": 7306,
        "name": "Female 1",
        "language": "en",
        "gender": "female",
        "description": "Clear female voice with neutral intonation.",
    },
    "female-2": {
        "index": 5800,
        "name": "Female 2",
        "language": "en",
        "gender": "female",
        "description": "Warm female voice with slightly lower pitch.",
    },
    "male-1": {
        "index": 600,
        "name": "Male 1",
        "language": "en",
        "gender": "male",
        "description": "Standard male voice with moderate pace.",
    },
    "male-2": {
        "index": 1500,
        "name": "Male 2",
        "language": "en",
        "gender": "male",
        "description": "Deep male voice with slower cadence.",
    },
    "narrator": {
        "index": 3000,
        "name": "Narrator",
        "language": "en",
        "gender": "neutral",
        "description": "Expressive voice suited for storytelling and narration.",
    },
}

# Maximum characters per chunk when splitting long texts.
_MAX_CHUNK_CHARS = 500


class SpeechT5Engine(TTSEngine):
    """TTS engine backed by ``microsoft/speecht5_tts``.

    Downloads the model, processor, vocoder, and preset embedding assets on first
    instantiation.  Subsequent calls reuse the cached artefacts.
    """

    def __init__(self) -> None:
        if not _HAS_DEPS:
            raise RuntimeError(
                "Cannot instantiate SpeechT5Engine — required packages "
                "(torch, transformers, datasets) are not installed."
            )

        logger.info("Loading SpeechT5 model, processor, and vocoder …")
        self._processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
        self._model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
        self._vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

        logger.info("Loading CMU-ARCTIC preset embeddings.")
        self._embeddings_dataset = load_dataset(
            "Matthijs/cmu-arctic-xvectors",
            split="validation",
        )
        self._sample_rate = 16_000
        logger.info("SpeechT5Engine initialised (sample_rate=%d)", self._sample_rate)

    # ── Public interface ──────────────────────────────────────────────

    def synthesize(
        self,
        text: str,
        voice: str = "default",
        language: str = "en",
    ) -> TTSResult:
        """Synthesise *text* into WAV audio using the selected *voice*."""
        preset_embedding = self._get_preset_embedding(voice)
        chunks = self._split_text(text)

        all_speech: list[Any] = []
        for chunk in chunks:
            inputs = self._processor(text=chunk, return_tensors="pt")
            with torch.no_grad():
                speech = self._model.generate_speech(
                    inputs["input_ids"],
                    preset_embedding,
                    vocoder=self._vocoder,
                )
            all_speech.append(speech.cpu().numpy())

        combined = np.concatenate(all_speech) if len(all_speech) > 1 else all_speech[0]
        wav_bytes = self._to_wav_bytes(combined)
        duration = len(combined) / self._sample_rate

        return TTSResult(
            audio_data=wav_bytes,
            sample_rate=self._sample_rate,
            duration_seconds=round(duration, 3),
            engine_name=self.get_engine_name(),
        )

    def get_voices(self) -> list[dict]:
        return [
            {
                "id": vid,
                "name": meta["name"],
                "language": meta["language"],
                "gender": meta["gender"],
                "description": meta["description"],
            }
            for vid, meta in _VOICE_PRESETS.items()
        ]

    def get_engine_name(self) -> str:
        return "speecht5"

    # ── Internals ─────────────────────────────────────────────────────

    def _get_preset_embedding(self, voice: str) -> "torch.Tensor":
        """Resolve *voice* to the selected preset embedding tensor."""
        preset = _VOICE_PRESETS.get(voice, _VOICE_PRESETS["default"])
        idx = preset["index"]
        xvector = self._embeddings_dataset[idx]["xvector"]
        return torch.tensor(xvector, dtype=torch.float32).unsqueeze(0)

    @staticmethod
    def _split_text(text: str) -> list[str]:
        """Split *text* into chunks of ≤ ``_MAX_CHUNK_CHARS`` on sentence boundaries."""
        if len(text) <= _MAX_CHUNK_CHARS:
            return [text]

        # Split on sentence-ending punctuation followed by whitespace.
        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks: list[str] = []
        current = ""

        for sentence in sentences:
            if current and len(current) + len(sentence) + 1 > _MAX_CHUNK_CHARS:
                chunks.append(current.strip())
                current = sentence
            else:
                current = f"{current} {sentence}" if current else sentence

        if current.strip():
            chunks.append(current.strip())

        # Safety: if a single sentence exceeds the limit, hard-split it.
        final: list[str] = []
        for chunk in chunks:
            while len(chunk) > _MAX_CHUNK_CHARS:
                # Try to split on the last space within the limit.
                split_pos = chunk.rfind(" ", 0, _MAX_CHUNK_CHARS)
                if split_pos == -1:
                    split_pos = _MAX_CHUNK_CHARS
                final.append(chunk[:split_pos].strip())
                chunk = chunk[split_pos:].strip()
            if chunk:
                final.append(chunk)

        return final

    def _to_wav_bytes(self, audio_array: "np.ndarray") -> bytes:
        """Convert a float32 numpy array to 16-bit PCM WAV bytes."""
        # Normalise to int16 range.
        audio_int16 = np.clip(audio_array, -1.0, 1.0)
        audio_int16 = (audio_int16 * 32767).astype(np.int16)

        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self._sample_rate)
            wf.writeframes(audio_int16.tobytes())
        return buf.getvalue()
