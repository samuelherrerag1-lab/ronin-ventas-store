"""Endurecimiento del backend: honestidad, FX, límites, atomicidad y auth.

Un test por bug real que encontró la auditoría (docs/CRITIQUE_SYSTEM.md A1/A2/
A3/M4/M5/A8/B7). Si algo vuelve a fingir un estado o a corromper datos, falla.
"""

import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient

import backend.services.catalog_seed as catalog_seed
import backend.services.social_feed_seed as social_feed_seed
from backend.config import BASE_DIR, GLOBAL_SKILLS_DIR
from backend.main import app
from backend.services.csv_sales_parser import parse_sales_csv
from backend.services.skills_catalog import DEFAULT_SKILLS
from backend.services.skills_loader import load_all_skills

client = TestClient(app)
DATA_DIR = BASE_DIR / "data"
GUMROAD = "https://samuelherrera.gumroad.com/l/ronin"

HOTMART_CSV = """Codigo de transaccion;Fecha;Producto;Precio;Moneda
HP-1;2026-11-02;E01 Producto;79.800;COP
HP-2;2026-11-02;E02 Brasil;R$ 100,00;BRL
HP-3;2026-11-02;E03 Europa;100 EUR;EUR
HP-4;2026-11-02;E04 Mexico;500 MXN;MXN
"""

GUMROAD_CSV = """Order ID,Date,Product Name,Price,Currency,Refunded
GR-1,2026-11-01,E01 Producto,19.00,USD,false
GR-2,2026-11-01,Order Bump +$9,9.00,USD,false
"""


def test_csv_fx_thousands_and_unsupported_currency():
    parsed = parse_sales_csv(HOTMART_CSV, "hotmart")
    assert parsed.imported_count == 3
    assert parsed.skipped_count == 1
    assert any("MXN" in error for error in parsed.errors)
    by_order = {sale.order_id: sale for sale in parsed.all_sales}
    assert by_order["HP-1"].amount_cop == 79800.0  # "79.800" son miles, no 79.8
    assert by_order["HP-1"].amount_usd == 19.0  # TRM única 4200
    assert by_order["HP-2"].amount_usd == 18.0  # BRL convertido
    assert by_order["HP-3"].amount_usd == 108.0  # EUR convertido
    assert all(sale.currency in ("COP", "BRL", "EUR", "USD") for sale in parsed.all_sales)


def test_metrics_summary_separates_order_bumps_and_labels_attribution():
    client.delete("/api/metrics/reset")
    assert client.post("/api/metrics/import-csv", json={"source": "gumroad", "csv_content": GUMROAD_CSV}).status_code == 200
    assert client.post("/api/metrics/import-csv", json={"source": "hotmart", "csv_content": HOTMART_CSV}).status_code == 200
    summary = client.get("/api/metrics").json()
    assert summary["product_sales_count"] == 4
    assert summary["total_sales"] == 4  # el bump NO es una venta de producto
    assert summary["order_bumps_count"] == 1
    assert summary["order_bumps_revenue_usd"] == 9.0
    assert summary["product_revenue_usd"] == 164.0
    assert summary["total_revenue_usd"] == 173.0
    assert summary["aov_usd"] == 41.0
    assert "aproximada" in summary["attribution_note"].lower()


def test_csv_import_never_returns_pii():
    csv_text = """Order ID,Date,Product Name,Price,Currency,Customer Email
GR-9,2026-11-01,E01 Producto,19.00,USD,example@example.invalid
"""
    res = client.post("/api/metrics/import-csv", json={"source": "gumroad", "csv_content": csv_text})
    assert res.status_code == 200
    assert "example@example.invalid" not in res.text
    assert res.json()["all_sales"] == []
    assert all(sale["customer_email"] is None for sale in res.json()["sales_sample"])


def test_csv_parser_does_not_invent_order_ids():
    csv_text = "Date,Product Name,Price,Currency\n2026-11-01,E01 Producto,19.00,USD\n"
    parsed = parse_sales_csv(csv_text, "gumroad")
    sale = parsed.all_sales[0]
    assert sale.order_id == ""
    assert sale.id.startswith("gumroad_row_")
    assert any("Order ID" in error for error in parsed.errors)


def test_metrics_input_validation_and_csv_size_limit():
    assert client.post(
        "/api/metrics/manual-entry",
        json={"date": "2026-11-02", "platform": "instagram", "piece_id": "x"},
    ).status_code == 422
    assert client.post(
        "/api/metrics/manual-entry",
        json={"date": "2026-11-02", "platform": "threads", "piece_id": "x", "impressions": -5},
    ).status_code == 422
    assert client.post(
        "/api/metrics/manual-entry",
        json={"date": "hola", "platform": "threads", "piece_id": "x"},
    ).status_code == 422
    too_big = "Date,Product Name,Price\n" + "x" * 2_000_001
    assert client.post("/api/metrics/import-csv", json={"source": "gumroad", "csv_content": too_big}).status_code == 422


