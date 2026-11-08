"""Utilidades de imagen y nombres para el alta de productos en Gumroad.

Gumroad solo acepta JPEG/PNG/GIF en `/v2/direct_uploads`, pero las portadas del
catálogo están en WebP: aquí se convierten en memoria (sin tocar data/).
"""

import io
import re
from pathlib import Path
from typing import Any, Dict


def cover_to_jpeg_bytes(path: Path, quality: int = 90) -> bytes:
    """Convierte la portada WebP del catálogo a JPEG para la API de Gumroad."""
    from PIL import Image

    with Image.open(path) as image:
        rgb = image.convert("RGB")
        buffer = io.BytesIO()
        rgb.save(buffer, format="JPEG", quality=quality, optimize=True)
    return buffer.getvalue()


def slug_of(product: Dict[str, Any]) -> str:
    """Slug real del producto: `custom_permalink` o el final de `short_url`."""
    slug = (product.get("custom_permalink") or "").strip()
    if slug:
        return slug
    match = re.search(r"/l/([^/?#]+)", product.get("short_url") or "")
    return match.group(1) if match else ""
