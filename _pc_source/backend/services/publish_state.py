"""Estado LOCAL de publicación y diagnóstico de readiness para salir a vender.

Este módulo NO publica en Threads ni en Pinterest: no hay API oficial, cookies
ni automatización de escritura aquí. Guarda qué piezas el operador marcó como
publicadas A MANO y calcula, con datos reales en disco, si el sistema está listo
para cobrar y publicar.
"""

import datetime
from typing import Any, Dict, List, Optional

from backend.config import DATA_DIR, PUBLISH_SITE_DIR
from backend.services.catalog_seed import load_or_init_catalog
from backend.services.json_store import lock_for, read_json, write_json_atomic
from backend.services.product_factory import DELIVERABLES_DIR
from backend.services.social_feed_seed import load_or_init_feeds
from backend.services.vertex_image_service import vertex_status

PUBLISH_STATE_PATH = DATA_DIR / "publish_state.json"
COVERS_DIR = DATA_DIR / "product_art" / "web" / "covers"
MANIFEST_PATH = PUBLISH_SITE_DIR / "manifest.json"
VALID_PLATFORMS = ("threads", "pinterest")
VALID_STATUSES = ("queued", "published")
EXPECTED_SKUS = 55
MIN_THREADS = 4
MIN_PINS = 7
LOCAL_ONLY_NOTE = (
    "Seguimiento local: el sistema NO publica en Threads ni Pinterest. "
    "'published' significa que TÚ lo publicaste a mano en la red; no hay URL ni "
    "timestamp devuelto por la plataforma."
)
CHECKOUT_ACTION = (
    "Crear los {paid} productos en Gumroad (USD / Apple Pay) y Hotmart "
    "(COP / Nequi / PSE / Efecty) y pegar cada URL de checkout en Publish Center "
    "(POST /api/catalog/checkout-bulk). Faltan {missing} SKUs."
)


def manifest_path() -> Any:
    return MANIFEST_PATH


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _load() -> Dict[str, Any]:
    with lock_for(PUBLISH_STATE_PATH):
        data, error = read_json(PUBLISH_STATE_PATH)
    if error or not isinstance(data, dict):
        return {"platforms": {}, "updated_at": None}
    if not isinstance(data.get("platforms"), dict):
        data["platforms"] = {}
    return data


def _tracked_items(platform: str) -> Dict[str, Dict[str, Any]]:
    items = _load()["platforms"].get(platform, {})
    return items if isinstance(items, dict) else {}


def local_status(platform: str, item_id: str, default: str = "queued") -> str:
    entry = _tracked_items(platform).get(item_id) or {}
    status = entry.get("status", default)
    return status if status in VALID_STATUSES else default


def status_map(platform: str) -> Dict[str, str]:
    return {
        item_id: entry.get("status", "queued")
        for item_id, entry in _tracked_items(platform).items()
        if isinstance(entry, dict) and entry.get("status") in VALID_STATUSES
    }


def mark_item(platform: str, item_id: str, status: str) -> Dict[str, Any]:
    """Persiste SOLO el seguimiento local. Nunca publica en la red."""
    if platform not in VALID_PLATFORMS:
        raise ValueError(f"Plataforma inválida: {platform}. Usa {', '.join(VALID_PLATFORMS)}")
    if status not in VALID_STATUSES:
        raise ValueError(f"Estado inválido: {status}. Usa {', '.join(VALID_STATUSES)}")
    with lock_for(PUBLISH_STATE_PATH):
        data = _load()
        data["platforms"].setdefault(platform, {})[item_id] = {
            "status": status,
            "updated_at": _now(),
        }
        data["updated_at"] = _now()
        write_json_atomic(PUBLISH_STATE_PATH, data)
    return {
        "platform": platform,
        "item_id": item_id,
        "status": status,
        "tracked_locally": True,
        "published_to_network": False,
        "publication_url": None,
        "note": LOCAL_ONLY_NOTE,
    }


def _cover_skus() -> set:
    if not COVERS_DIR.is_dir():
        return set()
    return {path.name.split("_")[0].upper() for path in COVERS_DIR.glob("*.webp")}


def _next_actions(blockers: List[str], paid: int, missing_checkout: int) -> List[str]:
    actions: List[str] = []
    if "checkout" in blockers:
        actions.append(CHECKOUT_ACTION.format(paid=paid, missing=missing_checkout))
    if "site" in blockers:
        actions.append(
            "Exportar el sitio publicable: POST /api/publish/export-site "
            "(o .\\.venv\\Scripts\\python.exe scripts\\build_publish_pack.py --base-url https://tu-dominio)."
        )
    if "deliverables" in blockers:
        actions.append("Generar los entregables faltantes: POST /api/catalog/{sku_id}/generate-deliverable.")
    if "art" in blockers:
        actions.append("Generar las portadas faltantes en data/product_art/web/covers (POST /api/customizations/vertex-generate).")
    if "vertex" in blockers:
        actions.append("Configurar ADC de Google Cloud (gcloud auth application-default login) y GOOGLE_CLOUD_PROJECT/VERTEX_LOCATION.")
    if "routes" in blockers:
        actions.append("Corregir el catálogo: cada SKU debe tener una bridge_route única (/blueprint, /boveda, /app, /sistema, /vault, /gratis).")
    if "content" in blockers:
        actions.append("Sembrar la cola de contenido en data/social_feeds.json (posts de Threads y pines propios).")
    if not actions:
        actions.append("Todo listo: exporta el sitio, pega los checkouts y publica la cola a mano (el sistema no publica solo).")
    return actions


