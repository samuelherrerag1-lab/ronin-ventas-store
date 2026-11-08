"""Catálogo de los 55 SKUs, entregables y checkout real por SKU.

El checkout es una URL https pegada por el operador y validada aquí (esquema,
host permitido y longitud). Sin URL no hay botón de pago: la landing lo dice.
"""

import os
import urllib.parse
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.catalog_seed import (
    atomic_update_catalog,
    get_last_load_error,
    load_or_init_catalog,
)
from backend.services.product_factory import (
    DELIVERABLES_DIR,
    ensure_deliverables_dir,
    generate_deliverable_for_sku,
)

router = APIRouter(prefix="/api/catalog", tags=["catalog"])

# Un entregable existente por debajo de esto se considera inválido y se regenera.
MIN_EXISTING_DELIVERABLE_BYTES = 20_000
DEFAULT_CHECKOUT_HOSTS = ("gumroad.com", "hotmart.com")


def allowed_checkout_hosts() -> List[str]:
    raw = os.environ.get("CHECKOUT_ALLOWED_HOSTS", "").strip()
    extra = [host.strip().lower() for host in raw.split(",") if host.strip()]
    return list(DEFAULT_CHECKOUT_HOSTS) + extra


def validate_checkout_url(raw: Optional[str], field_name: str) -> Optional[str]:
    """Normaliza una URL de checkout. `None` = no se envió; "" = borrar."""
    if raw is None:
        return None
    value = str(raw).strip()
    if not value:
        return ""
    if len(value) > 500:
        raise ValueError(f"{field_name}: URL demasiado larga (máximo 500 caracteres)")
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme != "https":
        raise ValueError(f"{field_name}: debe usar https:// (recibido: '{parsed.scheme or 'sin esquema'}')")
    host = (parsed.hostname or "").lower()
    if not host:
        raise ValueError(f"{field_name}: la URL no tiene host válido")
    if parsed.username or parsed.password:
        raise ValueError(f"{field_name}: no se permiten credenciales embebidas en la URL")
    allowed = allowed_checkout_hosts()
    if not any(host == candidate or host.endswith(f".{candidate}") for candidate in allowed):
        raise ValueError(f"{field_name}: host no permitido ('{host}'). Permitidos: {', '.join(allowed)}")
    return value


class CheckoutLinks(BaseModel):
    gumroad_url: Optional[str] = None
    hotmart_url: Optional[str] = None


class BulkCheckoutPayload(BaseModel):
    links: Dict[str, CheckoutLinks] = Field(default_factory=dict)


def _item_payload(item: Any) -> Dict[str, Any]:
    return {**item.model_dump(), "checkout_ready": bool(item.checkout_ready)}


def _deliverable_path(item: Any):
    return DELIVERABLES_DIR / f"{item.sku_id.lower()}_{item.slug}.html"


@router.get("")
def get_catalog(format_filter: Optional[str] = None, niche_filter: Optional[str] = None):
    ensure_deliverables_dir()
    all_items = load_or_init_catalog()
    # `generated` se deriva del disco SOLO en memoria: un GET no escribe.
    for item in all_items:
        if _deliverable_path(item).is_file():
            item.status = "generated"

    items = all_items
    if format_filter and format_filter != "all":
        items = [item for item in items if item.format == format_filter]
    if niche_filter and niche_filter != "all":
        items = [item for item in items if item.niche == niche_filter]

    paid_items = [item for item in all_items if item.price_usd > 0]
    lead_items = [item for item in all_items if item.price_usd == 0]
    return {
        "total_skus": len(all_items),
        "paid_skus": len(paid_items),
        "lead_magnets": len(lead_items),
        "unique_bridge_routes": len({item.bridge_route for item in all_items}),
        "checkout_ready_count": sum(1 for item in paid_items if item.checkout_ready),
        "items": [_item_payload(item) for item in items],
        "load_warning": get_last_load_error(),
    }


