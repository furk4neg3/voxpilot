"""Tests for product feedback collection."""


def _create_run(client) -> str:
    response = client.post("/synthesize", data={"text": "Feedback endpoint run"})
    assert response.status_code == 200
    return response.json()["run_id"]


def test_feedback_submission_persists_for_existing_run(client):
    run_id = _create_run(client)

    response = client.post(
        "/feedback",
        json={
            "run_id": run_id,
            "rating": 5,
            "naturalness": 4,
            "clarity": 5,
            "latency_acceptability": True,
            "comment": "Clear enough for a product demo.",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["feedback_id"] > 0
    assert data["run_id"] == run_id
    assert data["rating"] == 5
    assert data["naturalness"] == 4
    assert data["clarity"] == 5
    assert data["latency_acceptability"] is True


def test_feedback_rejects_invalid_rating(client):
    run_id = _create_run(client)

    response = client.post(
        "/feedback",
        json={"run_id": run_id, "rating": 6},
    )

    assert response.status_code == 422


def test_feedback_rejects_unknown_run(client):
    response = client.post(
        "/feedback",
        json={"run_id": "missing-run", "rating": 3},
    )

    assert response.status_code == 404


def test_feedback_summary_metrics(client):
    run_id = _create_run(client)
    client.post(
        "/feedback",
        json={
            "run_id": run_id,
            "rating": 4,
            "naturalness": 3,
            "clarity": 5,
            "latency_acceptability": False,
        },
    )

    summary = client.get("/feedback/summary").json()
    metrics = client.get("/metrics").json()

    assert summary["feedback_count"] >= 1
    assert summary["average_rating"] is not None
    assert summary["average_naturalness"] is not None
    assert summary["average_clarity"] is not None
    assert metrics["feedback_count"] == summary["feedback_count"]
    assert metrics["average_rating"] == summary["average_rating"]
