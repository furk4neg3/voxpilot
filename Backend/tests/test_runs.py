"""Tests for the /runs endpoint."""


class TestRunsEndpoint:
    """Verify that synthesis run history is tracked and retrievable."""

    def test_runs_returns_200(self, client):
        """Runs endpoint should return HTTP 200."""
        # Ensure at least one run exists
        client.post("/synthesize", data={"text": "Runs endpoint test"})
        response = client.get("/runs")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_runs_returns_list(self, client):
        """Runs endpoint should return a list."""
        data = client.get("/runs").json()
        assert isinstance(data, list), f"Expected list, got {type(data).__name__}"

    def test_runs_at_least_one(self, client):
        """There should be at least one run entry."""
        data = client.get("/runs").json()
        assert len(data) >= 1, "Expected at least 1 run entry"

    def test_run_has_required_fields(self, client):
        """Each run entry should have all required metadata fields."""
        data = client.get("/runs").json()
        entry = data[0]
        required_fields = [
            "run_id", "text", "voice", "language",
            "engine", "latency_ms", "success", "created_at",
        ]
        for field in required_fields:
            assert field in entry, f"Run entry missing '{field}' field"

    def test_run_success_is_boolean(self, client):
        """The success field in run entries should be a boolean."""
        data = client.get("/runs").json()
        entry = data[0]
        assert isinstance(entry["success"], bool), (
            f"Expected bool for success, got {type(entry['success']).__name__}"
        )

    def test_run_latency_positive(self, client):
        """Latency in run entries should be positive."""
        data = client.get("/runs").json()
        entry = data[0]
        assert entry["latency_ms"] > 0, (
            f"Expected positive latency, got {entry['latency_ms']}"
        )
