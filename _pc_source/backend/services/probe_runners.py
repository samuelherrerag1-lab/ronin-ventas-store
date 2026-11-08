import base64
import datetime
import json
import pathlib
import time
import urllib.request
from backend.config import APP_PORT, CHROME_VAULT_DIR, ensure_dirs, find_chrome_executable, get_lan_ip
from backend.models.diagnostic_models import ConnectorTestResult
from backend.services.vault_inspector import google_session_evidence

OPENCODE_SERVICE_PATH = pathlib.Path.home() / ".config" / "opencode" / "service.json"
TARGET_OPENCODE_SESSION = "ses_e64c0d9b1ffe56MtJmi0RNNym4"

DOMAIN_TARGETS = {
    "google_master": ("Google Master SSO", "https://accounts.google.com"),
    "threads": ("Threads (@ronoverthinks)", "https://www.threads.net"),
    "pinterest": ("Pinterest Business", "https://www.pinterest.com"),
    "gumroad": ("Gumroad USD Store", "https://gumroad.com"),
    "hotmart": ("Hotmart LatAm", "https://hotmart.com"),
    "github_pages": ("GitHub Pages Deploy", "https://github.com"),
}


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def test_vertex_ai() -> ConnectorTestResult:
    t0 = time.time()
    now = now_iso()
    try:
        from backend.services.vertex_image_service import GENERATED_IMG_DIR, generate_nano_banana_image

        res = generate_nano_banana_image("minimalist dark obsidian probe dot 1px", "1:1")
        filename = res.get("filename", "")
        file_path = GENERATED_IMG_DIR / filename
        if not file_path.exists() or file_path.stat().st_size < 500:
            raise RuntimeError(f"El archivo generado {filename} no existe o está corrupto (<500B)")
        ms = round((time.time() - t0) * 1000, 1)
        return ConnectorTestResult(
            connector_id="vertex_ai",
            name="Vertex AI & Nano Banana 2",
            status="CONECTADO",
            latency_ms=ms,
            detail=f"Vertex AI Nano Banana 2 operativo (imagen {filename} generada y validada en {ms}ms)",
            checked_at=now,
        )
    except Exception as exc:
        ms = round((time.time() - t0) * 1000, 1)
        err = f"Vertex AI: {type(exc).__name__} — {str(exc)}"
        return ConnectorTestResult(
            connector_id="vertex_ai",
            name="Vertex AI & Nano Banana 2",
            status="FALLA",
            latency_ms=ms,
            detail=err,
            checked_at=now,
            error_literal=err,
        )


def test_opencode_v2() -> ConnectorTestResult:
    t0 = time.time()
    now = now_iso()
    try:
        if not OPENCODE_SERVICE_PATH.exists():
            raise FileNotFoundError(f"service.json no encontrado en {OPENCODE_SERVICE_PATH}")
        cfg = json.loads(OPENCODE_SERVICE_PATH.read_text(encoding="utf-8"))
        password = cfg.get("password", "")
        auth = base64.b64encode(f"opencode:{password}".encode()).decode()
        req = urllib.request.Request(
            "http://127.0.0.1:28894/api/session",
            headers={"Authorization": f"Basic {auth}", "x-opencode-directory": r"C:\Users\USER\Documents\ronin_ventas"},
        )
        with urllib.request.urlopen(req, timeout=4) as res:
            if res.status != 200:
                raise RuntimeError(f"HTTP {res.status} al consultar sesiones de OpenCode V2")
            body = json.loads(res.read())
            sessions = body.get("data", []) if isinstance(body, dict) else body
            found = any(s.get("id") == TARGET_OPENCODE_SESSION for s in sessions if isinstance(s, dict))
            ms = round((time.time() - t0) * 1000, 1)
            if not found:
                err = f"OpenCode V2: Sesión {TARGET_OPENCODE_SESSION} no encontrada en daemon 127.0.0.1:28894"
                return ConnectorTestResult(
                    connector_id="opencode_v2",
                    name="OpenCode V2 (Fábrica SubAgente)",
                    status="FALLA",
                    latency_ms=ms,
                    detail=err,
                    checked_at=now,
                    error_literal=err,
                )
            return ConnectorTestResult(
                connector_id="opencode_v2",
                name="OpenCode V2 (Fábrica SubAgente)",
                status="CONECTADO",
                latency_ms=ms,
                detail=f"OpenCode V2 activo (sesión {TARGET_OPENCODE_SESSION} confirmada en {ms}ms)",
                checked_at=now,
            )
    except Exception as exc:
        ms = round((time.time() - t0) * 1000, 1)
        err = f"OpenCode V2: {type(exc).__name__} — {str(exc)}"
        return ConnectorTestResult(
            connector_id="opencode_v2",
            name="OpenCode V2 (Fábrica SubAgente)",
            status="FALLA",
            latency_ms=ms,
            detail=err,
            checked_at=now,
            error_literal=err,
        )


