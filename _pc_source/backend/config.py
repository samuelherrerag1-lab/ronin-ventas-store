import os
import socket
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHROME_VAULT_DIR = DATA_DIR / "chrome_vault"
CATALOG_JSON_PATH = DATA_DIR / "catalog.json"
FEEDS_JSON_PATH = DATA_DIR / "social_feeds.json"
CUSTOMIZATIONS_JSON_PATH = DATA_DIR / "customizations_state.json"
METRICS_REAL_PATH = DATA_DIR / "metrics_real.json"
LEADS_JSON_PATH = DATA_DIR / "leads.json"
SECRETS_JSON_PATH = DATA_DIR / "secrets.json"
CONNECT_JOBS_DIR = DATA_DIR / "connect_jobs"
FIN_OPS_JSON_PATH = DATA_DIR / "finops-ledger.json"
PUBLISH_SITE_DIR = DATA_DIR / "publish_site"


def _env(name: str, default: str) -> str:
    value = os.environ.get(name, "").strip()
    return value or default


# ---------------------------------------------------------------------------
# Vertex AI — proyecto nuevo (verificado 2026-11-04 con ADC de gcloud).
# Se puede sobreescribir con GOOGLE_CLOUD_PROJECT / VERTEX_LOCATION sin tocar código.
# ---------------------------------------------------------------------------
VERTEX_PROJECT_ID = _env(
    "GOOGLE_CLOUD_PROJECT",
    _env("VERTEX_PROJECT_ID", "example-project-id"),
)
VERTEX_LOCATION = _env("VERTEX_LOCATION", "global")
NANO_BANANA_MODEL = _env("NANO_BANANA_MODEL", "gemini-3.1-flash-image")
NANO_BANANA_FALLBACK_MODEL = _env("NANO_BANANA_FALLBACK_MODEL", "gemini-3.1-flash-lite-image")
VERTEX_MODEL_CANDIDATES = (NANO_BANANA_MODEL, NANO_BANANA_FALLBACK_MODEL)

# Precio real por imagen según docs/reconstruction/COST_MODEL.md (proyecto nuevo).
IMAGE_COST_USD = {
    "gemini-3.1-flash-image": 0.067,
    "gemini-3.1-flash-lite-image": 0.034,
    "gemini-2.5-flash-image": 0.030,
}
DEFAULT_IMAGE_COST_USD = IMAGE_COST_USD[NANO_BANANA_MODEL]
FINOPS_CIRCUIT_BREAKER_USD = float(_env("FINOPS_CIRCUIT_BREAKER_USD", "50"))

# Rutas del sistema local para conectores reales
GCLOUD_ADC_PATH = Path.home() / "AppData" / "Roaming" / "gcloud" / "application_default_credentials.json"
GLOBAL_SKILLS_DIR = Path.home() / ".agents" / "skills"
SIBLING_FINOPS_PATH = BASE_DIR.parent / "Generador de Contenido" / "finops-ledger.json"

CHROME_CANDIDATE_PATHS = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "Application" / "chrome.exe",
]

APP_HOST = "127.0.0.1"
BIND_HOST = "0.0.0.0"
APP_PORT = 8765


def _is_private_ipv4(ip: str) -> bool:
    parts = ip.split(".")
    if len(parts) != 4 or not all(p.isdigit() for p in parts):
        return False
    a, b = int(parts[0]), int(parts[1])
    return a == 10 or (a == 172 and 16 <= b <= 31) or (a == 192 and b == 168) or (a == 169 and b == 254)


def get_lan_ip() -> str:
    """IP privada real de la LAN. Nunca inventa una IP si no hay red."""
    candidates: list[str] = []
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            candidates.append(info[4][0])
    except Exception:
        pass
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(0.5)
            s.connect(("8.8.8.8", 80))
            candidates.append(s.getsockname()[0])
    except Exception:
        pass
    for ip in candidates:
        if _is_private_ipv4(ip) and not ip.startswith("169.254."):
            return ip
    return "127.0.0.1"


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CHROME_VAULT_DIR.mkdir(parents=True, exist_ok=True)


def find_chrome_executable() -> Path | None:
    for candidate in CHROME_CANDIDATE_PATHS:
        if candidate.exists():
            return candidate
    return None
