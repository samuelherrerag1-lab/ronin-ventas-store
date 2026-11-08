"""Datos del catálogo que necesita el alta en Gumroad: archivo, portada, textos y estado.

No escribe `data/catalog.json` a mano: usa `catalog_seed.atomic_update_catalog`.
"""

import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.config import CATALOG_JSON_PATH, DATA_DIR
from backend.services.catalog_seed import atomic_update_catalog
from backend.services.json_store import lock_for, read_json, write_json_atomic

STATE_PATH = DATA_DIR / "gumroad_products.json"
DELIVERABLES_DIR = DATA_DIR / "deliverables"
COVERS_DIR = DATA_DIR / "product_art" / "web" / "covers"
FLAGSHIP_SKUS = ("E01", "B01", "A01", "K01", "M06")

NICHE_LABEL = {
    "dinero_digital_faceless": "Dinero digital faceless",
    "ia_automatizacion_injusta": "IA y automatización injusta",
    "psicologia_oscura_persuasion": "Psicología oscura y atención",
    "escape_9a5_finanzas_cinicas": "Escape del 9 a 5 y finanzas cínicas",
}
FORMAT_LABEL = {
    "ebook_blueprint": "Ebook interactivo en HTML (se abre en el navegador, sin conexión)",
    "boveda_arsenal": "Bóveda/arsenal en HTML interactivo (se abre en el navegador, sin conexión)",
    "micro_app_html": "Micro-aplicación HTML de un archivo (funciona offline en el navegador)",
    "kit_sistema": "Kit completo: ebook + bóveda + micro-app HTML",
    "mega_bundle": "Mega-bundle con varios activos digitales descargables",
}


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def deliverable_path(sku_id: str, slug: str) -> Path:
    return DELIVERABLES_DIR / f"{sku_id.lower()}_{slug}.html"


def cover_path(sku_id: str) -> Path:
    return COVERS_DIR / f"{sku_id}_v1.webp"


def price_cents(price_usd: float) -> int:
    return int(round(float(price_usd) * 100))


def _escape(text: str) -> str:
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_description(sku: Dict[str, Any]) -> str:
    """Qué es, qué incluye y cómo se entrega. Sin promesas de ingresos."""
    title = _escape(sku.get("title", ""))
    subtitle = _escape(sku.get("subtitle", ""))
    hook = _escape(sku.get("hook_angle", ""))
    spec = _escape(sku.get("deliverable_spec", ""))
    niche = NICHE_LABEL.get(sku.get("niche", ""), "Sistemas digitales")
    fmt = FORMAT_LABEL.get(sku.get("format", ""), "Activo digital descargable")
    return (
        f"<p><strong>{title}</strong></p>"
        f"<p>{subtitle}</p>"
        f"<p>{hook}</p>"
        f"<p><strong>Qué incluye</strong><br>{fmt}. {spec}</p>"
        f"<p><strong>Nicho</strong>: {niche}</p>"
        "<p><strong>Cómo se entrega</strong><br>Descarga inmediata tras la compra. "
        "El archivo HTML se abre en cualquier navegador moderno y funciona sin conexión a internet.</p>"
        "<p><strong>Nota honesta</strong><br>Material educativo y de ejecución. "
        "No garantiza ingresos, resultados ni ventas: depende de cómo lo apliques.</p>"
    )


def tags_for(sku: Dict[str, Any]) -> List[str]:
    tags = ["ronin", "ronoverthinks", "digital"]
    fmt, niche = sku.get("format", ""), sku.get("niche", "")
    tags.append(
        "ebook" if "ebook" in fmt else
        "boveda" if "boveda" in fmt else
        "micro-app" if "micro_app" in fmt else
        "kit" if "kit" in fmt else
        "bundle"
    )
    tags.append(
        "dinero-digital" if "dinero" in niche else
        "ia-automatizacion" if "ia" in niche else
        "psicologia" if "psicologia" in niche else
        "finanzas"
    )
    return tags


def load_catalog() -> List[Dict[str, Any]]:
    data, error = read_json(CATALOG_JSON_PATH)
    return data if not error and isinstance(data, list) else []