def test_chrome_vault() -> ConnectorTestResult:
    """Google Master solo es CONECTADO si el vault tiene sesión real de Google.

    Antes lanzaba un Chrome headless con un `user-data-dir` temporal vacío y, si
    el proceso salía con 0, reportaba CONECTADO sin tocar Google. Eso era un
    falso verde que pintaba el badge SSO. Ahora se verifica la cookie de sesión
    de accounts.google.com en `data/chrome_vault`; si no hay evidencia, el
    estado es SIN_VERIFICAR con el motivo literal.
    """
    t0 = time.time()
    now = now_iso()
    name = "Google Master Session (Chrome Vault)"
    try:
        exe = find_chrome_executable()
        if not exe or not exe.exists():
            raise FileNotFoundError("chrome.exe no encontrado en rutas del sistema")
        ensure_dirs()
        evidence = google_session_evidence()
        ms = round((time.time() - t0) * 1000, 1)
        if evidence["session_found"]:
            return ConnectorTestResult(
                connector_id="google_master",
                name=name,
                status="CONECTADO",
                latency_ms=ms,
                detail=(
                    f"Sesión de Google verificada en {CHROME_VAULT_DIR.name}: "
                    f"{evidence['session_cookie_count']} cookies de sesión de google.com "
                    f"({', '.join(evidence['session_cookie_examples'])}), leídas en local."
                ),
                checked_at=now,
            )
        reason = evidence.get("reason") or "sin cookies de sesión de google.com"
        return ConnectorTestResult(
            connector_id="google_master",
            name=name,
            status="SIN_VERIFICAR",
            latency_ms=ms,
            detail=(
                f"Chrome encontrado en {exe.name}, pero no hay sesión de Google verificable "
                f"en {CHROME_VAULT_DIR}: {reason}. Abre Conectar → Google Master e inicia sesión."
            ),
            checked_at=now,
        )
    except Exception as exc:  # noqa: BLE001 - se devuelve la razón literal
        ms = round((time.time() - t0) * 1000, 1)
        err = f"Google Chrome: {type(exc).__name__} — {str(exc)}"
        return ConnectorTestResult(
            connector_id="google_master",
            name=name,
            status="FALLA",
            latency_ms=ms,
            detail=err,
            checked_at=now,
            error_literal=err,
        )


def test_social_domain(connector_id: str, name: str, url: str) -> ConnectorTestResult:
    t0 = time.time()
    now = now_iso()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 RoninVentasOS/2.0"}, method="HEAD")
        try:
            with urllib.request.urlopen(req, timeout=4) as res:
                pass
        except Exception:
            req_get = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 RoninVentasOS/2.0"}, method="GET")
            with urllib.request.urlopen(req_get, timeout=4) as res:
                pass
        ms = round((time.time() - t0) * 1000, 1)
        return ConnectorTestResult(
            connector_id=connector_id,
            name=name,
            status="SIN_VERIFICAR",
            latency_ms=ms,
            detail=f"{name}: Red alcanzable ({ms}ms). Sesión en Chrome Vault no verificable automáticamente por seguridad.",
            checked_at=now,
        )
    except Exception as exc:
        ms = round((time.time() - t0) * 1000, 1)
        err = f"{name}: Falla de red hacia {url} ({type(exc).__name__}: {str(exc)})"
        return ConnectorTestResult(
            connector_id=connector_id,
            name=name,
            status="FALLA",
            latency_ms=ms,
            detail=err,
            checked_at=now,
            error_literal=err,
        )


def test_lan_server() -> ConnectorTestResult:
    t0 = time.time()
    now = now_iso()
    lan_ip = get_lan_ip()
    target_url = f"http://{lan_ip}:{APP_PORT}/api/health"
    try:
        with urllib.request.urlopen(target_url, timeout=3) as res:
            if res.status != 200:
                raise RuntimeError(f"HTTP {res.status}")
        ms = round((time.time() - t0) * 1000, 1)
        return ConnectorTestResult(
            connector_id="lan_server",
            name="Servidor LAN (0.0.0.0:8765)",
            status="CONECTADO",
            latency_ms=ms,
            detail=f"Servidor LAN activo en http://{lan_ip}:{APP_PORT}/api/health ({ms}ms)",
            checked_at=now,
        )
    except Exception as exc:
        ms = round((time.time() - t0) * 1000, 1)
        err = f"Servidor LAN: Inaccesible en {lan_ip}:{APP_PORT} ({type(exc).__name__}: {str(exc)})"
        return ConnectorTestResult(
            connector_id="lan_server",
            name="Servidor LAN (0.0.0.0:8765)",
            status="FALLA",
            latency_ms=ms,
            detail=err,
            checked_at=now,
            error_literal=err,
        )
