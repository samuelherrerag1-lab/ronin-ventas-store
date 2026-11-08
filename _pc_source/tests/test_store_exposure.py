"""El sitio estático no puede exponer entregables de pago (C1/C6 del audit).

`data/publish_site/deliverables/` solo contiene lead magnets públicos. Si un
build futuro copia los 52 SKUs de pago, este test falla: la tienda pública no es
un segundo canal de descarga gratis.
"""

import pytest
from fastapi.testclient import TestClient

from backend.config import PUBLISH_SITE_DIR
from backend.main import app
from backend.services.delivery import LEAD_MAGNET_IDS, sku_from_filename

client = TestClient(app, client=("192.168.1.50", 50000))  # visitante LAN: sin privilegios de dueño
STORE_DELIVERABLES = PUBLISH_SITE_DIR / "deliverables"
PAID_PREFIXES = ("E", "B", "A", "K", "M")


def test_publish_site_contains_no_paid_deliverable_html():
    if not STORE_DELIVERABLES.is_dir():
        pytest.skip("data/publish_site no está exportado en este entorno")
    html_files = sorted(STORE_DELIVERABLES.glob("*.html"))
    assert html_files, "el sitio público debe incluir al menos los lead magnets"

    paid = [
        path.name
        for path in html_files
        if (sku_from_filename(path.name) or "").startswith(PAID_PREFIXES)
    ]
    assert paid == [], f"entregables de pago copiados a la tienda pública: {paid}"

    public = [path.name for path in html_files if sku_from_filename(path.name) in LEAD_MAGNET_IDS]
    assert public, "faltan los lead magnets públicos en el sitio"


def test_store_serves_lead_magnet_and_blocks_paid_deliverable():
    lead_magnet = STORE_DELIVERABLES / "l02_27-hooks-prohibidos.html"
    if not lead_magnet.is_file():
        pytest.skip("data/publish_site no incluye los lead magnets en este entorno")

    served = client.get("/store/deliverables/l02_27-hooks-prohibidos.html")
    assert served.status_code == 200
    assert served.headers["content-type"].startswith("text/html")

    blocked = client.get("/store/deliverables/e01_maquina-silenciosa-pdf.html")
    assert blocked.status_code in (403, 404), blocked.status_code
