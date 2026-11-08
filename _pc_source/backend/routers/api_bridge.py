"""Rutas puente: /blueprint/..., /boveda/..., /app/..., /sistema/..., /vault/..., /gratis/...

Antes no existían: todas devolvían el dashboard. Ahora cada una sirve una
landing real del SKU, con su precio y su checkout (o el aviso de que falta).
Las rutas son explícitas para no interceptar /api/*.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from backend.services.catalog_seed import load_or_init_catalog
from backend.services.landing_renderer import checkout_for, render_landing

router = APIRouter(tags=["bridge"])


@router.get("/blueprint/{slug}", response_class=HTMLResponse)
@router.get("/boveda/{slug}", response_class=HTMLResponse)
@router.get("/app/{slug}", response_class=HTMLResponse)
@router.get("/sistema/{slug}", response_class=HTMLResponse)
@router.get("/vault/{slug}", response_class=HTMLResponse)
@router.get("/gratis/{slug}", response_class=HTMLResponse)
def bridge_landing(slug: str, request: Request):
    prefix = request.url.path.strip("/").split("/")[0]
    catalog = load_or_init_catalog()
    sku = next((item for item in catalog if item.slug == slug), None)
    if sku is None:
        raise HTTPException(status_code=404, detail=f"SKU no encontrado: {slug}")
    if sku.bridge_route != f"/{prefix}/{slug}":
        raise HTTPException(status_code=404, detail=f"Ruta incorrecta. Usa {sku.bridge_route}")
    return HTMLResponse(render_landing(sku, checkout_for(sku)))
