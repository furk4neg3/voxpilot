"""Tests for the /metrics endpoint."""


class TestMetricsEndpoint:
    """Verify that metrics are tracked and returned correctly."""

    def test_metrics_returns_200(self, client):
        """Metrics endpoint should return HTTP 200."""
        # Ensure at least one synthesis has been done
        client.post("/synthesize", data={"text": "Metrics test request"})
        response = client.get("/metrics")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_metrics_total_requests(self, client):
        """Total requests count should be at least 1."""
        client.post("/synthesize", data={"text": "Metrics total test"})
        data = client.get("/metrics").json()
        assert "total_requests" in data, "Response missing 'total_requests'"
        assert data["total_requests"] >= 1, (
            f"Expected total_requests >= 1, got {data['total_requests']}"
        )

    def test_metrics_successful_requests(self, client):
        """Successful requests count should be at least 1."""
        data = client.get("/metrics").json()
        assert "successful_requests" in data, "Response missing 'successful_requests'"
        assert data["successful_requests"] >= 1, (
            f"Expected successful_requests >= 1, got {data['successful_requests']}"
        )

    def test_metrics_has_average_latency(self, client):
        """Metrics should include average latency."""
        data = client.get("/metrics").json()
        assert "average_latency_ms" in data, "Response missing 'average_latency_ms'"

    def test_metrics_has_cache_hit_count(self, client):
        """Metrics should include cache hit count."""
        data = client.get("/metrics").json()
        assert "cache_hit_count" in data, "Response missing 'cache_hit_count'"

    def test_metrics_has_engine(self, client):
        """Metrics should include the engine name."""
        data = client.get("/metrics").json()
        assert "engine" in data, "Response missing 'engine'"
        assert isinstance(data["engine"], str), "Engine should be a string"

    def test_metrics_has_feedback_summary_fields(self, client):
        """Metrics should include product feedback aggregates."""
        data = client.get("/metrics").json()
        for field in (
            "feedback_count",
            "average_rating",
            "average_naturalness",
            "average_clarity",
        ):
            assert field in data, f"Response missing '{field}'"
