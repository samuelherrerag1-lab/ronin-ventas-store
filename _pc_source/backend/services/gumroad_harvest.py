"""Extracción del token de Gumroad desde la sesión ya iniciada.

No confía en selectores: recoge candidatos de la página y valida cada uno
contra `GET /v2/user`. El primero que responde con una cuenta es el token.
"""

import json
import re
import urllib.parse
import urllib.request
from typing import Any, Callable, Dict, List, Optional

from backend.services.connect_jobs import store_secret

SETTINGS_URLS = [
    "https://gumroad.com/settings/advanced",
    "https://app.gumroad.com/settings/advanced",
    "https://gumroad.com/settings",
]


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    url = "https://api.gumroad.com/v2/user?" + urllib.parse.urlencode({"access_token": token})
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "RoninVentasOS/2.0"})
        with urllib.request.urlopen(req, timeout=12) as res:
            payload = json.loads(res.read().decode("utf-8", "replace"))
        if payload.get("success") and payload.get("user"):
            user = payload["user"]
            return {"email": user.get("email"), "name": user.get("name"), "user_id": user.get("user_id")}
    except Exception:
        return None
    return None


def _candidates(page) -> List[str]:
    found: List[str] = []
    try:
        found.extend(str(v) for v in page.eval_on_selector_all("input", "els => els.map(e => e.value).filter(Boolean)"))
    except Exception:
        pass
    try:
        found.extend(str(v) for v in page.eval_on_selector_all("code, pre, textarea", "els => els.map(e => e.textContent).filter(Boolean)"))
    except Exception:
        pass
    try:
        found.extend(re.findall(r"[A-Za-z0-9_-]{24,80}", page.inner_text("body")))
    except Exception:
        pass

    seen, ordered = set(), []
    for item in found:
        item = item.strip()
        if 24 <= len(item) <= 90 and item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered[:25]


def harvest_gumroad(page, connector_id: str, notify: Callable[..., None]) -> Dict[str, Any]:
    for url in SETTINGS_URLS:
        notify(connector_id, status="harvesting", step=f"Buscando token en {url}")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
        except Exception:
            continue
        page.wait_for_timeout(2500)

        for label in ("Generate token", "Create token", "New token", "Generar token", "Crear token"):
            try:
                btn = page.get_by_role("button", name=re.compile(label, re.I)).first
                if btn.count() and btn.is_visible():
                    btn.click(timeout=4000)
                    page.wait_for_timeout(2000)
                    break
            except Exception:
                continue

        for candidate in _candidates(page):
            verified = verify_token(candidate)
            if verified:
                store_secret("gumroad", {"access_token": candidate, **verified, "source": "playwright_harvest"})
                return {
                    "status": "connected",
                    "step": "Token de Gumroad verificado",
                    "detail": f"API validada con la cuenta {verified.get('email')}.",
                    "evidence": f"GET /v2/user → {verified.get('email')}",
                }

    return {
        "status": "logged_in_no_token",
        "step": "Sesión iniciada, token no encontrado",
        "detail": "Abre Settings → Advanced, genera un token y vuelve a pulsar Conectar.",
        "evidence": "Login confirmado; ningún candidato pasó la verificación de la API.",
    }
