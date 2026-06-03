"""Practical contract tests for fields consumed by the Streamlit UI."""


def test_synthesis_response_audio_url_is_fetchable(client):
    result = client.post(
        "/synthesize",
        data={"text": "Frontend playback contract"},
    ).json()

    response = client.get(result["audio_url"])

    assert result["audio_url"].startswith("/audio/")
    assert response.status_code == 200
    assert response.content.startswith(b"RIFF")


def test_runs_response_contains_dashboard_fields(client):
    client.post("/synthesize", data={"text": "Frontend dashboard contract"})

    rows = client.get("/runs").json()
    row = rows[0]

    for field in (
        "created_at",
        "text",
        "voice",
        "language",
        "engine",
        "latency_ms",
        "audio_duration_seconds",
        "cache_hit",
        "success",
    ):
        assert field in row

    assert isinstance(row["success"], bool)
    assert isinstance(row["cache_hit"], bool)
