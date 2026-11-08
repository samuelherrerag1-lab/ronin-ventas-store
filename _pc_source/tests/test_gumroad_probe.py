from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_gumroad_without_token_is_honest():
    with patch("backend.services.connect_jobs.get_secret", return_value=None):
        res = client.post("/api/customizations/test/gumroad")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "SIN_VERIFICAR"
    assert "token" in body["detail"].lower()


def test_gumroad_with_valid_token_connects():
    class FakeResponse:
        status = 200

        def read(self):
            return b'{"success": true, "user": {"email": "example@example.invalid"}}'

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    with patch("backend.services.connect_jobs.get_secret", return_value="tok_123"):
        with patch("backend.services.probe_runners.urllib.request.urlopen", return_value=FakeResponse()):
            res = client.post("/api/customizations/test/gumroad")
    body = res.json()
    assert body["status"] == "CONECTADO"
    assert "example@example.invalid" in body["detail"]


def test_gumroad_with_bad_token_fails_loudly():
    with patch("backend.services.connect_jobs.get_secret", return_value="tok_bad"):
        with patch(
            "backend.services.probe_runners.urllib.request.urlopen",
            side_effect=OSError("HTTP Error 401: Unauthorized"),
        ):
            res = client.post("/api/customizations/test/gumroad")
    body = res.json()
    assert body["status"] == "FALLA"
    assert "401" in body["detail"]


def test_github_uses_cli_status():
    class FakeProc:
        returncode = 0
        stdout = "github.com\n  ✓ Logged in to github.com account samuelherrerag1-lab (keyring)"
        stderr = ""

    with patch("backend.services.probe_store.subprocess.run", return_value=FakeProc()):
        res = client.post("/api/customizations/test/github_pages")
    body = res.json()
    assert body["status"] == "CONECTADO"
    assert "gh autenticado" in body["detail"]
