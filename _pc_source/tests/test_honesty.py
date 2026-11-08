"""Guardarraíles de honestidad.

Estos tests existen porque el sistema mostraba 8 conectores en verde sin ninguna
cuenta conectada, y `pytest` sembraba ese estado falso en `data/`.
Si alguno falla, la UI está mintiendo otra vez.
"""

import json

from fastapi.testclient import TestClient

from backend.config import BASE_DIR, CATALOG_JSON_PATH
from backend.main import app
from backend.services.product_factory import DELIVERABLES_DIR

client = TestClient(app)

STATE_PATH = BASE_DIR / "data" / "customizations_state.json"


def test_no_seeded_mock_state_on_disk():
    raw = STATE_PATH.read_text(encoding="utf-8")
    assert "mock_id" not in raw
    assert "Mock Connector" not in raw
    assert '"detail": "OK"' not in raw


def test_connect_never_claims_connected():
    for connector_id in ("threads", "pinterest", "gumroad", "hotmart"):
        res = client.post(
            f"/api/customizations/connect/{connector_id}", json={"launch_browser": False}
        )
        assert res.status_code == 200
        body = res.json()
        assert body["status"] != "connected"
        assert body["verification"] == "pending"


def test_stealth_diagnostic_has_no_invented_score():
    data = client.get("/api/customizations").json()
    diag = data["stealth_Diagnostic"]
    assert diag["liarjs_target_score"] is None
    assert diag["fingerprint_measured"] is False
    assert "ua_rotation_disabled" not in diag
    assert "webgl_gpu_consistent" not in diag


def test_finops_declares_its_source():
    finops = client.get("/api/customizations").json()["finops"]
    assert finops["ledger_source"] in ("local", "sibling", "defaults")
    assert isinstance(finops["ledger_found"], bool)


def test_published_sku_requires_checkout_url():
    """Un SKU `published` sin pasarela es venta fingida.

    Antes este test pasaba porque NINGÚN SKU estaba published (vacío). Ahora
    además valida la URL real y demuestra el invariante configurando un checkout
    por la API: sin URL => checkout_ready False; con URL => True.
    """
    raw = json.loads(CATALOG_JSON_PATH.read_text(encoding="utf-8"))
    offenders = [
        item["sku_id"]
        for item in raw
        if item.get("status") == "published"
        and not (item.get("gumroad_url") or item.get("hotmart_url"))
    ]
    assert offenders == [], f"SKUs publicados sin checkout: {offenders}"

    # Cualquier URL guardada debe ser https y de un host permitido.
    allowed = ("gumroad.com", "hotmart.com")
    for item in raw:
        for field in ("gumroad_url", "hotmart_url"):
            url = item.get(field) or ""
            if not url:
                continue
            assert url.startswith("https://"), (item["sku_id"], field, url)
            host = url.split("://", 1)[1].split("/", 1)[0].split(":", 1)[0].lower()
            assert any(host == hostname or host.endswith(f".{hostname}") for hostname in allowed), (
                item["sku_id"],
                field,
                host,
            )

    # Invariante funcional: sin URL no hay checkout_ready; con URL sí.
    before = client.get("/api/catalog").json()["items"]
    sku = next(item for item in before if item["price_usd"] > 0 and not item["checkout_ready"])
    assert sku["checkout_ready"] is False

    saved = client.post(
        f"/api/catalog/{sku['sku_id']}/checkout",
        json={"gumroad_url": "https://samuelherrera.gumroad.com/l/ronin"},
    )
    assert saved.status_code == 200
    assert saved.json()["checkout_ready"] is True
    after = client.get("/api/catalog").json()
    updated = next(item for item in after["items"] if item["sku_id"] == sku["sku_id"])
    assert updated["checkout_ready"] is True
    assert after["checkout_ready_count"] >= 1


def test_every_catalog_sku_has_its_deliverable():
    items = client.get("/api/catalog").json()["items"]
    missing = [
        item["sku_id"]
        for item in items
        if not (DELIVERABLES_DIR / f'{item["sku_id"].lower()}_{item["slug"]}.html').is_file()
    ]
    assert missing == [], f"SKUs sin entregable en disco: {missing}"
