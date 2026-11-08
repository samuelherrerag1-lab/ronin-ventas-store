"""Sesión real de Chrome persistente y verificación medible.

Usa ``launch_persistent_context(user_data_dir=..., channel="chrome",
headless=False)``. El estado de sesión se guarda en
``data/publish_jobs/sessions.json`` con la evidencia literal observada.
Nunca se declara una cuenta conectada sin una medición.
"""

import threading
import time
from contextlib import contextmanager
from typing import Any, Dict, Iterator, Optional, Tuple

from backend.services import social_config as cfg
from backend.services import social_detect as detect
from backend.services.json_store import read_json, write_json_atomic

_BROWSER_LOCK = threading.Lock()
_SESSION_LOCK = threading.Lock()


def empty_session(platform: str) -> Dict[str, Any]:
    return {
        "platform": platform,
        "logged_in": False,
        "status": "unknown",
        "account_label": None,
        "evidence": (
            "Sin verificación real todavía. Pulsa 'Verificar sesión' o abre el "
            "login para medir la sesión del perfil persistente."
        ),
        "checked_at": None,
        "url": None,
        "screenshot": None,
        "stale": True,
    }


def load_sessions() -> Dict[str, Any]:
    with _SESSION_LOCK:
        data, error = read_json(cfg.SESSIONS_PATH)
    if error or not isinstance(data, dict):
        return {"platforms": {}, "notes": ["sessions.json ausente o ilegible"]}
    if not isinstance(data.get("platforms"), dict):
        data["platforms"] = {}
    return data


def save_session(platform: str, state: Dict[str, Any]) -> Dict[str, Any]:
    with _SESSION_LOCK:
        data, error = read_json(cfg.SESSIONS_PATH)
        if error or not isinstance(data, dict):
            data = {"platforms": {}}
        data.setdefault("platforms", {})[platform] = dict(state)
        data["updated_at"] = cfg.now_iso()
        write_json_atomic(cfg.SESSIONS_PATH, data)
    return state


def get_session(platform: str) -> Dict[str, Any]:
    data = load_sessions()
    stored = data["platforms"].get(platform)
    merged = empty_session(platform)
    if isinstance(stored, dict):
        merged.update(stored)
    merged["platform"] = platform
    return merged


@contextmanager
def persistent_context() -> Iterator[Tuple[Any, Any]]:
    """Abre Chrome persistente real con ventana visible (UI web de verdad)."""
    profile = cfg.assert_profile_available()
    if not _BROWSER_LOCK.acquire(timeout=cfg.browser_lock_timeout_s()):
        raise cfg.SocialError(
            "Ya hay un Chrome automatizado en curso (login o publicación). "
            "Espera a que termine antes de lanzar otra operación."
        )
    try:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:  # pragma: no cover - entorno sin Playwright
            raise cfg.SocialError(f"Playwright no está instalado: {exc}") from exc

        cfg.ensure_dirs()
        try:
            with sync_playwright() as playwright:
                context = playwright.chromium.launch_persistent_context(
                    user_data_dir=str(profile),
                    channel=cfg.chrome_channel(),
                    headless=False,
                    viewport={"width": 1440, "height": 960},
                    locale="es-ES",
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-first-run",
                        "--no-default-browser-check",
                        "--disable-features=Translate",
                    ],
                )
                try:
                    page = context.pages[0] if context.pages else context.new_page()
                    yield context, page
                finally:
                    try:
                        context.close()
                    except Exception:
                        pass
        except cfg.SocialError:
            raise
        except Exception as exc:  # noqa: BLE001 - razón literal para el operador
            raise cfg.SocialError(
                "No se pudo abrir Chrome persistente con channel="
                f"'{cfg.chrome_channel()}' en '{profile}'. Detalle: "
                f"{type(exc).__name__}: {exc}"
            ) from exc
    finally:
        _BROWSER_LOCK.release()


@contextmanager
def platform_session(platform: str) -> Iterator[Any]:
    """Chrome persistente ya navegado a la home de la plataforma."""
    if platform not in cfg.PLATFORMS:
        raise cfg.SocialError(f"Plataforma no soportada: {platform}")
    with persistent_context() as (_context, page):
        page.goto(
            cfg.PLATFORM_HOME[platform],
            wait_until="domcontentloaded",
            timeout=cfg.goto_timeout_ms(),
        )
        time.sleep(1.5)
        yield page


def capture(page: Any, name: str, job_id: str = "") -> Optional[str]:
    """Screenshot de evidencia. Devuelve ruta relativa a data/ si existe."""
    cfg.ensure_dirs()
    stamp = time.strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(ch for ch in name if ch.isalnum() or ch in "._-")[:60] or "shot"
    prefix = f"{job_id}_" if job_id else ""
    target = cfg.evidence_path(f"{prefix}{safe_name}_{stamp}.png")
    try:
        page.screenshot(path=str(target), full_page=False)
    except Exception:
        return None
    return cfg.data_relative(target) if target.is_file() else None


def measure_page(page: Any, platform: str, label: str) -> Dict[str, Any]:
    """Mide login + bloqueo y captura evidencia en la página ya cargada."""
    measured = dict(detect.detect_login(page, platform))
    block = detect.detect_block(page)
    measured.update(
        {
            "checked_at": cfg.now_iso(),
            "screenshot": capture(page, label),
            "blocked": bool(block["blocked"]),
            "stale": False,
        }
    )
    if block["blocked"]:
        measured.update({"logged_in": False, "status": "blocked", "evidence": block["evidence"]})
    return measured


def verify_session(platform: str) -> Dict[str, Any]:
    """Abre el Chrome persistente y mide el login de verdad. Guarda evidencia."""
    if platform not in cfg.PLATFORMS:
        raise cfg.SocialError(f"Plataforma no soportada: {platform}")
    try:
        with platform_session(platform) as page:
            state = measure_page(page, platform, f"session_{platform}")
    except cfg.SocialError as exc:
        state = {**empty_session(platform)}
        state.update({"status": "error", "evidence": str(exc), "checked_at": cfg.now_iso(), "stale": False})
    except Exception as exc:  # noqa: BLE001 - la causa literal es la evidencia
        state = {**empty_session(platform)}
        state.update(
            {
                "status": "error",
                "evidence": f"No se pudo verificar la sesión: {type(exc).__name__}: {exc}",
                "checked_at": cfg.now_iso(),
                "stale": False,
            }
        )
    save_session(platform, state)
    return state


def browser_busy() -> bool:
    return _BROWSER_LOCK.locked()
