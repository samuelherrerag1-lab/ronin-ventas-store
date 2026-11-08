from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_customizations_overview_has_all_skills():
    res = client.get("/api/customizations")
    assert res.status_code == 200
    data = res.json()
    assert "connectors" in data
    assert "skills" in data
    assert len(data["skills"]) >= 100
    assert len(data["connectors"]) >= 7

    c_ids = {c["connector_id"] for c in data["connectors"]}
    assert "opencode_v2" in c_ids
    assert "vertex_ai" in c_ids
    assert "threads" in c_ids


@patch("backend.services.vertex_image_service.generate_nano_banana_image")
def test_test_vertex_ai_success_and_failure(mock_gen):
    # Success case
    mock_gen.return_value = {"filename": "nb2_mock.png", "latency_sec": 1.2}
    with patch("backend.services.vertex_image_service.GENERATED_IMG_DIR") as mock_dir:
        mock_file = MagicMock()
        mock_file.exists.return_value = True
        mock_file.stat.return_value.st_size = 2048
        mock_dir.__truediv__.return_value = mock_file

        res = client.post("/api/customizations/test/vertex_ai")
        assert res.status_code == 200
        d = res.json()
        assert d["status"] == "CONECTADO"
        assert d["connector_id"] == "vertex_ai"
        assert "operativo" in d["detail"]

    # Failure case
    mock_gen.side_effect = RuntimeError("403 PERMISSION_DENIED aiplatform.endpoints.predict en example-project-id")
    res_fail = client.post("/api/customizations/test/vertex_ai")
    assert res_fail.status_code == 200
    d_fail = res_fail.json()
    assert d_fail["status"] == "FALLA"
    assert "PERMISSION_DENIED" in d_fail["detail"]


@patch("urllib.request.urlopen")
def test_test_opencode_v2_success_and_failure(mock_urlopen):
    # Mock opencode response with canonical session
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = b'{"data": [{"id": "ses_e64c0d9b1ffe56MtJmi0RNNym4"}]}'
    mock_resp.__enter__.return_value = mock_resp
    mock_urlopen.return_value = mock_resp

    with patch("backend.services.probe_runners.OPENCODE_SERVICE_PATH") as mock_path:
        mock_path.exists.return_value = True
        mock_path.read_text.return_value = '{"password": "secret-mock-token"}'

        res = client.post("/api/customizations/test/opencode_v2")
        assert res.status_code == 200
        d = res.json()
        assert d["status"] == "CONECTADO"
        assert d["connector_id"] == "opencode_v2"
        assert "ses_e64c0d9b1ffe56MtJmi0RNNym4" in d["detail"]
        assert "secret-mock-token" not in d["detail"]

    # Missing session case
    mock_resp_empty = MagicMock()
    mock_resp_empty.status = 200
    mock_resp_empty.read.return_value = b'{"data": [{"id": "ses_other"}]}'
    mock_resp_empty.__enter__.return_value = mock_resp_empty
    mock_urlopen.return_value = mock_resp_empty

    with patch("backend.services.probe_runners.OPENCODE_SERVICE_PATH") as mock_path:
        mock_path.exists.return_value = True
        mock_path.read_text.return_value = '{"password": "mock"}'

        res_miss = client.post("/api/customizations/test/opencode_v2")
        assert res_miss.status_code == 200
        d_miss = res_miss.json()
        assert d_miss["status"] == "FALLA"
        assert "no encontrada" in d_miss["detail"]


@patch("urllib.request.urlopen")
def test_social_domains_report_sin_verificar_when_reachable(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__.return_value = mock_resp
    mock_urlopen.return_value = mock_resp

    for cid in ["threads", "pinterest", "hotmart"]:
        res = client.post(f"/api/customizations/test/{cid}")
        assert res.status_code == 200
        d = res.json()
        assert d["status"] == "SIN_VERIFICAR"
        assert "no verificable automÃ¡ticamente" in d["detail"]


@patch("backend.services.probe_runners.google_session_evidence")
@patch("backend.services.probe_runners.find_chrome_executable")
def test_google_master_requires_real_google_session(mock_find, mock_evidence):
    """Chrome instalado NO es sesiÃ³n de Google: antes se reportaba CONECTADO."""
    from pathlib import Path

    mock_find.return_value = Path("C:/mock/chrome.exe")
    mock_evidence.return_value = {
        "session_found": False,
        "session_cookie_count": 0,
        "google_cookie_count": 3,
        "session_cookie_examples": [],
        "reason": "3 cookies de google.com pero ninguna de sesiÃ³n (solo preferencias)",
    }
    with patch.object(Path, "exists", return_value=True):
        res = client.post("/api/customizations/test/google_master")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "SIN_VERIFICAR"
    assert "no hay sesiÃ³n de Google" in body["detail"]

    mock_evidence.return_value = {
        "session_found": True,
        "session_cookie_count": 2,
        "google_cookie_count": 9,
        "session_cookie_examples": ["SID", "__Secure-1PSID"],
        "reason": None,
    }
    with patch.object(Path, "exists", return_value=True):
        res_ok = client.post("/api/customizations/test/google_master")
    assert res_ok.status_code == 200
    body_ok = res_ok.json()
    assert body_ok["status"] == "CONECTADO"
    assert "SesiÃ³n de Google verificada" in body_ok["detail"]


@patch("urllib.request.urlopen")
def test_social_domains_report_falla_on_network_down(mock_urlopen):
    mock_urlopen.side_effect = ConnectionResetError("Connection reset by peer")

    res = client.post("/api/customizations/test/threads")
    assert res.status_code == 200
    d = res.json()
    assert d["status"] == "FALLA"
    assert "Falla de red" in d["detail"]


@patch("backend.services.connector_diagnostics.run_connector_test")
def test_test_all_connectors_summary(mock_test_single):
    from backend.models.diagnostic_models import ConnectorTestResult

    mock_test_single.return_value = ConnectorTestResult(
        connector_id="threads",
        name="Threads (@ronoverthinks)",
        status="SIN_VERIFICAR",
        latency_ms=180.0,
        detail="Red alcanzable. SesiÃ³n no verificada.",
        checked_at="2026-11-02T19:00:00Z",
    )

    res = client.post("/api/customizations/test-all")
    assert res.status_code == 200
    d = res.json()
    assert d["total"] >= 7
    # Sin evidencia de sesiÃ³n nada puede contarse como conectado.
    assert d["connected_count"] == 0
    assert d["sin_verificar_count"] >= 7
    assert "results" in d


def test_seeded_mock_diagnostics_are_discarded():
    """Un estado con resultados sembrados no debe pintar conectores en verde."""
    from backend.services import connector_diagnostics as cd

    polluted = {
        connector_id: {
            "connector_id": "mock_id",
            "name": "Mock Connector",
            "status": "CONECTADO",
            "latency_ms": 12.5,
            "detail": "OK",
            "checked_at": "2026-11-02T19:00:00Z",
        }
        for connector_id in cd.CORE_CONNECTOR_IDS
    }

    with patch.object(cd, "_load_diagnostic_state", return_value={"last_diagnostic_results": polluted}):
        assert cd.get_last_diagnostic_results() == {}
