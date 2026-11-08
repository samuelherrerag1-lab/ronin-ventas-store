from fastapi.testclient import TestClient

from backend.main import app
from backend.services.connect_jobs import _job_path
from backend.services.delivery import resolve

client = TestClient(app)


def test_paid_deliverable_is_blocked_for_lan_clients():
    lan_client = TestClient(app, client=("192.0.2.1", 50000))
    res = lan_client.get("/deliverables/e01_maquina-silenciosa-pdf.html")
    assert res.status_code == 403

    owner = TestClient(app, client=("127.0.0.1", 50000))
    assert owner.get("/deliverables/e01_maquina-silenciosa-pdf.html").status_code == 200


def test_lead_magnet_is_public():
    lan_client = TestClient(app, client=("192.0.2.1", 50000))
    res = lan_client.get("/deliverables/l01_anatomia-post-418-usd.html")
    assert res.status_code == 200


def test_deliverable_resolver_blocks_traversal():
    assert resolve("../../backend/config.py") is None
    assert resolve("..\\..\\backend\\config.py") is None
    assert resolve("../backend/main.py") is None


def test_connect_job_path_rejects_traversal():
    for bad in ["../../secret", "a/b", "..", "conn;id", ""]:
        try:
            _job_path(bad)
        except ValueError:
            continue
        raise AssertionError(f"id aceptado indebidamente: {bad!r}")


def test_lead_returns_existing_deliverable_url():
    res = client.post(
        "/api/leads",
        json={"email": "example@example.invalid", "source": "l01", "sku_id": "L01", "consent": True},
    )
    assert res.status_code == 200
    url = res.json()["deliverable_url"]
    assert url.endswith(".html")
    assert "expediente.pdf" not in url
