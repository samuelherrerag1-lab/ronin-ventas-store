"""Control de acceso a los entregables.

Los productos de pago no pueden servirse a cualquiera: el servidor escucha en
0.0.0.0 y toda la red Wi-Fi podía descargar los 52 SKUs. Los lead magnets sí
son públicos por diseño.
"""

from pathlib import Path
from typing import Optional

from fastapi import Request

from backend.services.product_factory import DELIVERABLES_DIR

LEAD_MAGNET_IDS = {"L01", "L02", "L03"}
OWNER_HOSTS = {"127.0.0.1", "::1", "localhost"}


def sku_from_filename(filename: str) -> Optional[str]:
    prefix = filename.split("_", 1)[0].upper()
    return prefix if len(prefix) == 3 and prefix[0] in "EBAKML" else None


def is_public(filename: str) -> bool:
    sku = sku_from_filename(filename)
    return sku is None or sku in LEAD_MAGNET_IDS


def is_owner(request: Request) -> bool:
    client = request.client.host if request.client else ""
    return client in OWNER_HOSTS


def resolve(path: str) -> Optional[Path]:
    """Resuelve dentro de deliverables sin permitir escapar del directorio."""
    candidate = (DELIVERABLES_DIR / path).resolve()
    root = DELIVERABLES_DIR.resolve()
    if root not in candidate.parents and candidate != root:
        return None
    return candidate if candidate.is_file() else None
