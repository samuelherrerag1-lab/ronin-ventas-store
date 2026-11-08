from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config import APP_PORT, BASE_DIR, PUBLISH_SITE_DIR, ensure_dirs, get_lan_ip
from backend.routers.api_bridge import router as bridge_router
from backend.routers.api_catalog import router as catalog_router
from backend.routers.api_customizations import router as customizations_router
from backend.routers.api_feeds import router as feeds_router
from backend.routers.api_leads import router as leads_router
from backend.routers.api_metrics import router as metrics_router
from backend.routers.api_publish import router as publish_router
from backend.security_middleware import install_security
from backend.services.delivery import is_owner, is_public, resolve as resolve_deliverable
from backend.services.product_factory import ensure_deliverables_dir
from backend.services.vertex_image_service import GENERATED_IMG_DIR, ensure_img_dir, vertex_status

ensure_dirs()
ensure_img_dir()
ensure_deliverables_dir()

app = FastAPI(title="Ronin Ventas OS — Desktop Core", version="2.1.0")
install_security(app)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; img-src 'self' data: blob:; "
        "style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; "
        "font-src 'self' data:; connect-src 'self'; frame-ancestors 'self'; base-uri 'self'; form-action 'self'",
    )
    return response

# El frontend se sirve desde el mismo origen que la API (PC y LAN), así que no
# se necesitan credenciales cross-origin. Se limita CORS a orígenes local/LAN:
# una página externa ya no puede leer respuestas de la API.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=(
        r"^https?://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|"
        r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})(:\d+)?$"
    ),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(catalog_router)
app.include_router(bridge_router)
app.include_router(feeds_router)
app.include_router(customizations_router)
app.include_router(leads_router)
app.include_router(metrics_router)
app.include_router(publish_router)

PRODUCT_ART_DIR = BASE_DIR / "data" / "product_art" / "web"
PRODUCT_ART_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/generated_images", StaticFiles(directory=str(GENERATED_IMG_DIR)), name="generated_images")
app.mount("/product_art", StaticFiles(directory=str(PRODUCT_ART_DIR)), name="product_art")


@app.get("/store")
@app.get("/store/")
def store_index():
    index_file = PUBLISH_SITE_DIR / "index.html"
    if not index_file.is_file():
        raise HTTPException(
            status_code=404,
            detail="El sitio publicable aún no está generado. Ejecuta scripts/build_publish_pack.py.",
        )
    return FileResponse(str(index_file))


@app.get("/store/{path:path}")
def store_file(path: str):
    """Sirve data/publish_site/ sin permitir escapar del directorio."""
    root = PUBLISH_SITE_DIR.resolve()
    candidate = (PUBLISH_SITE_DIR / path).resolve()
    if root not in candidate.parents and candidate != root:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    if candidate.is_dir():
        candidate = candidate / "index.html"
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    # Defensa en profundidad: aunque alguien copie un producto de pago al sitio
    # estático, no se sirve por esta vía. Solo los lead magnets son públicos.
    if "deliverables" in candidate.parts and not is_public(candidate.name):
        raise HTTPException(status_code=403, detail="Entregable de pago fuera de la tienda pública")
    return FileResponse(str(candidate))

FRONTEND_DIST = BASE_DIR / "frontend" / "dist"


@app.get("/api/health")
def health_check():
    lan_ip = get_lan_ip()
    vertex = vertex_status()
    site_ready = (PUBLISH_SITE_DIR / "manifest.json").is_file()
    return {
        "status": "ok",
        "system": "ronin_ventas_os",
        "block": 2,
        "lan_ip": lan_ip,
        "lan_url": f"http://{lan_ip}:{APP_PORT}",
        "frontend_built": (FRONTEND_DIST / "index.html").is_file(),
        "publish_site_ready": site_ready,
        "vertex": {
            "project_id": vertex["project_id"],
            "location": vertex["location"],
            "model": vertex["primary_model"],
            "fallback_model": vertex["fallback_model"],
            "adc_present": vertex["adc_present"],
        },
    }


@app.get("/deliverables/{path:path}")
def serve_deliverable(path: str, request: Request):
    target = resolve_deliverable(path)
    if target is None:
        raise HTTPException(status_code=404, detail="Entregable no encontrado")
    if not is_public(target.name) and not is_owner(request):
        raise HTTPException(
            status_code=403,
            detail="Este producto es de pago. Ábrelo desde el equipo del sistema o con un enlace de compra.",
        )
    return FileResponse(str(target))


@app.get("/api/{path:path}")
def api_not_found(path: str):
    """Un endpoint inexistente debe dar 404 JSON, nunca el HTML del SPA."""
    raise HTTPException(status_code=404, detail=f"Endpoint de API no encontrado: /api/{path}")


if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        index_file = FRONTEND_DIST / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"status": "frontend_not_built"}
