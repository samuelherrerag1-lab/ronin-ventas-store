"""CLI: construye el sitio estático publicable e imprime su manifest.

Uso:
    .\\.venv\\Scripts\\python.exe scripts\\build_publish_pack.py
    .\\.venv\\Scripts\\python.exe scripts\\build_publish_pack.py --base-url https://mi-dominio.com
    .\\.venv\\Scripts\\python.exe scripts\\build_publish_pack.py --base-url https://mi-dominio.com --verify

Exit code 1 si la verificación (`--verify`) falla.
"""

import argparse
import json
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.config import PUBLISH_SITE_DIR  # noqa: E402
from backend.services.publish_pack import build_site  # noqa: E402

EXTERNAL_RESOURCE_RE = re.compile(
    r"""(?isx)
    (?:src|poster)\s*=\s*["']https?://
    | <link\b(?=[^>]*\brel\s*=\s*["'](?:stylesheet|preload|prefetch|icon|manifest|dns-prefetch|preconnect))
      [^>]*\bhref\s*=\s*["']https?://
    | @import\s+(?:url\()?["']?https?://
    | url\(\s*["']?https?://
    """
)


def verify(manifest: dict, site_dir: Path = PUBLISH_SITE_DIR) -> list[str]:
    """Comprueba el sitio en disco. Devuelve la lista de fallos (vacía = PASS)."""
    failures: list[str] = []
    routes = manifest.get("routes") or []
    if len(routes) != 55:
        failures.append(f"rutas: {len(routes)} != 55")
    if not (site_dir / "manifest.json").is_file():
        failures.append("falta manifest.json")
    index = site_dir / "index.html"
    if not index.is_file():
        failures.append("falta index.html")
    elif "<title>" not in index.read_text(encoding="utf-8", errors="ignore"):
        failures.append("index.html sin <title>")
    for route in routes:
        page = site_dir / route.strip("/") / "index.html"
        if not page.is_file():
            failures.append(f"falta {page.relative_to(site_dir).as_posix()}")
            continue
        raw = page.read_text(encoding="utf-8", errors="ignore")
        if not re.search(r"<title[^>]*>\s*\S", raw, re.IGNORECASE):
            failures.append(f"{route} sin <title>")
        if EXTERNAL_RESOURCE_RE.search(raw):
            failures.append(f"{route} carga recurso externo")
        if "legal/" not in raw:
            failures.append(f"{route} sin enlaces legales")
    for legal in manifest.get("legal_routes") or []:
        if not (site_dir / legal.strip("/") / "index.html").is_file():
            failures.append(f"falta legal {legal}")
    if "legal/" not in index.read_text(encoding="utf-8", errors="ignore"):
        failures.append("index.html sin enlaces legales")
    html_files = [path for path in site_dir.rglob("*.html")]
    for page in html_files:
        if EXTERNAL_RESOURCE_RE.search(page.read_text(encoding="utf-8", errors="ignore")):
            failures.append(f"{page.relative_to(site_dir).as_posix()} carga recurso externo")
    deliverable_dir = site_dir / "deliverables"
    if deliverable_dir.is_dir():
        for item in sorted(deliverable_dir.glob("*.html")):
            if not item.name.startswith(("l01_", "l02_", "l03_")):
                failures.append(f"entregable de pago copiado: {item.name}")
    for name in ("l01_", "l02_", "l03_"):
        if not any(item.name.startswith(name) for item in deliverable_dir.glob("*.html")):
            failures.append(f"lead magnet sin copia: {name}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Construye data/publish_site y prueba el manifest")
    parser.add_argument("--base-url", default="", help="Dominio raíz del sitio (opcional)")
    parser.add_argument("--verify", action="store_true", help="Verifica el sitio generado")
    parser.add_argument("--summary", action="store_true", help="Imprime solo el resumen, no el JSON")
    args = parser.parse_args()

    manifest = build_site(base_url=args.base_url)
    print(f"Sitio: {manifest['site_dir']} · {manifest['skus']} SKUs · "
          f"{len(manifest['routes'])} rutas · {manifest['files']} archivos · "
          f"{manifest['total_bytes'] / 1024 / 1024:.2f} MB")
    print(f"Checkout listo: {manifest['checkout_ready']}/{manifest['paid_skus']} · "
          f"blockers: {len(manifest['blockers'])}")
    print(f"Contenido: {manifest['content']['threads']} threads · "
          f"{manifest['content']['pinterest']} pines · assets: {manifest['assets']}")
    if not args.summary:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))

    if args.verify:
        failures = verify(manifest)
        if failures:
            print("\nVERIFY: FAIL")
            for failure in failures:
                print(f" - {failure}")
            return 1
        print("\nVERIFY: PASS · 55 rutas + index + legales + sin recursos externos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
