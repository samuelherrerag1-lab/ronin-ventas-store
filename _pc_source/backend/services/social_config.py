"""Configuración, rutas y guardas del publicador social real.

El perfil persistente por defecto es ``data/chrome_vault``. Si existe
``data/_locks/chrome_vault.owner`` otro proceso está usando ese perfil: el
publicador se niega a abrirlo para no corromper la sesión y explica quién lo
tiene. Para desarrollo y pruebas se puede cambiar con
``RONIN_SOCIAL_PROFILE_DIR`` (por ejemplo ``data/chrome_vault_test``).
"""

import datetime
import os
import random
from pathlib import Path
from typing import Optional

from backend.config import CHROME_VAULT_DIR, DATA_DIR

SOCIAL_DIR = DATA_DIR / "publish_jobs"
EVIDENCE_DIR = SOCIAL_DIR / "evidence"
REPLY_IMAGES_DIR = SOCIAL_DIR / "images"
SESSIONS_PATH = SOCIAL_DIR / "sessions.json"
REPLY_QUEUE_PATH = SOCIAL_DIR / "reply_queue.json"
SCHEDULE_PATH = SOCIAL_DIR / "schedule.json"
PUBLISHED_INDEX_PATH = SOCIAL_DIR / "published_index.json"

VAULT_LOCK_PATH = DATA_DIR / "_locks" / "chrome_vault.owner"

PLATFORMS = ("threads", "pinterest")
PLATFORM_LABEL = {"threads": "Threads", "pinterest": "Pinterest"}
PLATFORM_HOME = {
    "threads": "https://www.threads.net/",
    "pinterest": "https://www.pinterest.com/",
}
PLATFORM_LOGIN = {
    "threads": "https://www.threads.net/login",
    "pinterest": "https://www.pinterest.com/login/",
}
JOB_ID_RE = r"^job_[A-Za-z0-9_]{6,64}$"


class SocialError(RuntimeError):
    """Error honesto y accionable del publicador social (sin fingir éxito)."""


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def min_delay_s() -> float:
    return max(0.0, _env_float("RONIN_SOCIAL_MIN_DELAY", 20.0))


def max_delay_s() -> float:
    return max(min_delay_s(), _env_float("RONIN_SOCIAL_MAX_DELAY", 60.0))


def piece_delay_s() -> float:
    """Pausa humana entre piezas (por defecto 20-60 s)."""
    return random.uniform(min_delay_s(), max_delay_s())


def goto_timeout_ms() -> int:
    return int(max(5.0, _env_float("RONIN_SOCIAL_GOTO_TIMEOUT_S", 45.0)) * 1000)


def login_timeout_s() -> float:
    return max(30.0, _env_float("RONIN_SOCIAL_LOGIN_TIMEOUT_S", 900.0))


def login_poll_s() -> float:
    return max(1.0, _env_float("RONIN_SOCIAL_LOGIN_POLL_S", 3.0))


def browser_lock_timeout_s() -> float:
    return max(1.0, _env_float("RONIN_SOCIAL_BROWSER_LOCK_S", 30.0))


def chrome_channel() -> str:
    """Canal real de Chrome. ``chromium`` solo para desarrollo sin Chrome."""
    return os.environ.get("RONIN_SOCIAL_CHANNEL", "chrome").strip() or "chrome"


def ensure_dirs() -> None:
    for folder in (SOCIAL_DIR, EVIDENCE_DIR, REPLY_IMAGES_DIR):
        folder.mkdir(parents=True, exist_ok=True)


def profile_dir() -> Path:
    override = os.environ.get("RONIN_SOCIAL_PROFILE_DIR", "").strip()
    if override:
        return Path(override).expanduser()
    return Path(CHROME_VAULT_DIR)


def using_vault() -> bool:
    try:
        return profile_dir().resolve() == Path(CHROME_VAULT_DIR).resolve()
    except OSError:
        return False


def vault_lock_owner() -> Optional[str]:
    if not VAULT_LOCK_PATH.is_file():
        return None
    try:
        owner = VAULT_LOCK_PATH.read_text(encoding="utf-8").strip()
    except OSError:
        return "desconocido"
    return owner or "desconocido"


def assert_profile_available() -> Path:
    """Devuelve el perfil utilizable o falla sin abrir un Chrome en uso."""
    profile = profile_dir()
    if using_vault():
        owner = vault_lock_owner()
        if owner:
            raise SocialError(
                "El perfil persistente data/chrome_vault está en uso por "
                f"'{owner}' (data/_locks/chrome_vault.owner). No se abre para no "
                "corromper esa sesión. Espera a que libere el lock o arranca con "
                "RONIN_SOCIAL_PROFILE_DIR=data/chrome_vault_test."
            )
    profile.mkdir(parents=True, exist_ok=True)
    return profile


def data_relative(path: Path) -> str:
    """Ruta relativa a data/ para guardarla en JSON y servirla por API."""
    try:
        return path.resolve().relative_to(DATA_DIR.resolve()).as_posix()
    except (OSError, ValueError):
        return path.as_posix()


def evidence_path(name: str) -> Path:
    ensure_dirs()
    safe = "".join(ch for ch in name if ch.isalnum() or ch in "._-")[:120]
    return EVIDENCE_DIR / (safe or "evidence")
