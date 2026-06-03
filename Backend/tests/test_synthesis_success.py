"""Tests for successful speech synthesis via POST /synthesize."""
import os


class TestSynthesisSuccess:
    """Verify that valid synthesis requests succeed and return correct metadata."""

    def test_synthesis_returns_200(self, client):
        """A valid synthesis request should return HTTP 200."""
        response = client.post("/synthesize", data={"text": "Hello world test"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_synthesis_success_flag(self, client):
        """Response should have success=True for valid requests."""
        data = client.post("/synthesize", data={"text": "Hello world test"}).json()
        assert data["success"] is True, f"Expected success=True, got {data.get('success')}"

    def test_synthesis_has_run_id(self, client):
        """Response should include a unique run_id."""
        data = client.post("/synthesize", data={"text": "Unique run id test"}).json()
        assert "run_id" in data, "Response missing 'run_id'"
        assert data["run_id"], "run_id should not be empty"

    def test_synthesis_has_audio_path(self, client):
        """Response should include the path to the generated audio file."""
        data = client.post("/synthesize", data={"text": "Audio path test"}).json()
        assert "audio_path" in data, "Response missing 'audio_path'"
        assert data["audio_path"], "audio_path should not be empty"

    def test_synthesis_latency_positive(self, client):
        """Latency should be a positive number (in milliseconds)."""
        data = client.post("/synthesize", data={"text": "Latency test"}).json()
        assert "latency_ms" in data, "Response missing 'latency_ms'"
        assert data["latency_ms"] > 0, f"Expected positive latency, got {data['latency_ms']}"

    def test_synthesis_audio_duration_positive(self, client):
        """Audio duration should be a positive number (in seconds)."""
        data = client.post("/synthesize", data={"text": "Duration test"}).json()
        assert "audio_duration_seconds" in data, "Response missing 'audio_duration_seconds'"
        assert data["audio_duration_seconds"] > 0, (
            f"Expected positive duration, got {data['audio_duration_seconds']}"
        )

    def test_synthesis_cache_hit_false_first_request(self, client):
        """First request with unique text should not be a cache hit."""
        data = client.post(
            "/synthesize", data={"text": "Unique text for cache miss check xyz"}
        ).json()
        assert "cache_hit" in data, "Response missing 'cache_hit'"
        assert data["cache_hit"] is False, "First request should have cache_hit=False"

    def test_synthesis_engine_name(self, client):
        """Engine should be the fake test engine."""
        data = client.post("/synthesize", data={"text": "Engine name test"}).json()
        assert "engine" in data, "Response missing 'engine'"
        assert data["engine"] == "fake-test-engine", (
            f"Expected 'fake-test-engine', got {data['engine']}"
        )

    def test_synthesis_audio_file_exists(self, client):
        """The generated audio file should exist on disk."""
        data = client.post("/synthesize", data={"text": "File exists test"}).json()
        audio_path = data.get("audio_path", "")
        assert audio_path, "audio_path is empty"
        assert os.path.isfile(audio_path), f"Audio file does not exist at: {audio_path}"
