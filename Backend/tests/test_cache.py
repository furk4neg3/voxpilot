"""Tests for synthesis result caching."""


class TestCaching:
    """Verify that repeated identical requests are served from cache."""

    def test_cache_hit_on_second_request(self, client):
        """Second identical request should be a cache hit."""
        payload = {
            "text": "Cache test deterministic text for hit check",
            "voice": "default",
            "language": "en",
        }

        # First request — should be a cache miss
        first = client.post("/synthesize", data=payload).json()
        assert first["success"] is True, "First synthesis should succeed"
        assert first["cache_hit"] is False, (
            f"First request should be cache miss, got cache_hit={first['cache_hit']}"
        )

        # Second request with identical parameters — should be a cache hit
        second = client.post("/synthesize", data=payload).json()
        assert second["success"] is True, "Second synthesis should succeed"
        assert second["cache_hit"] is True, (
            f"Second identical request should be cache hit, got cache_hit={second['cache_hit']}"
        )

    def test_cache_miss_on_different_text(self, client):
        """Requests with different text should not hit cache."""
        first = client.post(
            "/synthesize", data={"text": "First unique text alpha"}
        ).json()
        second = client.post(
            "/synthesize", data={"text": "Second unique text beta"}
        ).json()

        assert first["success"] is True, "First request should succeed"
        assert second["success"] is True, "Second request should succeed"
        assert first["cache_hit"] is False, "First request should be cache miss"
        assert second["cache_hit"] is False, "Different text should be cache miss"
