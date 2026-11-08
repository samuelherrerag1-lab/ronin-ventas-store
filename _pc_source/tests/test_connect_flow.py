from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_connect_without_browser_is_not_requested():
    res = client.post("/api/customizations/connect/gumroad", json={"launch_browser": False})
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "not_requested"
    assert body["verification"] == "pending"


def test_connect_unknown_browser_provider_requires_manual():
    res = client.post("/api/customizations/connect/github_pages", json={"launch_browser": True})
    assert res.status_code == 200
    assert res.json()["status"] == "manual_required"


@patch("backend.routers.api_customizations.start_job")
def test_connect_starts_worker_job(mock_start):
    mock_start.return_value = {
        "connector_id": "gumroad",
        "status": "starting",
        "step": "Preparando Chrome",
        "pid": 1234,
    }
    res = client.post("/api/customizations/connect/gumroad", json={"launch_browser": True})
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "starting"
    assert body["verification"] == "pending"
    mock_start.assert_called_once()


def test_connect_status_idle_when_no_attempt():
    res = client.get("/api/customizations/connect/threads/status")
    assert res.status_code == 200
    body = res.json()
    assert body["job"]["status"] == "idle"
    assert "secrets" in body


def test_secrets_are_masked():
    from backend.services import connect_jobs

    with patch.object(connect_jobs, "_load_secrets", return_value={"gumroad": {"access_token": "EXAMPLE_CREDENTIAL_REMOVED", "email": "example@example.invalid"}}):
        res = client.get("/api/customizations/secrets")
    assert res.status_code == 200
    assert res.json()["gumroad"]["access_token"] == "EXAMPLE_MASKED_CREDENTIAL"
    assert "abcdef123456" not in res.text
