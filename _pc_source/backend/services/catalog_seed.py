from typing import Any, Callable, List, Optional
from backend.config import CATALOG_JSON_PATH, ensure_dirs
from backend.models.catalog_models import ProductSKU
from backend.services.catalog_data import BOVEDA_SPECS, EBOOK_SPECS, MICRO_APP_SPECS
from backend.services.json_store import (
    lock_for,
    quarantine_corrupt,
    read_json,
    write_json_atomic,
)

COP_RATE = 4200


def _usd_to_cop(usd: float) -> int:
    if usd <= 0:
        return 0
    raw = int(round(usd * COP_RATE, -2))
    return raw


def build_default_catalog() -> List[ProductSKU]:
    skus: List[ProductSKU] = []

    # 1. 12 Ebooks Blueprint
    for sku_id, slug, title, sub, niche, usd, hook, spec, feat in EBOOK_SPECS:
        skus.append(
            ProductSKU(
                sku_id=sku_id,
                slug=slug,
                title=title,
                subtitle=sub,
                format="ebook_blueprint",
                niche=niche,  # type: ignore[arg-type]
                price_usd=usd,
                price_cop=_usd_to_cop(usd),
                bridge_route=f"/blueprint/{slug}",
                hook_angle=hook,
                deliverable_spec=spec,
                featured_on_stan=feat,
            )
        )

    # 2. 12 Bóvedas / Arsenales
    for sku_id, slug, title, sub, niche, usd, hook, spec in BOVEDA_SPECS:
        skus.append(
            ProductSKU(
                sku_id=sku_id,
                slug=slug,
                title=title,
                subtitle=sub,
                format="boveda_arsenal",
                niche=niche,  # type: ignore[arg-type]
                price_usd=usd,
                price_cop=_usd_to_cop(usd),
                bridge_route=f"/boveda/{slug}",
                hook_angle=hook,
                deliverable_spec=spec,
                featured_on_stan=(sku_id in {"B01", "B05"}),
            )
        )

    # 3. 12 Micro-Apps HTML Offline
    for sku_id, slug, title, sub, niche, usd, hook, spec, feat in MICRO_APP_SPECS:
        skus.append(
            ProductSKU(
                sku_id=sku_id,
                slug=slug,
                title=title,
                subtitle=sub,
                format="micro_app_html",
                niche=niche,  # type: ignore[arg-type]
                price_usd=usd,
                price_cop=_usd_to_cop(usd),
                bridge_route=f"/app/{slug}",
                hook_angle=hook,
                deliverable_spec=spec,
                featured_on_stan=feat,
            )
        )

    # 4. 10 Kits Combinados (Ebook + Bóveda + Micro-App HTML)
    for idx in range(10):
        eb = EBOOK_SPECS[idx]
        bv = BOVEDA_SPECS[idx]
        ap = MICRO_APP_SPECS[idx]
        kit_id = f"K{idx + 1:02d}"
        slug = f"kit-sistema-{eb[1]}"
        kit_usd = 49.0 if idx in (0, 4, 7) else 39.0
        skus.append(
            ProductSKU(
                sku_id=kit_id,
                slug=slug,
                title=f"Sistema Completo #{idx + 1}: {eb[2]} + Bóveda + App HTML",
                subtitle=f"Incluye el Blueprint ({eb[0]}), la Bóveda ({bv[0]}) y la Micro-App interactiva ({ap[0]})",
                format="kit_sistema",
                niche=eb[4],  # type: ignore[arg-type]
                price_usd=kit_usd,
                price_cop=_usd_to_cop(kit_usd),
                bridge_route=f"/sistema/{slug}",
                hook_angle=f"El pack de ejecución completo: {eb[6]}",
                deliverable_spec=f"ZIP con Ebook PDF ({eb[0]}) + Bóveda ({bv[0]}) + App HTML ({ap[0]})",
                featured_on_stan=(idx == 0),
            )
        )

    # 5. 6 Mega-Bundles (52 SKUs de pago en total)
    bundles = [
        ("M01", "bundle-imperio-faceless", "Mega-Bundle Imperio Faceless (12 Activos: Ebooks + Bóvedas + 4 Apps HTML)", "Todo el arsenal de monetización anónima en Threads y Pinterest", "dinero_digital_faceless", 79.0, True),
        ("M02", "bundle-ia-injusta", "Mega-Bundle IA & Ingeniería Inversa (9 Activos + 3 Apps HTML)", "Todos los sistemas de clonación, prompts de extracción y automatización sin APIs", "ia_automatizacion_injusta", 89.0, True),
        ("M03", "bundle-psicologia-oscura", "Mega-Bundle Psicología Oscura & Atención (9 Activos + 3 Apps HTML)", "El sistema completo de persuasión, precios, hooks y secuestro de atención", "psicologia_oscura_persuasion", 79.0, False),
        ("M04", "bundle-escape-dolar", "Mega-Bundle Escape del 9-a-5 & Arbitraje en USD (6 Activos + 2 Apps HTML)", "Matemáticas cínicas, calculadoras de reemplazo salarial y cobro internacional", "escape_9a5_finanzas_cinicas", 69.0, False),
        ("M05", "suite-12-micro-apps-html", "Ronin ToolSuite — Las 12 Micro-Aplicaciones HTML Interactivas", "Licencia personal de las 12 herramientas web offline de 1 archivo listas para usar en tu navegador", "ia_automatizacion_injusta", 99.0, True),
        ("M06", "ronin-all-access-vault", "THE INSIDER VAULT (All-Access: Los 52 Productos + Actualizaciones)", "Acceso absoluto a los 12 Ebooks, 12 Bóvedas, 12 Micro-Apps HTML y todos los sistemas de Ron Overthinks", "dinero_digital_faceless", 149.0, True),
    ]
    for b_id, slug, title, sub, niche, usd, feat in bundles:
        skus.append(
            ProductSKU(
                sku_id=b_id,
                slug=slug,
                title=title,
                subtitle=sub,
                format="mega_bundle",
                niche=niche,  # type: ignore[arg-type]
                price_usd=usd,
                price_cop=_usd_to_cop(usd),
                bridge_route=f"/vault/{slug}",
                hook_angle="Por qué comprar piezas sueltas cuando puedes instalar la bóveda entera hoy",
                deliverable_spec="Acceso completo a todos los paquetes descargables de la colección",
                featured_on_stan=feat,
            )
        )

    # 6. 3 Lead Magnets estratégicos ($0) para captura en el Clon de Stan Store
    leads = [
        ("L01", "anatomia-post-418-usd", "El Desglose del Experimento de $418.50 (PDF + Mini-Calculadora HTML)", "La anatomía exacta de cómo un archivo corto convierte tráfico frío en ventas", "dinero_digital_faceless"),
        ("L02", "27-hooks-prohibidos", "27 Hooks de Polarización que Paran el Scroll en 1.5 Segundos", "Muestra gratuita extraída de la Bóveda de 500 Hooks Cínicos", "psicologia_oscura_persuasion"),
        ("L03", "prompt-extractor-competencia", "El Meta-Prompt de Ingeniería Inversa (Versión Lite)", "Extrae la oferta y el gancho de cualquier cuenta en 30 segundos", "ia_automatizacion_injusta"),
    ]
    for l_id, slug, title, sub, niche in leads:
        skus.append(
            ProductSKU(
                sku_id=l_id,
                slug=slug,
                title=title,
                subtitle=sub,
                format="lead_magnet",
                niche=niche,  # type: ignore[arg-type]
                price_usd=0.0,
                price_cop=0,
                bridge_route=f"/gratis/{slug}",
                hook_angle="Descarga gratis el anzuelo de entrada antes de que pase a pago",
                deliverable_spec="PDF corto + acceso directo al embudo principal",
                featured_on_stan=True,
            )
        )

    return skus