def compute_readiness() -> Dict[str, Any]:
    items = load_or_init_catalog()
    paid = [item for item in items if item.price_usd > 0]
    leads = [item for item in items if item.price_usd == 0]
    missing_deliverables = [
        item.sku_id
        for item in items
        if not (DELIVERABLES_DIR / f"{item.sku_id.lower()}_{item.slug}.html").is_file()
    ]
    cover_skus = _cover_skus()
    cover_files = len(list(COVERS_DIR.glob("*.webp"))) if COVERS_DIR.is_dir() else 0
    missing_covers = [item.sku_id for item in items if item.sku_id.upper() not in cover_skus]
    routes = [item.bridge_route for item in items]
    unique_routes = len(set(routes))
    gumroad = [item for item in paid if item.gumroad_url]
    hotmart = [item for item in paid if item.hotmart_url]
    with_checkout = [item for item in paid if item.gumroad_url or item.hotmart_url]
    missing_checkout = [item.sku_id for item in paid if not (item.gumroad_url or item.hotmart_url)]
    feeds = load_or_init_feeds()
    threads = feeds["threads"]
    pins = [pin for pin in feeds["pinterest"] if not pin.is_competitor_benchmark]
    vertex = vertex_status()
    vertex_ok = bool(vertex.get("adc_present")) and bool(vertex.get("project_id"))
    site_exists = MANIFEST_PATH.is_file()

    checks = [
        {
            "id": "deliverables",
            "label": "Entregables en disco",
            "ok": not missing_deliverables,
            "detail": f"{len(items) - len(missing_deliverables)}/{len(items)} archivos en data/deliverables"
            + (f". Faltan: {', '.join(missing_deliverables[:8])}" if missing_deliverables else ""),
        },
        {
            "id": "checkout",
            "label": "Checkout real por SKU",
            "ok": not missing_checkout,
            "detail": f"{len(with_checkout)}/{len(paid)} SKUs de pago con checkout "
            f"(Gumroad {len(gumroad)}, Hotmart {len(hotmart)}). "
            f"Faltan {len(missing_checkout)}: {', '.join(missing_checkout[:8])}"
            + ("..." if len(missing_checkout) > 8 else ""),
        },
        {
            "id": "vertex",
            "label": "Vertex AI configurado",
            "ok": vertex_ok,
            "detail": f"proyecto {vertex.get('project_id')} · {vertex.get('location')} · "
            f"{vertex.get('primary_model')} (fallback {vertex.get('fallback_model')}) · "
            f"ADC {'presente' if vertex.get('adc_present') else 'ausente'} · "
            f"semilla Ron {'presente' if vertex.get('seed_present') else 'ausente'}",
        },
        {
            "id": "art",
            "label": "Portadas de arte en disco",
            "ok": not missing_covers,
            "detail": f"{len(items) - len(missing_covers)}/{len(items)} portadas "
            f"({cover_files} archivos webp en data/product_art/web/covers)",
        },
        {
            "id": "routes",
            "label": "Rutas puente únicas",
            "ok": unique_routes == len(items) and len(items) == EXPECTED_SKUS,
            "detail": f"{unique_routes} rutas únicas para {len(items)} SKUs "
            f"(se esperan {EXPECTED_SKUS} rutas y {EXPECTED_SKUS} SKUs)",
        },
        {
            "id": "content",
            "label": "Cola de contenido Threads/Pinterest",
            "ok": len(threads) >= MIN_THREADS and len(pins) >= MIN_PINS,
            "detail": f"{len(threads)} posts en Threads · {len(pins)} pines propios en Pinterest "
            f"(benchmarks de competencia excluidos)",
        },
        {
            "id": "site",
            "label": "Sitio estático exportado",
            "ok": site_exists,
            "detail": "data/publish_site/manifest.json existe"
            if site_exists
            else "Falta data/publish_site/manifest.json: ejecuta POST /api/publish/export-site",
        },
    ]
    blockers = [check["id"] for check in checks if not check["ok"]]
    counts = {
        "skus": len(items),
        "paid": len(paid),
        "leads": len(leads),
        "checkouts": len(with_checkout),
        "checkouts_gumroad": len(gumroad),
        "checkouts_hotmart": len(hotmart),
        "skus_missing_checkout": len(missing_checkout),
        "skus_missing_checkout_ids": missing_checkout,
        "threads": len(threads),
        "pins": len(pins),
        "art_covers": len(items) - len(missing_covers),
        "art_cover_files": cover_files,
        "deliverables": len(items) - len(missing_deliverables),
    }
    return {
        "ready": not blockers,
        "checks": checks,
        "blockers": blockers,
        "counts": counts,
        "next_actions": _next_actions(blockers, len(paid), len(missing_checkout)),
    }
