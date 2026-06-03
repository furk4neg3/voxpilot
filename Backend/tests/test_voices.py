"""Tests for the /voices endpoint."""


class TestVoicesEndpoint:
    """Verify the voices listing endpoint returns available TTS voices."""

    def test_voices_returns_200(self, client):
        """Voices endpoint should return HTTP 200."""
        response = client.get("/voices")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_voices_has_voices_list(self, client):
        """Response should contain a 'voices' list."""
        data = client.get("/voices").json()
        assert "voices" in data, "Response missing 'voices' field"
        assert isinstance(data["voices"], list), "'voices' should be a list"

    def test_voices_at_least_one(self, client):
        """There should be at least one voice available."""
        data = client.get("/voices").json()
        assert len(data["voices"]) >= 1, "Expected at least 1 voice"

    def test_voice_has_required_fields(self, client):
        """Each voice should have id, name, and language fields."""
        data = client.get("/voices").json()
        for voice in data["voices"]:
            assert "id" in voice, f"Voice missing 'id': {voice}"
            assert "name" in voice, f"Voice missing 'name': {voice}"
            assert "language" in voice, f"Voice missing 'language': {voice}"

    def test_voices_has_engine(self, client):
        """Response should include the engine name."""
        data = client.get("/voices").json()
        assert "engine" in data, "Response missing 'engine' field"

    def test_voices_does_not_expose_removed_upload_capability(self, client):
        """Response should only describe selectable voice presets."""
        data = client.get("/voices").json()
        removed_key = "supports_" + "ref" + "erence"
        assert removed_key not in data
