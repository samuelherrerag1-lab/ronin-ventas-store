"""Automatización de navegador para la sesión de Gumroad (solo Playwright).

Login humano una vez en el perfil persistente `data/chrome_vault` y extracción o
creación del access token en Settings -> Advanced. La validación final siempre se
hace contra `GET /v2/user`; nunca se declara "conectado" sin esa prueba.
"""

import json
import re
import time
from typing import Any, Dict, List, Optional

from backend.config import CHROME_VAULT_DIR, DATA_DIR
from backend.services.connect_jobs import store_secret
from backend.services.gumroad_products import GumroadClient, GumroadError, utc_now

SETTINGS_URLS = (
    "https://gumroad.com/settings/advanced",
    "https://app.gumroad.com/settings/advanced",
    "https://gumroad.com/settings",
)
LOGIN_URL = "https://gumroad.com/login?next=%2Fsettings%2Fadvanced"
STATE_PATH = DATA_DIR / "_locks" / "gumroad_login.state.json"
CAPTURES_DIR = DATA_DIR / "captures" / "gumroad"
TOKEN_RE = re.compile(r"[A-Za-z0-9_-]{24,90}")
APP_NAME = "Ronin Ventas OS"
REDIRECT_URI = "http://127.0.0.1"


def _heartbeat(payload: Dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {"updated_at": utc_now(), **payload}
    STATE_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _launch():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    ctx = pw.chromium.launch_persistent_context(
        user_data_dir=str(CHROME_VAULT_DIR),
        channel="chrome",
        headless=False,
        viewport={"width": 1440, "height": 950},
        args=["--no-first-run", "--no-default-browser-check", "--disable-features=Translate"],
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.set_default_timeout(15000)
    return pw, ctx, page


def _safe_close(pw, ctx) -> None:
    for closer in (lambda: ctx.close(), lambda: pw.stop()):
        try:
            closer()
        except Exception:
            pass


def _shot(page, name: str) -> str:
    CAPTURES_DIR.mkdir(parents=True, exist_ok=True)
    path = CAPTURES_DIR / name
    try:
        page.screenshot(path=str(path), full_page=False)
    except Exception:
        return ""
    return str(path)


def _candidates(page) -> List[str]:
    found: List[str] = []
    for selector, js in (
        ("input, textarea", "els => els.map(e => e.value).filter(Boolean)"),
        ("code, pre, .token, [data-token]", "els => els.map(e => e.textContent).filter(Boolean)"),
    ):
        try:
            found.extend(str(v) for v in page.eval_on_selector_all(selector, js))
        except Exception:
            pass
    try:
        found.extend(TOKEN_RE.findall(page.inner_text("body")))
    except Exception:
        pass
    seen, ordered = set(), []
    for item in found:
        item = item.strip()
        if 20 <= len(item) <= 90 and item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered[:40]


def validate_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        user = GumroadClient(token).get_user()
    except GumroadError:
        return None
    if not user:
        return None
    return {"email": user.get("email"), "name": user.get("name"), "user_id": user.get("user_id") or user.get("id")}


def store(token: str, account: Dict[str, Any], source: str) -> Dict[str, Any]:
    store_secret("gumroad", {"access_token": token, **account, "source": source, "key_last4": token[-4:]})
    return {"status": "connected", "source": source, "account": account,
            "evidence": f"GET /v2/user OK para {account.get('email')}"}


def _click_first(page, labels) -> List[str]:
    clicked: List[str] = []
    for label in labels:
        try:
            locator = page.get_by_role("button", name=re.compile(re.escape(label), re.I)).first
            if locator.count() and locator.is_visible():
                locator.click(timeout=5000)
                clicked.append(label)
                page.wait_for_timeout(2500)
        except Exception:
            continue
    return clicked


def _fill_application_form(page) -> List[str]:
    """Rellena el formulario de aplicación de API si Settings lo muestra vacío."""
    filled: List[str] = []
    for pattern, value in ((re.compile(r"application name|^name$|app name", re.I), APP_NAME),
                           (re.compile(r"redirect|callback|uri", re.I), REDIRECT_URI)):
        try:
            field = page.get_by_label(pattern).first
            if field.count() and field.is_visible():
                field.fill(value, timeout=4000)
                filled.append(value)
        except Exception:
            continue
    if len(filled) < 2:
        try:
            inputs = [el for el in page.query_selector_all("input[type=text], input[type=url], input:not([type])")
                      if el.is_visible()]
            for index, value in enumerate((APP_NAME, REDIRECT_URI)):
                if index < len(inputs) and value not in filled:
                    inputs[index].fill(value, timeout=4000)
                    filled.append(value)
        except Exception:
            pass
    if filled:
        _click_first(page, ("Create application", "Create app", "Save", "Generate access token", "Generate token"))
    return filled


def harvest_token(page, allow_form: bool = True) -> Dict[str, Any]:
    """Busca, crea si hace falta, y valida el token en Settings -> Advanced."""
    screenshot = ""
    for url in SETTINGS_URLS:
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3500)
        except Exception:
            continue
        if "/login" in page.url:
            return {"status": "login_required", "url": page.url, "step": "Login de Gumroad requerido"}
        _click_first(page, ("Generate access token", "Generate token", "Create token", "New token", "Create application"))
        page.wait_for_timeout(1500)
        for candidate in _candidates(page):
            account = validate_token(candidate)
            if account:
                return store(candidate, account, "playwright_harvest")
        if allow_form and _fill_application_form(page):
            page.wait_for_timeout(2500)
            for candidate in _candidates(page):
                account = validate_token(candidate)
                if account:
                    return store(candidate, account, "playwright_application")
        screenshot = _shot(page, "no_token.png")
    return {
        "status": "logged_in_no_token",
        "url": page.url,
        "step": "Crear aplicación de API (nombre + redirect http://127.0.0.1) y pulsar Generate access token",
        "screenshot": screenshot,
    }


def probe_session() -> Dict[str, Any]:
    pw, ctx, page = _launch()
    try:
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2500)
        if "/login" in page.url:
            return {"logged_in": False, "url": page.url, "title": page.title(),
                    "detail": "La cookie _gumroad_app_session del perfil existe pero Gumroad la rechaza.",
                    "screenshot": _shot(page, "probe_login_required.png")}
        harvest = harvest_token(page)
        return {"logged_in": True, "url": page.url, "title": page.title(), "harvest": harvest,
                "screenshot": _shot(page, "probe_logged_in.png")}
    finally:
        _safe_close(pw, ctx)