_LAST_LOAD_ERROR: Optional[str] = None


def get_last_load_error() -> Optional[str]:
    """Motivo legible si el catálogo en disco estaba ilegible y se regeneró."""
    return _LAST_LOAD_ERROR


def _parse_catalog(raw: Any) -> List[ProductSKU]:
    return [ProductSKU(**item) for item in raw]


def load_or_init_catalog() -> List[ProductSKU]:
    """Lee el catálogo. Si está corrupto lo pone en cuarentena y regenera.

    Antes un byte corrupto en catalog.json rompía `/api/catalog` y todas las
    vistas. Ahora se degrada: backup del archivo dañado + catálogo por defecto
    y un `load_warning` legible que la API expone.
    """
    global _LAST_LOAD_ERROR
    ensure_dirs()
    with lock_for(CATALOG_JSON_PATH):
        raw, error = read_json(CATALOG_JSON_PATH)
        if error is None and raw is None:
            catalog = build_default_catalog()
            save_catalog(catalog)
            _LAST_LOAD_ERROR = None
            return catalog
        if error is None:
            try:
                catalog = _parse_catalog(raw)
                _LAST_LOAD_ERROR = None
                return catalog
            except Exception as exc:  # modelo inválido o estructura inesperada
                error = f"{type(exc).__name__}: {exc}"
        backup = quarantine_corrupt(CATALOG_JSON_PATH)
        catalog = build_default_catalog()
        save_catalog(catalog)
        _LAST_LOAD_ERROR = (
            f"catalog.json ilegible ({error}). Se movió a {backup or 'sin backup'} "
            "y se regeneró el catálogo por defecto."
        )
        return catalog


def save_catalog(catalog: List[ProductSKU]) -> None:
    ensure_dirs()
    payload = [item.model_dump() for item in catalog]
    write_json_atomic(CATALOG_JSON_PATH, payload)


def atomic_update_catalog(mutator: Callable[[List[ProductSKU]], Any]) -> Any:
    """Lectura-modificación-escritura serializada sobre catalog.json.

    Dos requests concurrentes (p. ej. dos checkouts) ya no se pisan: el lock se
    toma antes de leer y se libera después de escribir.
    """
    with lock_for(CATALOG_JSON_PATH):
        catalog = load_or_init_catalog()
        result = mutator(catalog)
        save_catalog(catalog)
        return result
