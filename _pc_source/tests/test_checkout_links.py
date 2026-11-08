"""Checkout real por SKU: validación estricta, persistencia y carga masiva."""

import json
from pathlib import Path

from fastapi.testclient import TestClient

import backend.services.catalog_seed as catalog_seed
from backend.main import app

client = TestClient(app)

GUMROAD = "https://samuelherrera.gumroad.com/l/ronin-blueprint"
HOTMART = "https://pay.hotmart.com/R99112233X"


def _catalog_items() -> list:
    return client.get("/api/catalog").json()["items"]


def _item(sku_id: str) -> dict:
    return next(item for item in _catalog_items() if item["sku_id"] == sku_id)


def _persisted(sku_id: str) -> dict:
    raw = json.loads(Path(catalog_seed.CATALOG_JSON_PATH).read_text(encoding="utf-8"))
    return next(entry for entry in raw if entry["sku_id"] == sku_id)


def test_get_catalog_exposes_checkout_ready_and_warning():
    data = client.get("/api/catalog").json()
    assert "checkout_ready_count" in data
    assert "load_warning" in data
    for item in data["items"]:
        assert isinstance(item["checkout_ready"], bool)
    assert data["checkout_ready_count"] == sum(1 for item in data["items"] if item["checkout_ready"])
    assert data["checkout_ready_count"] == sum(
        1 for item in data["items"] if item["price_usd"] > 0 and item["checkout_ready"]
    )


def test_single_checkout_persists_and_can_be_cleared():
    res = client.post(
        "/api/catalog/E01/checkout",
        json={"gumroad_url": GUMROAD, "hotmart_url": HOTMART},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["sku_id"] == "E01"
    assert body["checkout_ready"] is True
    assert body["gumroad_url"] == GUMROAD
    assert body["hotmart_url"] == HOTMART

    assert _item("E01")["checkout_ready"] is True
    stored = _persisted("E01")
    assert stored["gumroad_url"] == GUMROAD
    assert stored["hotmart_url"] == HOTMART

    cleared = client.post("/api/catalog/E01/checkout", json={"gumroad_url": ""})
    assert cleared.status_code == 200
    assert cleared.json()["gumroad_url"] == ""
    assert _persisted("E01")["gumroad_url"] == ""
    # hotmart no se envió: se conserva.
    assert _persisted("E01")["hotmart_url"] == HOTMART


def test_checkout_rejects_unsafe_urls():
    for bad in (
        "http://gumroad.com/l/abc",  # no https
        "https://evil.example.com/l/abc",  # host no permitido
        "https://gumroad.com.evil.example.com/l/abc",  # prefijo engañoso
        "https://example:EXAMPLE_REMOVED@example.invalid/l/abc",  # credenciales embebidas
        "ftp://gumroad.com/l/abc",
        "https://gumroad.com/" + "a" * 600,
    ):
        res = client.post("/api/catalog/E02/checkout", json={"gumroad_url": bad})
        assert res.status_code == 422, bad
        assert _persisted("E02")["gumroad_url"] == ""


def test_checkout_honors_env_allowlist(monkeypatch):
    monkeypatch.setenv("CHECKOUT_ALLOWED_HOSTS", "tiendamia.com")
    allowed = client.post(
        "/api/catalog/E03/checkout",
        json={"gumroad_url": "https://tiendamia.com/producto/ronin"},
    )
    assert allowed.status_code == 200
    assert allowed.json()["checkout_ready"] is True


def test_checkout_requires_a_field_and_known_sku():
    assert client.post("/api/catalog/E04/checkout", json={}).status_code == 422
    assert client.post("/api/catalog/ZZZ/checkout", json={"gumroad_url": GUMROAD}).status_code == 404


def test_checkout_bulk_updates_valid_and_reports_errors():
    payload = {
        "links": {
            "E05": {"gumroad_url": GUMROAD},
            "K01": {"gumroad_url": GUMROAD, "hotmart_url": HOTMART},
            "E06": {"gumroad_url": "http://gumroad.com/inseguro"},
            "NOPE": {"gumroad_url": GUMROAD},
            "E07": {},
        }
    }
    res = client.post("/api/catalog/checkout-bulk", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["updated"] == 2
    assert body["skipped"] == 3
    error_ids = {error["sku_id"] for error in body["errors"]}
    assert error_ids == {"E06", "NOPE", "E07"}
    for error in body["errors"]:
        assert error["reason"].strip()
    assert body["checkout_ready_count"] >= 2
    assert body["paid_skus"] == 52

    assert _persisted("E05")["gumroad_url"] == GUMROAD
    assert _persisted("K01")["hotmart_url"] == HOTMART
    assert _persisted("E06")["gumroad_url"] == ""
    raw = json.loads(Path(catalog_seed.CATALOG_JSON_PATH).read_text(encoding="utf-8"))
    assert all(entry["sku_id"] != "NOPE" for entry in raw)


def test_checkout_bulk_rejects_empty_links():
    assert client.post("/api/catalog/checkout-bulk", json={"links": {}}).status_code == 422
