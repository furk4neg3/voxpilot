"""Tests for TTS engine abstractions and fallback behavior."""

from app.tts import create_engine
import pytest

from app.tts.fake_engine import FakeTTSEngine
from app.tts.fallback_engine import FallbackEngine
from app.tts.system_engine import SystemSayEngine
from app.utils.audio import get_audio_duration


def test_fake_engine_returns_deterministic_valid_wav():
    engine = FakeTTSEngine()

    first = engine.synthesize("hello")
    second = engine.synthesize("hello again")

    assert first.audio_data.startswith(b"RIFF")
    assert b"WAVE" in first.audio_data[:16]
    assert first.audio_data == second.audio_data
    assert first.engine_name == "fake-test-engine"


def test_fallback_engine_generates_playable_wav_and_voice_metadata():
    engine = FallbackEngine()

    result = engine.synthesize("fallback audio", voice="default")
    voices = engine.get_voices()

    assert result.audio_data.startswith(b"RIFF")
    assert get_audio_duration(result.audio_data, result.sample_rate) > 0
    assert result.engine_name == "fallback-tone-generator"
    assert voices
    assert {"id", "name", "language"}.issubset(voices[0])


def test_create_engine_uses_fake_and_unknown_fallback_without_ml_dependencies():
    fake = create_engine("fake")
    unknown = create_engine("does-not-exist")

    assert isinstance(fake, FakeTTSEngine)
    assert isinstance(unknown, FallbackEngine)


@pytest.mark.skipif(
    not SystemSayEngine.is_available(),
    reason="macOS say/afconvert are not available",
)
def test_system_say_engine_generates_real_wav():
    engine = SystemSayEngine()

    result = engine.synthesize("Hello from VoxPilot", voice="default", language="en")

    assert result.audio_data.startswith(b"RIFF")
    assert b"WAVE" in result.audio_data[:16]
    assert result.duration_seconds > 0
    assert result.engine_name == "macos-say"
