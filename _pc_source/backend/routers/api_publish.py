"""API de publicación: readiness, kit de contenido, marcado local y export.

Ningún endpoint de este router publica en Threads ni en Pinterest: `mark` guarda
seguimiento LOCAL y `export-site` delega en `backend.services.publish_pack`
(generador de sitio estático, implementado por el task de generadores).
"""

import importlib
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from backend.config import DATA_DIR
from backend.services.catalog_seed import load_or_init_catalog
from backend.services.json_store import read_json
from backend.services.publish_state import (
    LOCAL_ONLY_NOTE,
    compute_readiness,
    manifest_path,
    mark_item,
    status_map,
)
from backend.services.social_feed_seed import load_or_init_feeds

router = APIRouter(prefix="/api/publish", tags=["publish"])

GENERATED_IMAGES_DIR = DATA_DIR / "generated_images"


class MarkRequest(BaseModel):
    platform: Literal["threads", "pinterest"]
    item_id: str = Field(min_length=1, max_length=64)
    status: Literal["queued", "published"]


def _absolute(base_url: str, path: str) -> str:
    if not path:
        return ""
    if path.startswith(("http://", "https://")):
        return path
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def _image_url(base_url: str, relative: Optional[str]) -> Optional[str]:
    """URL absoluta solo si la imagen existe en disco (nada de imágenes 404)."""
    if not relative:
        return None
    if not (DATA_DIR / relative.lstrip("/")).is_file():
        return None
    return _absolute(base_url, relative)


def _thread_text(post: Any) -> str:
    return "\n\n".join(slide for slide in post.body_slides if slide).strip()


def _pin_text(pin: Any) -> str:
    parts = (pin.overlay_headline, pin.seo_title, pin.seo_description)
    return "\n\n".join(part for part in parts if part).strip()


def _kit_items(base_url: str, platform: str, limit: int) -> List[Dict[str, Any]]:
    feeds = load_or_init_feeds()
    statuses = status_map(platform)
    routes = {item.sku_id: item.bridge_route for item in load_or_init_catalog()}
    items: List[Dict[str, Any]] = []

    if platform == "threads":
        for post in feeds["threads"][:limit]:
            items.append(
                {
                    "id": post.post_id,
                    "platform": "threads",
                    "text": _thread_text(post),
                    "image_url": None,
                    "target_route": _absolute(base_url, routes.get(post.target_sku_id, "")),
                    "target_sku_id": post.target_sku_id,
                    "status": statuses.get(post.post_id, "queued"),
                }
            )
        return items

    for pin in feeds["pinterest"]:
        if pin.is_competitor_benchmark:
            continue
        if len(items) >= limit:
            break
        items.append(
            {
                "id": pin.pin_id,
                "platform": "pinterest",
                "text": _pin_text(pin),
                "image_url": _image_url(base_url, pin.image_url),
                "target_route": _absolute(base_url, pin.bridge_route),
                "target_sku_id": pin.target_sku_id,
                "status": statuses.get(pin.pin_id, "queued"),
            }
        )
    return items


def _load_publish_pack() -> Any:
    """Import LAZY: el módulo puede no existir todavía (otro task lo crea)."""
    return importlib.import_module("backend.services.publish_pack")


@router.get("/readiness")
def publish_readiness() -> Dict[str, Any]:
    return compute_readiness()


@router.get("/kit")
def publish_kit(
    request: Request,
    platform: Literal["threads", "pinterest"] = Query(...),
    limit: int = Query(50, ge=1, le=200),
) -> Dict[str, Any]:
    base_url = str(request.base_url)
    items = _kit_items(base_url, platform, limit)
    return {
        "platform": platform,
        "base_url": base_url.rstrip("/"),
        "count": len(items),
        "items": items,
        "tracking": "local",
        "published_to_network": False,
        "note": LOCAL_ONLY_NOTE,
    }


@router.post("/mark")
def publish_mark(payload: MarkRequest) -> Dict[str, Any]:
    feeds = load_or_init_feeds()
    if payload.platform == "threads":
        exists = any(post.post_id == payload.item_id for post in feeds["threads"])
    else:
        exists = any(
            pin.pin_id == payload.item_id and not pin.is_competitor_benchmark
            for pin in feeds["pinterest"]
        )
    if not exists:
        raise HTTPException(
            status_code=404,
            detail=f"Ítem {payload.item_id} no encontrado en {payload.platform}",
        )
    try:
        return mark_item(payload.platform, payload.item_id, payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/export-site")
def export_site(request: Request) -> Dict[str, Any]:
    try:
        module = _load_publish_pack()
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "El generador de sitio estático todavía no existe: falta "
                "backend/services/publish_pack.py con build_site(base_url). "
                f"Detalle: {exc}"
            ),
        ) from exc
    build = getattr(module, "build_site", None)
    if not callable(build):
        raise HTTPException(
            status_code=503,
            detail="backend/services/publish_pack.py existe pero no expone build_site(base_url).",
        )
    base_url = str(request.base_url).rstrip("/")
    try:
        manifest = build(base_url=base_url)
    except Exception as exc:  # noqa: BLE001 - se devuelve la razón literal
        raise HTTPException(
            status_code=500,
            detail=f"build_site(base_url='{base_url}') falló: {type(exc).__name__}: {exc}",
        ) from exc
    return {"status": "ok", "base_url": base_url, "manifest": manifest}


@router.get("/site-manifest")
def site_manifest() -> Dict[str, Any]:
    data, error = read_json(manifest_path())
    if error:
        raise HTTPException(status_code=500, detail=f"manifest.json ilegible: {error}")
    if not isinstance(data, dict):
        raise HTTPException(
            status_code=404,
            detail=(
                "El sitio aún no se ha exportado: falta data/publish_site/manifest.json. "
                "Ejecuta POST /api/publish/export-site."
            ),
        )
    return {"status": "ok", "manifest": data}
