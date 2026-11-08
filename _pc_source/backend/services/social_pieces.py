"""Construye piezas publicables desde la cola real y prepara sus imágenes.

Fuente única de contenido: ``data/social_feeds.json`` (nunca se inventan
textos aquí). Los límites de cada red se aplican de verdad: un post de Threads
que supera 500 caracteres se recorta y se deja constancia en ``notes``.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.config import DATA_DIR, PUBLISH_SITE_DIR
from backend.services import social_config as cfg
from backend.services.catalog_seed import load_or_init_catalog
from backend.services.json_store import read_json, write_json_atomic
from backend.services.social_feed_seed import load_or_init_feeds

COVERS_DIR = DATA_DIR / "product_art" / "web" / "covers"
THREADS_LIMIT = 500
PIN_TITLE_LIMIT = 100
PIN_DESC_LIMIT = 500
PIN_SIZE = {"2:3": (1000, 1500), "9:16": (1080, 1920)}


def _is_public_host(url: str) -> bool:
    """Pinterest rechaza IPs privadas/localhost: no se pone un link inútil."""
    from urllib.parse import urlparse

    host = (urlparse(url).hostname or "").lower()
    if not host or host in ("localhost", "127.0.0.1", "0.0.0.0", "::1"):
        return False
    if host.startswith(("10.", "192.168.", "169.254.")):
        return False
    if host.startswith("172."):
        try:
            return not 16 <= int(host.split(".")[1]) <= 31
        except (ValueError, IndexError):
            return False
    return "." in host


def public_base_url() -> str:
    """Dominio público para los links de los pines (nunca inventa uno)."""
    override = os.environ.get("RONIN_PUBLIC_BASE_URL", "").strip()
    if override and _is_public_host(override):
        return override.rstrip("/")
    manifest, _error = read_json(PUBLISH_SITE_DIR / "manifest.json")
    if isinstance(manifest, dict):
        base = str(manifest.get("base_url") or "").strip()
        if base.startswith("http") and _is_public_host(base):
            return base.rstrip("/")
    return ""


def clip(text: str, limit: int) -> tuple:
    text = (text or "").strip()
    if len(text) <= limit:
        return text, False
    return text[: max(0, limit - 3)].rstrip() + "...", True


def _threads_text(post: Any, notes: List[str]) -> str:
    text = "\n\n".join(slide for slide in post.body_slides if slide).strip()
    clipped, was_clipped = clip(text, THREADS_LIMIT)
    if was_clipped:
        notes.append(f"Texto recortado a {THREADS_LIMIT} caracteres (límite de Threads).")
    return clipped


def _cover_for(sku_id: str) -> Optional[Path]:
    if not COVERS_DIR.is_dir():
        return None
    candidates = sorted(COVERS_DIR.glob(f"{sku_id.upper()}_*.webp"))
    return candidates[0] if candidates else None


def resolve_image(relative: Optional[str], sku_id: str) -> Optional[Path]:
    """Ruta en disco de la imagen de la pieza; None si no hay imagen real."""
    if relative:
        candidate = DATA_DIR / relative.lstrip("/")
        if candidate.is_file():
            return candidate
    return _cover_for(sku_id)


def _ui_image_url(path: Optional[Path]) -> Optional[str]:
    if path is None:
        return None
    try:
        return "/" + path.resolve().relative_to(DATA_DIR.resolve()).as_posix()
    except (OSError, ValueError):
        return None


def _routes_by_sku() -> Dict[str, str]:
    return {item.sku_id: item.bridge_route for item in load_or_init_catalog()}


def _pin_piece(pin: Any, routes: Dict[str, str]) -> Dict[str, Any]:
    notes: List[str] = []
    title, clipped = clip(pin.seo_title, PIN_TITLE_LIMIT)
    if clipped:
        notes.append(f"Título recortado a {PIN_TITLE_LIMIT} caracteres.")
    description, clipped = clip(pin.seo_description, PIN_DESC_LIMIT)
    if clipped:
        notes.append(f"Descripción recortada a {PIN_DESC_LIMIT} caracteres.")
    route = pin.bridge_route or routes.get(pin.target_sku_id, "")
    base = public_base_url()
    link = f"{base}{route}" if base and route.startswith("/") else route
    if not base:
        notes.append(
            "Sin base URL PÚBLICA (RONIN_PUBLIC_BASE_URL o manifest del sitio): el pin se "
            "publica sin link. Pinterest rechaza localhost/IP privada, así que no se envía uno roto."
        )
    image_path = resolve_image(pin.image_url, pin.target_sku_id)
    if image_path is None:
        notes.append("No hay imagen real en disco para este pin: no se puede publicar en Pinterest.")
    return {
        "id": pin.pin_id,
        "platform": "pinterest",
        "sku_id": pin.target_sku_id,
        "text": description,
        "title": title,
        "description": description,
        "board": pin.board_name,
        "target_route": link,
        "image_path": str(image_path) if image_path else None,
        "image_url": _ui_image_url(image_path),
        "aspect_ratio": pin.aspect_ratio,
        "self_replies": [],
        "notes": notes,
        "status": pin.status,
    }


def _threads_piece(post: Any, routes: Dict[str, str]) -> Dict[str, Any]:
    notes: List[str] = []
    text = _threads_text(post, notes)
    image_path = resolve_image(getattr(post, "image_url", None), post.target_sku_id)
    route = routes.get(post.target_sku_id, "")
    if not image_path:
        notes.append("La cola no trae imagen adjunta para este post: se publica solo texto.")
    return {
        "id": post.post_id,
        "platform": "threads",
        "sku_id": post.target_sku_id,
        "text": text,
        "target_route": route,
        "image_path": str(image_path) if image_path else None,
        "image_url": _ui_image_url(image_path),
        "self_replies": [reply for reply in post.suggested_self_replies if reply.strip()][:2],
        "notes": notes,
        "status": post.status,
    }


def list_pieces(platform: str, limit: int = 20, ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Piezas seleccionadas de la cola real, en el orden pedido."""
    if platform not in cfg.PLATFORMS:
        raise cfg.SocialError(f"Plataforma no soportada: {platform}")
    feeds = load_or_init_feeds()
    routes = _routes_by_sku()
    if platform == "threads":
        pieces = [_threads_piece(post, routes) for post in feeds["threads"]]
    else:
        pieces = [
            _pin_piece(pin, routes)
            for pin in feeds["pinterest"]
            if not pin.is_competitor_benchmark
        ]
    if ids:
        wanted = {item_id.strip() for item_id in ids if item_id.strip()}
        pieces = [piece for piece in pieces if piece["id"] in wanted]
    return pieces[:limit]


