"""Detección medible de sesión y de bloqueo/captcha.

Todo lo que se afirma aquí sale de lo que la página muestra: URL, selectores
visibles y textos. Nunca se marca ``logged_in`` sin una señal observada.
"""

import re
from typing import Any, Dict, List, Optional

from backend.services.social_dom import locator_first, page_url, visible

LOGIN_URL_MARKERS = (
    "/login",
    "/accounts/login",
    "/auth/login",
    "/signin",
    "/sign-in",
    "checkpoint",
)

LOGIN_WALL_SELECTORS = {
    "threads": [
        "input[name='username']",
        "input[autocomplete='username']",
        "a[href='/login']",
        "a[href*='/login']",
        "div[role='dialog'] input[type='text']",
    ],
    "pinterest": [
        "input[name='id']",
        "input[id='email']",
        "input[type='email']",
        "a[href*='/login']",
        "div[data-test-id='login-modal']",
    ],
}

LOGGED_IN_SELECTORS = {
    "threads": [
        "a[href^='/@']",
        "svg[aria-label*='New thread' i]",
        "svg[aria-label*='Nuevo hilo' i]",
        "div[contenteditable='true'][role='textbox']",
        "div[contenteditable='true']",
        "[aria-label*='Create' i]",
        "[aria-label*='Crear' i]",
    ],
    "pinterest": [
        "[data-test-id='header-profile']",
        "a[href^='/user/']",
        "[data-test-id='homefeed-feed']",
        "div[data-test-id='pin-builder']",
        "[data-test-id='search-box']",
    ],
}

PROFILE_LINK_SELECTORS = {
    "threads": ("a[href^='/@']", "a[href*='threads.net/@']"),
    "pinterest": (
        "a[href^='/user/']",
        "a[href*='pinterest.com/user/']",
        "[data-test-id='header-profile'] a[href]",
    ),
}

BLOCK_MARKERS = (
    "captcha",
    "verifica que eres humano",
    "confirm you're human",
    "confirm you are human",
    "unusual activity",
    "actividad inusual",
    "security check",
    "comportamiento automatizado",
    "automated behavior",
    "challenge_required",
    "cuenta suspendida temporalmente",
    "temporarily blocked",
)


def _profile_account(page: Any, platform: str) -> Optional[str]:
    for selector in PROFILE_LINK_SELECTORS.get(platform, ()):
        locator = locator_first(page, selector)
        if locator is None:
            continue
        try:
            if locator.count() == 0 or not locator.is_visible(timeout=0):
                continue
            href = locator.get_attribute("href") or ""
        except Exception:
            continue
        if platform == "threads":
            match = re.search(r"/@([^/?#]+)", href)
        else:
            match = re.search(r"/user/([^/?#]+)", href) or re.search(
                r"^/([A-Za-z0-9_.-]{2,40})/?(?:[?#].*)?$", href
            )
        if match:
            return match.group(1)
        try:
            label = (locator.get_attribute("aria-label") or "").strip()
        except Exception:
            label = ""
        if label:
            return label[:80]
    return None


def detect_login(page: Any, platform: str) -> Dict[str, Any]:
    """Estado de sesión medido con señales observadas en la página."""
    url = page_url(page)
    normalized = url.lower()
    if any(marker in normalized for marker in LOGIN_URL_MARKERS):
        return {
            "logged_in": False,
            "status": "login_required",
            "account_label": None,
            "evidence": f"URL de login detectada: {url}. No hay sesión activa.",
            "url": url,
            "signals": [],
        }

    for selector in LOGIN_WALL_SELECTORS.get(platform, []):
        if visible(page, selector):
            return {
                "logged_in": False,
                "status": "login_required",
                "account_label": None,
                "evidence": (
                    f"URL={url} · muro de login visible con el selector '{selector}'. "
                    "Hace falta iniciar sesión una vez."
                ),
                "url": url,
                "signals": [selector],
            }

    signals = [selector for selector in LOGGED_IN_SELECTORS.get(platform, []) if visible(page, selector)]
    if signals:
        account = _profile_account(page, platform)
        evidence = f"URL={url} · señales de sesión visibles: {', '.join(signals[:3])}"
        if account:
            evidence += f" · cuenta={account}"
        return {
            "logged_in": True,
            "status": "logged_in",
            "account_label": account,
            "evidence": evidence,
            "url": url,
            "signals": signals,
        }

    return {
        "logged_in": False,
        "status": "login_required",
        "account_label": None,
        "evidence": (
            f"URL={url} · sin señales de sesión (ni muro de login ni avatar/compositor). "
            "No se puede confirmar la cuenta."
        ),
        "url": url,
        "signals": [],
    }


def detect_block(page: Any) -> Dict[str, Any]:
    """Detecta captcha, checkpoint o bloqueo anti-bot por el texto visible."""
    text = ""
    locator = locator_first(page, "body")
    if locator is not None:
        try:
            text = locator.inner_text(timeout=3000) or ""
        except Exception:
            text = ""
    haystack = text.lower()[:40000]
    found: List[str] = [marker for marker in BLOCK_MARKERS if marker in haystack]
    if not found:
        return {"blocked": False, "evidence": "", "markers": []}
    return {
        "blocked": True,
        "evidence": (
            "Señal de bloqueo/captcha en la página: "
            + ", ".join(found)
            + ". El job se detiene sin publicar."
        ),
        "markers": found,
    }
