"""Audio utility helpers — duration calculation and file persistence."""

from __future__ import annotations

import io
import logging
import struct
import wave
from pathlib import Path

logger = logging.getLogger(__name__)


def get_audio_duration(audio_data: bytes, sample_rate: int) -> float:
    """Return the duration **in seconds** of WAV-encoded *audio_data*.

    The function first attempts to parse the data as a standard WAV file.  If
    that fails (e.g. raw PCM bytes), it falls back to a simple size-based
    estimate assuming 16-bit mono PCM.

    Parameters
    ----------
    audio_data:
        Raw bytes of a WAV (RIFF) file **or** raw 16-bit PCM samples.
    sample_rate:
        Sample rate in Hz used for the fallback calculation.

    Returns
    -------
    float
        Duration in seconds (≥ 0.0).
    """
    if not audio_data:
        return 0.0

    # ── Try WAV header parsing first ───────────────────────────────────
    try:
        with wave.open(io.BytesIO(audio_data), "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            if rate > 0:
                return frames / rate
    except (wave.Error, struct.error, EOFError):
        logger.debug("WAV header parsing failed; falling back to raw PCM estimate.")

    # ── Fallback: assume 16-bit mono PCM ──────────────────────────────
    bytes_per_sample = 2  # 16-bit
    num_samples = len(audio_data) // bytes_per_sample
    if sample_rate > 0:
        return num_samples / sample_rate

    return 0.0


def save_audio_file(audio_data: bytes, filepath: str) -> None:
    """Persist *audio_data* to *filepath*, creating parent dirs as needed.

    Parameters
    ----------
    audio_data:
        Raw bytes (typically WAV) to write.
    filepath:
        Destination path.  Parent directories are created automatically.

    Raises
    ------
    OSError
        If the file cannot be written.
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(audio_data)
    logger.info("Audio file saved: %s (%d bytes)", filepath, len(audio_data))