def get_piece(platform: str, item_id: str) -> Optional[Dict[str, Any]]:
    for piece in list_pieces(platform, limit=500, ids=[item_id]):
        return piece
    return None


def prepare_pin_image(piece: Dict[str, Any], job_id: str) -> Optional[str]:
    """Normaliza la imagen a 1000x1500 (o 1080x1920) con Pillow, sin deformar."""
    source = piece.get("image_path")
    if not source or not Path(source).is_file():
        return None
    target_size = PIN_SIZE.get(str(piece.get("aspect_ratio") or "2:3"), PIN_SIZE["2:3"])
    cfg.ensure_dirs()
    output = cfg.REPLY_IMAGES_DIR / f"{job_id}_{piece['id']}_{target_size[0]}x{target_size[1]}.png"
    try:
        from PIL import Image
    except ImportError:
        return None
    try:
        with Image.open(source) as image:
            image = image.convert("RGB")
            target_ratio = target_size[0] / target_size[1]
            width, height = image.size
            ratio = width / height
            if ratio > target_ratio:
                new_width = int(height * target_ratio)
                image = image.crop(((width - new_width) // 2, 0, (width + new_width) // 2, height))
            else:
                new_height = int(width / target_ratio)
                image = image.crop((0, (height - new_height) // 2, width, (height + new_height) // 2))
            image = image.resize(target_size, Image.LANCZOS)
            image.save(output, "PNG", optimize=True)
    except Exception:
        return None
    return str(output)


def published_index() -> Dict[str, Any]:
    data, error = read_json(cfg.PUBLISHED_INDEX_PATH)
    return data if isinstance(data, dict) and not error else {}


def mark_published(platform: str, item_id: str, url: Optional[str], job_id: str) -> None:
    """Registra una publicación REAL (con URL) para que el scheduler no la repita."""
    data = published_index()
    data.setdefault(platform, {})[item_id] = {
        "post_url": url,
        "job_id": job_id,
        "published_at": cfg.now_iso(),
    }
    data["updated_at"] = cfg.now_iso()
    write_json_atomic(cfg.PUBLISHED_INDEX_PATH, data)
