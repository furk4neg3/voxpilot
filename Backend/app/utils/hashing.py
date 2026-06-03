"""Deterministic cache-key generation for synthesis requests."""

from __future__ import annotations

import hashlib


def generate_cache_key(
    text: str,
    voice: str,
    language: str,
    engine: str,
) -> str:
    """Return a hex SHA-256 digest that uniquely identifies a synthesis request.

    The key is derived from the concatenation of the four input fields
    separated by a NUL byte (to avoid ambiguous collisions).

    Parameters
    ----------
    text:
        Input text to synthesise.
    voice:
        Voice preset identifier.
    language:
        BCP-47 language code.
    engine:
        Name of the TTS engine.

    Returns
    -------
    str
        64-character lowercase hexadecimal SHA-256 digest.
    """
    payload = "\x00".join([text, voice, language, engine])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
