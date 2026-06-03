"""Tests for synthesis input validation."""
import pytest


class TestSynthesisValidation:
    """Verify that invalid synthesis inputs are properly rejected."""

    @pytest.mark.parametrize(
        "text,description",
        [
            ("", "empty text"),
            ("   ", "whitespace-only text"),
        ],
        ids=["empty_text", "whitespace_only"],
    )
    def test_empty_text_rejected(self, client, text, description):
        """Synthesis with empty or blank text should fail."""
        response = client.post("/synthesize", data={"text": text})
        # Accept either HTTP 400 or a 200 with success=False
        if response.status_code == 200:
            data = response.json()
            assert data.get("success") is False, (
                f"Expected failure for {description}, got success=True"
            )
        else:
            assert response.status_code == 400, (
                f"Expected 400 for {description}, got {response.status_code}"
            )

    def test_text_exceeds_max_length(self, client):
        """Synthesis with text exceeding max_text_length should fail."""
        long_text = "x" * 1500  # Default max is 1000
        response = client.post("/synthesize", data={"text": long_text})
        # Accept either HTTP 400 or a 200 with success=False
        if response.status_code == 200:
            data = response.json()
            assert data.get("success") is False, (
                "Expected failure for text exceeding max length, got success=True"
            )
        else:
            assert response.status_code == 400, (
                f"Expected 400 for long text, got {response.status_code}"
            )