def paid_skus(catalog: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    catalog = catalog if catalog is not None else load_catalog()
    return [sku for sku in catalog if sku.get("format") != "lead_magnet"]


def missing_files(skus: List[Dict[str, Any]]) -> List[str]:
    out = []
    for sku in skus:
        if not deliverable_path(sku["sku_id"], sku["slug"]).is_file():
            out.append(sku["sku_id"])
    return out


# -- estado local del alta ---------------------------------------------------
def load_state() -> Dict[str, Any]:
    data, error = read_json(STATE_PATH)
    if error or not isinstance(data, dict):
        return {"account": {}, "products": {}, "updated_at": None}
    data.setdefault("products", {})
    data.setdefault("account", {})
    return data


def save_state(state: Dict[str, Any]) -> None:
    with lock_for(STATE_PATH):
        state["updated_at"] = utc_now()
        write_json_atomic(STATE_PATH, state)


def product_entry(state: Dict[str, Any], sku_id: str) -> Dict[str, Any]:
    products = state.get("products")
    if not isinstance(products, dict):
        products = {}
        state["products"] = products
    return products.setdefault(sku_id, {})


def summarize(state: Dict[str, Any]) -> Dict[str, Any]:
    products = state.get("products") or {}
    real = [p for p in products.values() if p.get("product_id")]
    return {
        "account": state.get("account") or {},
        "tracked_skus": len(products),
        "created": len(real),
        "with_file": sum(1 for p in real if p.get("file_attached")),
        "with_cover": sum(1 for p in real if p.get("cover_attached")),
        "published": sum(1 for p in real if p.get("published")),
        "blocked_quota": sum(1 for p in products.values() if p.get("status") == "blocked_quota"),
        "updated_at": state.get("updated_at"),
    }


def apply_urls_to_catalog(state: Dict[str, Any], published_only: bool = True) -> Dict[str, Any]:
    """Persiste checkout URLs verificables en catalog.json vía catalog_seed.

    Por defecto solo escribe SKUs publicados: un producto en borrador no es
    comprable y publicarlo como checkout sería un estado falso. Con
    `published_only=False` se guardan también los borradores.
    """
    products = state.get("products") or {}
    applied, skipped, published_ids = 0, 0, []

    def mutate(catalog):
        nonlocal applied, skipped
        for sku in catalog:
            entry = products.get(sku.sku_id) or {}
            url = entry.get("gumroad_url") or ""
            if not url:
                continue
            if published_only and not entry.get("published"):
                skipped += 1
                continue
            sku.gumroad_url = url
            if entry.get("published"):
                sku.status = "published"
                published_ids.append(sku.sku_id)
            applied += 1

    atomic_update_catalog(mutate)
    return {"applied": applied, "skipped_drafts": skipped, "published": len(published_ids)}


def verify_stored_urls(state: Dict[str, Any], only_published: bool = True) -> List[Dict[str, Any]]:
    """Comprueba con GET público (sin token) las URLs de los productos publicados."""
    import re

    import requests

    results = []
    for sku_id, entry in sorted((state.get("products") or {}).items()):
        url = entry.get("gumroad_url")
        if not url:
            continue
        section: Dict[str, Any] = {"sku_id": sku_id, "url": url, "published": bool(entry.get("published"))}
        if only_published and not entry.get("published"):
            results.append(section)
            continue
        try:
            response = requests.get(url, timeout=30, allow_redirects=True, headers={"User-Agent": "RoninVentasOS/2.0"})
            html = response.text or ""
            title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
            price_match = re.search(r'"(?:formatted_price|price)"\s*:\s*"?(?P<p>[^",}]+)', html)
            section.update(
                {
                    "ok": response.status_code == 200,
                    "status": response.status_code,
                    "final_url": response.url,
                    "title": re.sub(r"\s+", " ", title_match.group(1)).strip()[:200] if title_match else "",
                    "price": (price_match.group("p").strip()[:40] if price_match else ""),
                }
            )
        except Exception as exc:  # pragma: no cover - depende de la red
            section.update({"ok": False, "error": f"{type(exc).__name__}: {exc}"})
        results.append(section)
    return results