def test_leads_require_consent_and_known_sku():
    assert client.post("/api/leads", json={"email": "example@example.invalid", "sku_id": "ZZZ", "consent": True}).status_code == 422
    assert client.post("/api/leads", json={"email": "example@example.invalid", "sku_id": "L01"}).status_code == 422
    ok = client.post("/api/leads", json={"email": "example@example.invalid", "sku_id": "L01", "consent": True})
    assert ok.status_code == 200
    assert ok.json()["deliverable_url"].endswith(".html")


def test_feeds_toggle_is_local_tracking_only():
    feeds = client.get("/api/feeds").json()
    assert feeds["published_to_network"] is False
    assert "no publica" in feeds["publication_note"].lower()
    assert all(post["status_source"] == "local_tracking" for post in feeds["threads"])

    res = client.post("/api/feeds/threads/th_001/toggle-status")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "published"
    assert body["published_to_network"] is False
    assert body["detail"]
    # El JSON del feed NUNCA guarda "published": el estado real es local.
    raw = json.loads(Path(social_feed_seed.FEEDS_JSON_PATH).read_text(encoding="utf-8"))
    assert all(post["status"] == "queued" for post in raw["threads"])

    back = client.post("/api/feeds/threads/th_001/toggle-status").json()
    assert back["status"] == "queued"


def test_mutate_hook_is_template_variant_without_fake_metrics():
    before = next(p for p in client.get("/api/feeds").json()["threads"] if p["post_id"] == "th_001")
    res = client.post("/api/feeds/threads/th_001/mutate-hook")
    assert res.status_code == 200
    body = res.json()
    assert body["engine"] == "template_variant"
    assert body["ai_used"] is False
    assert body["mutation_note"]
    assert body["simulated_likes"] == before["simulated_likes"]  # mutar no genera likes


def test_connect_invalid_id_is_422_not_500():
    assert client.get("/api/customizations/connect/BAD/status").status_code == 422
    assert client.post("/api/customizations/connect/BAD/stop").status_code == 422


def test_catalog_corrupt_json_degrades_with_backup():
    catalog_path = Path(catalog_seed.CATALOG_JSON_PATH)
    catalog_path.write_text("{ esto no es json", encoding="utf-8")
    res = client.get("/api/catalog")
    assert res.status_code == 200
    data = res.json()
    assert data["total_skus"] == 55
    assert data["load_warning"] and "ilegible" in data["load_warning"]
    assert list(catalog_path.parent.glob("catalog.corrupt-*.json")), "debe quedar backup del JSON dañado"
    assert client.get("/api/catalog").json()["load_warning"] is None


def test_publish_data_has_no_test_contamination():
    raw = json.loads((DATA_DIR / "social_feeds.json").read_text(encoding="utf-8"))
    texts = ["\n".join(post.get("body_slides") or []) for post in raw["threads"]]
    assert not any("Prueba de inyección" in text for text in texts)
    assert not any(post.get("hook_pattern") == "Custom Bait Studio Injection" for post in raw["threads"])
    assert len(raw["threads"]) >= 4
    own_pins = [pin for pin in raw["pinterest"] if not pin.get("is_competitor_benchmark")]
    assert len(own_pins) >= 7
    assert any(pin.get("is_competitor_benchmark") for pin in raw["pinterest"]), "benchmarks se conservan"


def test_data_dir_not_mutated_by_suite(data_dir_snapshot):
    changed = []
    for name, expected in data_dir_snapshot["files"].items():
        path = DATA_DIR / name
        if not path.is_file():
            changed.append((name, "desapareció"))
            continue
        current = hashlib.sha256(path.read_bytes()).hexdigest()
        if current != expected:
            changed.append((name, "hash distinto"))
    assert changed == [], f"pytest modificó datos de producción: {changed}"


def test_skills_installed_on_disk_is_measured():
    for skill in load_all_skills(DEFAULT_SKILLS, {}):
        expected = (GLOBAL_SKILLS_DIR / skill.skill_id).is_dir()
        assert skill.installed_on_disk is expected, skill.skill_id


def test_landing_shows_checkout_only_when_configured():
    assert client.post("/api/catalog/E01/checkout", json={"gumroad_url": GUMROAD}).status_code == 200
    sku = next(item for item in catalog_seed.load_or_init_catalog() if item.sku_id == "E01")
    landing = client.get(sku.bridge_route).text
    assert GUMROAD in landing
    assert "Comprar ahora" in landing
    assert "Checkout aún no configurado" not in landing
