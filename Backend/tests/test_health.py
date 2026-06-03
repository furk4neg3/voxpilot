"""Tests for the /health endpoint."""


class TestHealthEndpoint:
    """Verify the health check endpoint returns correct system status."""

    def test_health_returns_200(self, client):
        """Health endpoint should return HTTP 200."""
        response = client.get("/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_health_status_healthy(self, client):
        """Health endpoint should report status as 'healthy'."""
        data = client.get("/health").json()
        assert data["status"] == "healthy", f"Expected 'healthy', got {data.get('status')}"

    def test_health_has_engine(self, client):
        """Health response should include the TTS engine name."""
        data = client.get("/health").json()
        assert "engine" in data, "Response missing 'engine' field"
        assert isinstance(data["engine"], str), "Engine should be a string"

    def test_health_model_loaded(self, client):
        """Health response should confirm model is loaded."""
        data = client.get("/health").json()
        assert "model_loaded" in data, "Response missing 'model_loaded' field"
        assert data["model_loaded"] is True, "model_loaded should be True"

    def test_health_has_version(self, client):
        """Health response should include the app version."""
        data = client.get("/health").json()
        assert "version" in data, "Response missing 'version' field"
        assert isinstance(data["version"], str), "Version should be a string"

    def test_health_has_timestamp(self, client):
        """Health response should include a timestamp."""
        data = client.get("/health").json()
        assert "timestamp" in data, "Response missing 'timestamp' field"
