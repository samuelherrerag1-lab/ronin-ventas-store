"""Fábrica de entregables de respaldo.

Política única de protección (antes había dos umbrales contradictorios:
60 KB aquí y 1.500 bytes en el router):

- Nunca se sobrescribe un archivo existente que sea un entregable válido
  (>= `PROTECT_MIN_BYTES`) ni un lead magnet (L01-L03), sin importar su tamaño.
- `force=True` permite regenerar un entregable normal, pero jamás pisa un lead
  magnet existente.
- El HTML generado se valida antes de escribir: si queda vacío o le falta
  `</html>`/`<title>`, se lanza `ValueError` y el catálogo NO se marca como
  `generated`.
"""

import re
from pathlib import Path
from typing import Any, Dict

from backend.config import DATA_DIR, ensure_dirs
from backend.models.catalog_models import ProductSKU
from backend.services.catalog_seed import load_or_init_catalog, save_catalog
from backend.services.product_templates_elite import render_elite_product_html

DELIVERABLES_DIR = DATA_DIR / "deliverables"

# Un solo umbral para el router, la fábrica y la validación.
MIN_DELIVERABLE_BYTES = 20_000
PROTECT_MIN_BYTES = MIN_DELIVERABLE_BYTES
ELITE_MIN_BYTES = 60_000
LEAD_MAGNET_IDS = frozenset({"L01", "L02", "L03"})
REQUIRED_MARKERS = ("<!doctype html", "</html>", "<title")
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def ensure_deliverables_dir() -> Path:
    ensure_dirs()
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    return DELIVERABLES_DIR


def deliverable_filename(sku: ProductSKU) -> str:
    """Nombre canónico: <sku_id en minúsculas>_<slug>.html."""
    slug = (sku.slug or "").strip()
    if not SLUG_PATTERN.match(slug):
        raise ValueError(f"Slug inválido para {sku.sku_id}: {sku.slug!r}")
    return f"{sku.sku_id.lower()}_{slug}.html"


def deliverable_path(sku: ProductSKU) -> Path:
    return DELIVERABLES_DIR / deliverable_filename(sku)


def is_protected_deliverable(path: Path, sku_id: str = "") -> bool:
    """Guardián único: lead magnets siempre; el resto por tamaño mínimo válido."""
    if not path.is_file():
        return False
    if sku_id.upper() in LEAD_MAGNET_IDS:
        return True
    try:
        return path.stat().st_size >= PROTECT_MIN_BYTES
    except OSError:
        return True


def validate_generated_html(html_content: str) -> None:
    raw = html_content or ""
    size = len(raw.encode("utf-8"))
    if size < MIN_DELIVERABLE_BYTES:
        raise ValueError(
            f"HTML generado demasiado pequeño: {size} bytes < {MIN_DELIVERABLE_BYTES}"
        )
    lowered = raw.lower()
    missing = [marker for marker in REQUIRED_MARKERS if marker not in lowered]
    if missing:
        raise ValueError(f"HTML generado incompleto, faltan marcadores: {missing}")
    if not re.search(r"<title[^>]*>\s*\S", raw, re.IGNORECASE):
        raise ValueError("HTML generado sin <title> con contenido")


def _write_atomic(path: Path, content: str) -> None:
    tmp_path = path.with_name(path.name + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(path)


def _result(target: ProductSKU, filename: str, out_path: Path, source: str) -> Dict[str, Any]:
    file_size = out_path.stat().st_size if out_path.is_file() else 0
    return {
        "sku_id": target.sku_id,
        "status": "generated",
        "filename": filename,
        "deliverable_url": f"/deliverables/{filename}",
        "bytes": file_size,
        "is_elite_deliverable": file_size > ELITE_MIN_BYTES,
        "source": source,
        "preserved_existing": source != "generated",
    }


def generate_deliverable_for_sku(sku_id: str, force: bool = False) -> Dict[str, Any]:
    """Genera (o preserva) el entregable de respaldo de un SKU."""
    ensure_deliverables_dir()
    catalog = load_or_init_catalog()
    target = next((item for item in catalog if item.sku_id == sku_id), None)
    if not target:
        raise ValueError(f"SKU {sku_id} no existe en el catálogo")

    filename = deliverable_filename(target)
    out_path = DELIVERABLES_DIR / filename
    is_lead_magnet = target.sku_id.upper() in LEAD_MAGNET_IDS
    protected = is_protected_deliverable(out_path, target.sku_id)

    if is_lead_magnet and out_path.is_file():
        return _result(target, filename, out_path, "preserved_lead_magnet")
    if protected and not force:
        return _result(target, filename, out_path, "preserved_existing")

    html_content = render_elite_product_html(target)
    validate_generated_html(html_content)  # si falla, no se marca generated
    _write_atomic(out_path, html_content)

    target.status = "generated"
    save_catalog(catalog)
    return _result(target, filename, out_path, "generated")


def generate_all_micro_apps(force: bool = False) -> Dict[str, Any]:
    """Regenera solo lo que falte o sea inválido; conserva lo existente."""
    catalog = load_or_init_catalog()
    generated, preserved = [], []
    for item in catalog:
        res = generate_deliverable_for_sku(item.sku_id, force=force)
        if res["source"] == "generated":
            generated.append(res["sku_id"])
        else:
            preserved.append(res["sku_id"])
    return {
        "generated_count": len(generated),
        "preserved_count": len(preserved),
        "sku_ids": generated,
        "preserved_sku_ids": preserved,
    }
