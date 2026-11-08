"""Genera el sitio estático publicable en `data/publish_site/`.

Contrato público: `build_site(base_url: str = "") -> dict`. Devuelve el manifest
y deja en disco:

- `index.html` (tienda de los 55 SKUs) y una carpeta por ruta puente.
- `legal/` (términos, privacidad, reembolsos, licencia) enlazadas desde la
  tienda y desde cada landing.
- `assets/covers/` (portadas reales), `assets/ron/` (avatar/hero si existen),
  `assets/pins/` (imágenes de la cola de Pinterest) y `deliverables/` con SOLO
  los 3 lead magnets públicos; los 52 de pago nunca se copian.
- `content/threads.json`, `content/pinterest.json` y `content/README.md`.
- `sitemap.xml`, `robots.txt`, `404.html` y `manifest.json`.

Sin dependencias externas en el HTML generado. Los pagos no configurados no
muestran botón: se listan como blockers en el manifest.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

from backend.config import DATA_DIR, FEEDS_JSON_PATH, PUBLISH_SITE_DIR
from backend.models.catalog_models import ProductSKU
from backend.services import publish_content as content
from backend.services.catalog_seed import load_or_init_catalog
from backend.services.landing_renderer import checkout_for, render_landing
from backend.services.publish_legal import build_legal_html, build_legal_index

COVERS_SRC = DATA_DIR / "product_art" / "web" / "covers"
WEB_ART_SRC = DATA_DIR / "product_art" / "web"
DELIVERABLES_SRC = DATA_DIR / "deliverables"
PINS_SRC = DATA_DIR / "generated_images"
LEAD_MAGNET_IDS = frozenset({"L01", "L02", "L03"})
RON_FILES = (
    ("stan_store_profile", "profile_avatar_ron.webp"),
    ("stan_store_profile", "stan_hero_ai.webp"),
    ("stan_store_profile", "profile_banner_ron.webp"),
)


def _write(path: Path, text: str) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = text.encode("utf-8")
    path.write_bytes(data)
    return len(data)


def _copy(src: Path, dst: Path) -> int:
    if not src.is_file():
        return 0
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.is_file() and dst.stat().st_size == src.stat().st_size:
        return dst.stat().st_size
    shutil.copyfile(src, dst)
    return dst.stat().st_size


def _url(base_url: str, route: str) -> str:
    """URL de una ruta. La raíz nunca produce `//` cuando base_url está vacía."""
    path = "/" if not route.strip("/") else f"/{route.strip('/')}/"
    base = base_url.rstrip("/")
    return f"{base}{path}" if base else path


def _deliverable_name(sku: ProductSKU) -> str:
    return f"{sku.sku_id.lower()}_{sku.slug}.html"


def _build_sitemap(routes: list[str], legal_routes: list[str], base_url: str) -> str:
    locations = [_url(base_url, "/"), *[_url(base_url, route) for route in routes],
                 *[_url(base_url, route) for route in legal_routes]]
    entries = "".join(f"  <url><loc>{loc}</loc></url>\n" for loc in locations)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{entries}</urlset>\n")


def _build_robots(base_url: str) -> str:
    lines = ["User-agent: *", "Allow: /", ""]
    if base_url.strip():
        lines.insert(2, f"Sitemap: {base_url.rstrip('/')}/sitemap.xml")
    return "\n".join(lines) + "\n"


def _copy_assets(catalog: list[ProductSKU], root: Path) -> dict:
    counters = {"covers": 0, "ron": 0, "pins": 0, "lead_magnets": 0}
    for sku in catalog:
        source = COVERS_SRC / f"{sku.sku_id}_v1.webp"
        counters["covers"] += 1 if _copy(source, root / "assets" / "covers" / source.name) else 0
    for folder, name in RON_FILES:
        counters["ron"] += 1 if _copy(WEB_ART_SRC / folder / name, root / "assets" / "ron" / name) else 0
    for sku in catalog:
        if sku.sku_id.upper() not in LEAD_MAGNET_IDS:
            continue
        source = DELIVERABLES_SRC / _deliverable_name(sku)
        counters["lead_magnets"] += 1 if _copy(source, root / "deliverables" / source.name) else 0
    return counters


def _build_pages(catalog: list[ProductSKU], root: Path, base_url: str) -> list[dict]:
    pages = []
    for sku in catalog:
        route = sku.bridge_route.strip("/")
        download = (
            f"../../deliverables/{_deliverable_name(sku)}"
            if sku.sku_id.upper() in LEAD_MAGNET_IDS
            else ""
        )
        html = render_landing(
            sku,
            checkout_for(sku),
            base_url=base_url,
            assets_href="../../assets",
            legal_root="../../legal/",
            store_href="../../",
            download_href=download,
        )
        size = _write(root / route / "index.html", html)
        pages.append({
            "sku_id": sku.sku_id,
            "route": sku.bridge_route,
            "file": f"{route}/index.html",
            "bytes": size,
            "checkout_ready": bool(sku.gumroad_url or sku.hotmart_url) or sku.price_usd <= 0,
        })
    return pages


def _collect_files(root: Path) -> list[dict]:
    files = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            files.append({"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size})
    return files


def build_site(base_url: str = "") -> dict:
    """Construye el sitio completo y devuelve el manifest (rutas, bytes, blockers)."""
    catalog = load_or_init_catalog()
    root = PUBLISH_SITE_DIR.with_name(PUBLISH_SITE_DIR.name + "_building")
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    assets = _copy_assets(catalog, root)
    pages = _build_pages(catalog, root, base_url)
    routes = [page["route"] for page in pages]
    stamp = content.generated_stamp()

    index_bytes = _write(root / "index.html", content.build_store_html(catalog, stamp))
    legal_routes = []
    for slug, _label in content.LEGAL_PAGES:
        legal_routes.append(f"/legal/{slug}")
        _write(root / "legal" / slug / "index.html", build_legal_html(slug, stamp))
    _write(root / "legal" / "index.html", build_legal_index(stamp))
    _write(root / "404.html", content.build_404_html())

    feeds = {}
    if FEEDS_JSON_PATH.is_file():
        feeds = json.loads(FEEDS_JSON_PATH.read_text(encoding="utf-8"))
    route_by_sku = {sku.sku_id: sku.bridge_route for sku in catalog}
    threads = content.build_threads_content(feeds, route_by_sku)
    pins = content.build_pinterest_content(feeds, route_by_sku)
    content.write_json(root / "content" / "threads.json", threads)
    content.write_json(root / "content" / "pinterest.json", pins)
    for item in pins:
        image = item.get("image")
        if image:
            source = PINS_SRC / Path(image).name
            assets["pins"] += 1 if _copy(source, root / image) else 0
    _write(root / "content" / "README.md",
           content.content_readme(len(threads), len(pins), base_url))

    _write(root / "sitemap.xml", _build_sitemap(routes, legal_routes, base_url))
    _write(root / "robots.txt", _build_robots(base_url))

    paid = [sku for sku in catalog if sku.price_usd > 0]
    ready = [sku for sku in paid if sku.gumroad_url or sku.hotmart_url]
    blockers = [f"checkout:{sku.sku_id}" for sku in paid if not (sku.gumroad_url or sku.hotmart_url)]
    files = _collect_files(root)
    notes = [
        "El sitio incluye las 55 rutas puente y los 4 documentos legales.",
        "Los 52 entregables de pago NO se copian: la entrega real sigue protegida por el backend.",
    ]
    if not base_url.strip():
        notes.append("Sin base_url: canonical, OG y sitemap quedan en rutas relativas. "
                     "Usa --base-url https://tu-dominio para URLs absolutas.")
    manifest = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "base_url": base_url,
        "site_dir": "data/publish_site",
        "skus": len(catalog),
        "paid_skus": len(paid),
        "lead_magnets": len(catalog) - len(paid),
        "routes": routes,
        "legal_routes": legal_routes,
        "pages": pages,
        "index": {"file": "index.html", "bytes": index_bytes},
        "files": len(files),
        "file_list": files,
        "total_bytes": sum(item["bytes"] for item in files),
        "assets": assets,
        "content": {"threads": len(threads), "pinterest": len(pins)},
        "checkout_ready": len(ready),
        "blockers": blockers,
        "notes": notes,
    }
    _write(root / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))

    if PUBLISH_SITE_DIR.exists():
        shutil.rmtree(PUBLISH_SITE_DIR)
    root.replace(PUBLISH_SITE_DIR)
    manifest["manifest_path"] = str(PUBLISH_SITE_DIR / "manifest.json")
    return manifest
