from fastapi.testclient import TestClient
from backend.config import BASE_DIR
from backend.main import app
from backend.services.product_factory import DELIVERABLES_DIR

client = TestClient(app)


def test_health_check():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"


def test_catalog_has_52_paid_skus_and_unique_routes():
    res = client.get("/api/catalog")
    assert res.status_code == 200
    data = res.json()
    assert data["paid_skus"] == 52
    assert data["lead_magnets"] == 3
    assert data["total_skus"] == 55
    assert data["unique_bridge_routes"] == 55

    formats = {item["format"] for item in data["items"]}
    assert "ebook_blueprint" in formats
    assert "boveda_arsenal" in formats
    assert "micro_app_html" in formats
    assert "kit_sistema" in formats
    assert "mega_bundle" in formats


def test_catalog_generate_real_deliverable():
    res = client.post("/api/catalog/A01/generate-deliverable")
    assert res.status_code == 200
    data = res.json()
    assert data["sku_id"] == "A01"
    assert data["status"] == "generated"
    assert data["deliverable_url"].startswith("/deliverables/")
    assert data["bytes"] > 20_000  # no un HTML vacío/placeholder

    deliverable = DELIVERABLES_DIR / data["filename"]
    assert deliverable.is_file()
    assert deliverable.stat().st_size == data["bytes"]
    html = deliverable.read_text(encoding="utf-8", errors="ignore")
    assert "</html>" in html.lower()
    assert "<title>" in html.lower()
    assert "{{" not in html

    # El producto de pago solo se sirve al dueño local (no a la LAN).
    owner = TestClient(app, client=("127.0.0.1", 50000))
    served = owner.get(data["deliverable_url"])
    assert served.status_code == 200
    assert served.headers["content-type"].startswith("text/html")


def test_catalog_toggle_stan_featured():
    res = client.post("/api/catalog/E03/toggle-stan")
    assert res.status_code == 200
    toggled = res.json()["featured_on_stan"]
    res2 = client.post("/api/catalog/E03/toggle-stan")
    assert res2.status_code == 200
    assert res2.json()["featured_on_stan"] != toggled


def test_feeds_threads_and_pinterest_infiltration_mode():
    res_all = client.get("/api/feeds?include_benchmarks=true")
    assert res_all.status_code == 200
    feeds_all = res_all.json()
    assert len(feeds_all["threads"]) >= 4
    assert len(feeds_all["pinterest"]) >= 7

    res_own = client.get("/api/feeds?include_benchmarks=false")
    assert res_own.status_code == 200
    feeds_own = res_own.json()
    assert len(feeds_own["pinterest"]) < len(feeds_all["pinterest"])
    assert all(not p["is_competitor_benchmark"] for p in feeds_own["pinterest"])


def test_mutate_thread_hook_and_create_bait_post():
    res_mut = client.post("/api/feeds/threads/th_001/mutate-hook")
    assert res_mut.status_code == 200
    mutated = res_mut.json()
    assert mutated["post_id"] == "th_001"
    assert len(mutated["body_slides"][0]) > 20

    res_create = client.post(
        "/api/feeds/threads/from-bait",
        json={
            "headline_metric": "$619.20 USD",
            "sub_metric": "11 notificaciones en 6h",
            "notifications": ["Gumroad: You made a sale! $29.00"],
            "widget_type": "ios_lockscreen",
            "post_text": "Prueba de inyección desde el laboratorio de anzuelos.",
            "target_sku_id": "E01",
        },
    )
    assert res_create.status_code == 200
    created = res_create.json()
    assert created["bait_widget"]["headline_metric"] == "$619.20 USD"


def test_customizations_hub_and_connector_state():
    res = client.get("/api/customizations")
    assert res.status_code == 200
    data = res.json()
    connector_ids = {c["connector_id"] for c in data["connectors"]}
    assert {"google_master", "threads", "pinterest", "gumroad", "hotmart", "vertex_ai", "github_pages"}.issubset(
        connector_ids
    )
    # El score de fingerprint no existe hasta que una sonda real lo mida.
    assert data["stealth_Diagnostic"]["liarjs_target_score"] is None
    assert data["stealth_Diagnostic"]["fingerprint_measured"] is False

    res_conn = client.post("/api/customizations/connect/pinterest", json={"launch_browser": False})
    assert res_conn.status_code == 200
    # Abrir el login no conecta nada: solo deja la verificación pendiente.
    assert res_conn.json()["status"] == "not_requested"
    assert res_conn.json()["verification"] == "pending"

    res_sk = client.post("/api/customizations/skills/viral-hook-creator/toggle", json={"enabled": False})
    assert res_sk.status_code == 200
    assert res_sk.json()["enabled"] is False
    client.post("/api/customizations/skills/viral-hook-creator/toggle", json={"enabled": True})


def test_render_ios17_retina_png():
    res = client.post(
        "/api/customizations/render-ios-png",
        json={
            "headline_metric": "$418.50 USD",
            "sub_metric": "7 notificaciones en 4h",
            "notifications": ["Gumroad: You made a sale! $27.00 — Bóveda 500 Hooks"],
            "timestamp_label": "07:12",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["image_url"].startswith("/generated_images/ios17_bait_")
    assert data["bytes"] > 5000


def test_strict_atomic_file_line_limit():
    """Verifica que NINGÚN archivo de código (.py, .ts, .tsx) supere las 250 líneas."""
    code_extensions = {".py", ".ts", ".tsx"}
    excluded_dirs = {"node_modules", "dist", ".venv", "__pycache__", ".git", "data"}

    violating_files = []
    for path in BASE_DIR.rglob("*"):
        if any(part in excluded_dirs for part in path.parts):
            continue
        if path.is_file() and path.suffix in code_extensions:
            line_count = len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
            if line_count > 250:
                violating_files.append((str(path.relative_to(BASE_DIR)), line_count))

    assert violating_files == [], f"Archivos que violan el límite de 250 líneas: {violating_files}"
