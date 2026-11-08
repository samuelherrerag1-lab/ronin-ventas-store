from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_lead_capture_stores_and_deduplicates():
    payload = {"email": "example@example.invalid", "source": "l01", "sku_id": "L01", "consent": True}

    first = client.post("/api/leads", json=payload)
    assert first.status_code == 200
    body = first.json()
    assert body["status"] == "stored"
    assert body["total_leads"] == 1

    second = client.post("/api/leads", json=payload)
    assert second.status_code == 200
    assert second.json()["status"] == "already_registered"
    assert second.json()["total_leads"] == 1


def test_lead_capture_rejects_invalid_email():
    res = client.post("/api/leads", json={"email": "no-es-correo", "source": "l01", "sku_id": "L01"})
    assert res.status_code == 422


def test_lead_count_endpoint_hides_emails():
    client.post(
        "/api/leads",
        json={"email": "example@example.invalid", "source": "l01", "sku_id": "L01", "consent": True},
    )
    res = client.get("/api/leads/count")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert "@" not in str(data)