def _looks_authenticated(url: str) -> bool:
    """Solo cuenta como sesión iniciada si estamos en un área privada real."""
    return bool(re.search(r"gumroad\.com/(settings|dashboard|library)", url or ""))


def wait_for_login(timeout_sec: int = 3600, poll_sec: int = 4) -> Dict[str, Any]:
    """Abre la ventana de login y espera. Devuelve token cuando el humano entra."""
    pw, ctx, page = _launch()
    try:
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        deadline = time.time() + max(60, int(timeout_sec))
        _heartbeat({"status": "awaiting_login", "url": page.url, "started_at": utc_now()})
        print(json.dumps({"status": "awaiting_login", "url": page.url, "command": "login --wait",
                          "timeout_sec": timeout_sec}, ensure_ascii=False), flush=True)
        attempts = 0
        while time.time() < deadline:
            if page.is_closed():
                _heartbeat({"status": "window_closed"})
                return {"status": "window_closed", "step": "La ventana se cerró antes de completar el login"}
            if _looks_authenticated(page.url):
                attempts += 1
                _heartbeat({"status": "login_detected", "url": page.url, "attempt": attempts})
                page.wait_for_timeout(1500)
                result = harvest_token(page)
                if result.get("status") == "connected":
                    _heartbeat({"status": "connected", "detail": result.get("evidence")})
                    return result
                if not page.is_closed():  # falso positivo: seguir esperando sin cerrar
                    try:
                        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=20000)
                    except Exception:
                        pass
            page.wait_for_timeout(poll_sec * 1000)
        _heartbeat({"status": "login_timeout"})
        return {"status": "login_timeout", "step": "No hubo login en la ventana durante el tiempo de espera",
                "url": page.url if not page.is_closed() else "",
                "screenshot": _shot(page, "login_timeout.png") if not page.is_closed() else ""}
    finally:
        _safe_close(pw, ctx)
