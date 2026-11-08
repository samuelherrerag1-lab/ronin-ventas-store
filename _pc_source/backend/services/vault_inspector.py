"""Inspección real del Chrome Vault.

Devuelve únicamente hechos medidos. Si algo no se puede leer, lo dice con la
razón literal en lugar de inventar un valor. No hay puntuaciones estimadas.

`google_session_evidence()` es la única fuente para decidir si la sesión de
Google Master existe: lee la base SQLite de cookies del vault (copia temporal,
porque Chrome la bloquea) y busca cookies de sesión de google.com.
"""

import importlib.util
import shutil
import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from backend.config import CHROME_VAULT_DIR, ensure_dirs, find_chrome_executable

COOKIES_RELATIVE = Path("Default") / "Network" / "Cookies"
SESSION_HINTS = ("session", "sid", "auth", "token", "login", "remember")
GOOGLE_SESSION_HINTS = (
    "sid",
    "hsid",
    "ssid",
    "apisid",
    "sapisid",
    "oauth",
    "__secure-1psid",
    "__secure-3psid",
)


def google_session_evidence() -> Dict[str, Any]:
    """¿Hay una sesión real de Google en el vault? Solo hechos locales."""
    cookies_path = CHROME_VAULT_DIR / COOKIES_RELATIVE
    rows, error = _read_cookie_rows(cookies_path)
    if error is not None:
        return {
            "session_found": False,
            "session_cookie_count": 0,
            "google_cookie_count": 0,
            "session_cookie_examples": [],
            "reason": error,
        }
    google_cookies = [
        (str(host).lstrip("."), str(name))
        for host, name in rows
        if str(host or "").lstrip(".").endswith("google.com")
    ]
    session_names = sorted(
        {name for _, name in google_cookies if any(hint in name.lower() for hint in GOOGLE_SESSION_HINTS)}
    )
    reason: Optional[str] = None
    if not google_cookies:
        reason = "no hay cookies de google.com en el vault: nadie inició sesión en Chrome"
    elif not session_names:
        reason = f"{len(google_cookies)} cookies de google.com pero ninguna de sesión (solo preferencias)"
    return {
        "session_found": bool(session_names),
        "session_cookie_count": len(session_names),
        "google_cookie_count": len(google_cookies),
        "session_cookie_examples": session_names[:5],
        "reason": reason,
    }


def _read_cookie_rows(cookies_path: Path) -> Tuple[List[Tuple[str, str]], Optional[str]]:
    if not cookies_path.exists():
        return [], f"No existe el archivo de cookies: {cookies_path.name}"
    tmp_dir = Path(tempfile.mkdtemp(prefix="ronin_cookies_"))
    tmp_file = tmp_dir / "Cookies"
    try:
        shutil.copy2(cookies_path, tmp_file)
        con = sqlite3.connect(f"file:{tmp_file.as_posix()}?mode=ro", uri=True)
        try:
            return list(con.execute("SELECT host_key, name FROM cookies")), None
        finally:
            con.close()
    except Exception as exc:  # noqa: BLE001 - queremos la razón literal
        return [], f"{type(exc).__name__}: {exc}"
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _read_cookie_hosts(cookies_path: Path) -> Dict[str, Any]:
    rows, error = _read_cookie_rows(cookies_path)
    if error is not None:
        return {
            "readable": False,
            "reason": error,
            "hosts": [],
            "session_cookies": 0,
        }
    host_set: List[str] = sorted({str(host).lstrip(".") for host, _ in rows if host})
    session_count = sum(1 for _, name in rows if any(hint in str(name).lower() for hint in SESSION_HINTS))
    return {
        "readable": True,
        "reason": None,
        "hosts": host_set,
        "session_cookies": session_count,
    }


def _playwright_available() -> bool:
    try:
        return importlib.util.find_spec("playwright") is not None
    except Exception:  # noqa: BLE001
        return False


def inspect_chrome_vault() -> Dict[str, Any]:
    """Hechos verificables del perfil persistente de Chrome."""
    ensure_dirs()
    chrome = find_chrome_executable()
    profile_dir = CHROME_VAULT_DIR / "Default"
    cookies = _read_cookie_hosts(CHROME_VAULT_DIR / COOKIES_RELATIVE)
    google = google_session_evidence()

    return {
        "chrome_binary_found": chrome is not None,
        "chrome_binary_path": str(chrome) if chrome else None,
        "persistent_vault_dir": str(CHROME_VAULT_DIR),
        "profile_exists": profile_dir.is_dir(),
        "cookies_readable": cookies["readable"],
        "cookies_reason": cookies["reason"],
        "domains_with_cookies": cookies["hosts"],
        "session_cookie_count": cookies["session_cookies"],
        "google_session_verified": google["session_found"],
        "google_session_reason": google["reason"],
        "playwright_installed": _playwright_available(),
        # Sin sonda de fingerprint ejecutada no existe puntuación.
        "fingerprint_measured": False,
        "liarjs_target_score": None,
    }
