"""Trabajador de conexión. Corre en un proceso aparte (ver connect_jobs).

Abre Chrome con el perfil persistente del vault, espera a que el usuario inicie
sesión y, cuando lo detecta, verifica la sesión o extrae el token del proveedor.
Nunca inventa un estado: si no puede probar la sesión, lo dice.
"""

import datetime
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.config import CONNECT_JOBS_DIR, ensure_dirs
from backend.services.gumroad_harvest import harvest_gumroad
from backend.services.json_store import read_json, write_json_atomic

LOGIN_TIMEOUT_SEC = 720
POLL_SEC = 2.0

PROFILES: Dict[str, Dict[str, Any]] = {
    "gumroad": {
        "login_url": "https://gumroad.com/login",
        "home_url": "https://gumroad.com/",
        "logged_in": ["a[href*='/products']", "a[href*='/settings']", "[data-testid='user-menu']"],
        "settings_urls": [
            "https://gumroad.com/settings/advanced",
            "https://app.gumroad.com/settings/advanced",
            "https://gumroad.com/settings",
        ],
        "harvest": "gumroad_token",
    },
    "hotmart": {
        "login_url": "https://app-vlc.hotmart.com/login",
        "home_url": "https://app-vlc.hotmart.com/tools/products",
        "logged_in": ["[data-testid='user-menu']", "a[href*='/products']", "[class*='avatar']"],
        "harvest": "session_only",
    },
    "pinterest": {
        "login_url": "https://www.pinterest.com/login/",
        "home_url": "https://www.pinterest.com/",
        "logged_in": ["[data-test-id='header-profile']", "a[href*='/ideas/']", "[data-test-id='profile-avatar']"],
        "harvest": "session_only",
    },
    "threads": {
        "login_url": "https://www.threads.net/login",
        "home_url": "https://www.threads.net/",
        "logged_in": ["a[href*='/settings']", "svg[aria-label='Perfil']", "[aria-label='Profile']"],
        "harvest": "session_only",
    },
    "google": {
        "login_url": "https://accounts.google.com/",
        "home_url": "https://myaccount.google.com/",
        "logged_in": ["a[href*='SignOutOptions']", "[aria-label*='Cuenta de Google']", "img[alt*='perfil']"],
        "harvest": "session_only",
    },
}


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _write(connector_id: str, **fields: Any) -> None:
    ensure_dirs()
    CONNECT_JOBS_DIR.mkdir(parents=True, exist_ok=True)
    path = CONNECT_JOBS_DIR / f"{connector_id}.json"
    data, _error = read_json(path)
    current: Dict[str, Any] = data if isinstance(data, dict) else {}
    current.update(fields)
    current["updated_at"] = _now()
    write_json_atomic(path, current)


def _wait_for_login(page, connector_id: str, profile: Dict[str, Any]) -> bool:
    started = time.time()
    while time.time() - started < LOGIN_TIMEOUT_SEC:
        elapsed = int(time.time() - started)
        try:
            url = page.url or ""
        except Exception:
            return False
        if "/login" not in url and "accounts.google.com" not in url:
            for selector in profile["logged_in"]:
                try:
                    if page.locator(selector).first.is_visible(timeout=700):
                        return True
                except Exception:
                    continue
        _write(
            connector_id,
            status="awaiting_login",
            step="Esperando inicio de sesión",
            detail=f"Inicia sesión en la ventana de Chrome. ({elapsed}s)",
            elapsed_sec=elapsed,
        )
        page.wait_for_timeout(int(POLL_SEC * 1000))
    return False


def _persist_diagnostic(connector_id: str, status: str, detail: str) -> None:
    """Deja constancia del resultado para que el Hub no dependa de la memoria."""
    try:
        from backend.models.diagnostic_models import ConnectorTestResult
        from backend.services.connector_diagnostics import _save_single_test_result

        _save_single_test_result(
            ConnectorTestResult(
                connector_id=connector_id,
                name=connector_id,
                status=status,
                latency_ms=0.0,
                detail=detail,
                checked_at=_now(),
            )
        )
    except Exception:
        pass


def run(connector_id: str, target_url: str, provider: str) -> None:
    profile = PROFILES.get(provider)
    if not profile:
        _write(connector_id, status="failed", step="Proveedor desconocido", detail=f"Sin perfil para {provider}")
        return

    _write(connector_id, status="starting", step="Abriendo Chrome", detail="Lanzando el navegador del vault.")

    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # noqa: BLE001
        _write(connector_id, status="failed", step="Playwright no disponible", detail=str(exc))
        return

    from backend.services.browser_launcher import close_browser, open_login_browser

    proc = None
    try:
        port, proc = open_login_browser(profile["login_url"])
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.pages[0] if context.pages else context.new_page()
            _write(connector_id, status="browser_open", step="Chrome abierto",
                   detail="Inicia sesión con Google en la ventana. El sistema la detecta solo.")

            try:
                if profile["home_url"] not in (page.url or ""):
                    page.goto(profile["home_url"], wait_until="domcontentloaded", timeout=45000)
            except Exception:
                pass

            if not _wait_for_login(page, connector_id, profile):
                _write(connector_id, status="timeout", step="Tiempo de espera agotado",
                       detail="No se detectó la sesión. Cierra la ventana y vuelve a intentar.")
                return

            _write(connector_id, status="logged_in", step="Sesión detectada", detail="Verificando credenciales.")

            if profile["harvest"] == "gumroad_token":
                result = harvest_gumroad(page, connector_id, _write)
            else:
                result = {
                    "status": "connected",
                    "step": "Sesión verificada",
                    "detail": f"Sesión activa en {page.url}",
                    "evidence": f"Marcador de sesión encontrado en {page.url}",
                }

            if result.get("status") == "connected":
                _persist_diagnostic(connector_id, "CONECTADO", result.get("evidence") or result.get("detail", ""))

            _write(connector_id, **result)
    except Exception as exc:  # noqa: BLE001
        message = str(exc)
        if "already in use" in message.lower() or "ProcessSingleton" in message:
            message = "El perfil de Chrome está en uso. Cierra la ventana y reintenta."
        _write(connector_id, status="failed", step="Error de conexión", detail=f"{type(exc).__name__}: {message}")
    finally:
        close_browser(proc)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise SystemExit("uso: python -m backend.services.connect_worker <connector_id> <url> <provider>")
    run(sys.argv[1], sys.argv[2], sys.argv[3])
