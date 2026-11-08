from fastapi.testclient import TestClient

from backend.main import app
from backend.services.catalog_seed import load_or_init_catalog

client = TestClient(app)


def test_bridge_route_serves_landing_not_dashboard():
    sku = next(item for item in load_or_init_catalog() if item.sku_id == "E01")
    res = client.get(sku.bridge_route)
    assert res.status_code == 200
    body = res.text
    assert "Ronin Ventas OS" in body
    assert sku.title in body
    assert "/assets/index-" not in body  # no es el dashboard
    assert "<script type=\"application/ld+json\">" in body


def test_every_catalog_route_has_a_landing():
    for sku in load_or_init_catalog():
        res = client.get(sku.bridge_route)
        assert res.status_code == 200, sku.bridge_route


def test_wrong_prefix_is_404():
    res = client.get("/app/maquina-silenciosa-pdf")
    assert res.status_code == 404


def test_unknown_slug_is_404():
    res = client.get("/blueprint/no-existe")
    assert res.status_code == 404


def test_landing_without_checkout_is_honest():
    sku = next(item for item in load_or_init_catalog() if item.sku_id == "E01")
    body = client.get(sku.bridge_route).text
    if not (sku.gumroad_url or sku.hotmart_url):
        assert "Checkout aún no configurado" in body
        assert "Comprar ahora" not in body