@router.post("/checkout-bulk")
def set_bulk_checkout(payload: BulkCheckoutPayload):
    """Pega muchas URLs de checkout en una sola llamada y persiste una vez."""
    if not payload.links:
        raise HTTPException(status_code=422, detail="links no puede estar vacío")
    prepared: Dict[str, Dict[str, str]] = {}
    errors: List[Dict[str, str]] = []
    for sku_id, links in payload.links.items():
        if not links.model_fields_set:
            errors.append({"sku_id": sku_id, "reason": "envía gumroad_url y/o hotmart_url"})
            continue
        try:
            values: Dict[str, str] = {}
            if "gumroad_url" in links.model_fields_set:
                values["gumroad_url"] = validate_checkout_url(links.gumroad_url, "gumroad_url") or ""
            if "hotmart_url" in links.model_fields_set:
                values["hotmart_url"] = validate_checkout_url(links.hotmart_url, "hotmart_url") or ""
        except ValueError as exc:
            errors.append({"sku_id": sku_id, "reason": str(exc)})
            continue
        prepared[sku_id] = values

    def mutate(catalog: List[Any]) -> int:
        by_id = {item.sku_id: item for item in catalog}
        updated = 0
        for sku_id, values in prepared.items():
            target = by_id.get(sku_id)
            if target is None:
                errors.append({"sku_id": sku_id, "reason": "SKU no existe en el catálogo"})
                continue
            for field, value in values.items():
                setattr(target, field, value)
            updated += 1
        return updated

    updated = atomic_update_catalog(mutate)
    catalog = load_or_init_catalog()
    return {
        "updated": updated,
        "skipped": len(errors),
        "errors": errors,
        "checkout_ready_count": sum(1 for item in catalog if item.checkout_ready),
        "paid_skus": sum(1 for item in catalog if item.price_usd > 0),
        "note": "URLs validadas (https + host permitido) y persistidas en data/catalog.json.",
    }


@router.post("/{sku_id}/checkout")
def set_sku_checkout(sku_id: str, payload: CheckoutLinks):
    """Configura el checkout de un SKU. Cadena vacía borra el campo."""
    if not payload.model_fields_set:
        raise HTTPException(
            status_code=422,
            detail="Envía gumroad_url y/o hotmart_url (cadena vacía borra el campo).",
        )
    try:
        gumroad = (
            validate_checkout_url(payload.gumroad_url, "gumroad_url")
            if "gumroad_url" in payload.model_fields_set
            else None
        )
        hotmart = (
            validate_checkout_url(payload.hotmart_url, "hotmart_url")
            if "hotmart_url" in payload.model_fields_set
            else None
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    def mutate(catalog: List[Any]) -> Any:
        target = next((item for item in catalog if item.sku_id == sku_id), None)
        if target is None:
            raise KeyError(sku_id)
        if gumroad is not None:
            target.gumroad_url = gumroad
        if hotmart is not None:
            target.hotmart_url = hotmart
        return target

    try:
        target = atomic_update_catalog(mutate)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"SKU {sku_id} no encontrado") from exc
    return {
        **_item_payload(target),
        "note": "Checkout persistido en data/catalog.json. La landing del SKU ya lo usa.",
    }


@router.post("/{sku_id}/toggle-stan")
def toggle_stan_featured(sku_id: str):
    def mutate(catalog: List[Any]) -> Any:
        target = next((item for item in catalog if item.sku_id == sku_id), None)
        if target is None:
            raise KeyError(sku_id)
        target.featured_on_stan = not target.featured_on_stan
        return target

    try:
        target = atomic_update_catalog(mutate)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"SKU {sku_id} no encontrado") from exc
    return _item_payload(target)


@router.post("/{sku_id}/generate-deliverable")
def api_generate_sku_deliverable(sku_id: str):
    ensure_deliverables_dir()
    catalog = load_or_init_catalog()
    target = next((item for item in catalog if item.sku_id == sku_id), None)
    if not target:
        raise HTTPException(status_code=404, detail=f"SKU {sku_id} no encontrado")

    expected_path = _deliverable_path(target)
    if expected_path.is_file() and expected_path.stat().st_size >= MIN_EXISTING_DELIVERABLE_BYTES:
        target.status = "generated"
        return {
            "sku_id": target.sku_id,
            "status": "generated",
            "filename": expected_path.name,
            "deliverable_url": f"/deliverables/{expected_path.name}",
            "bytes": expected_path.stat().st_size,
            "engine": "opencode_deepseek_flagship",
        }

    try:
        return generate_deliverable_for_sku(sku_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
