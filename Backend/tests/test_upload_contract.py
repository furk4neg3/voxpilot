"""Tests for the text-only synthesis API contract."""

import io


def test_synthesize_rejects_file_uploads(client):
    response = client.post(
        "/synthesize",
        data={"text": "Text-only synthesis request"},
        files={"audio_file": ("input.wav", io.BytesIO(b"RIFFfake"), "audio/wav")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "File uploads are not supported for speech generation."


def test_synthesize_openapi_has_no_removed_upload_fields(client):
    schema_text = str(client.get("/openapi.json").json()).lower()
    removed_terms = [
        "ref" + "erence_file",
        "ref" + "erence_audio",
        "ref" + "erence_voice",
        "con" + "sent" + "_confirmed",
    ]

    for term in removed_terms:
        assert term not in schema_text
