"""Resolución del access token de Gumroad (capa sin navegador).

Orden: `GUMROAD_ACCESS_TOKEN` (env) -> token guardado en `data/secrets.json` ->
login humano en Chrome persistente. La parte de navegador vive en
`gumroad_browser.py` para respetar el límite de 250 líneas por archivo.
"""

import os
from typing import Any, Dict, Optional

from backend.services.connect_jobs import get_secret
from backend.services.gumroad_browser import (  # noqa: F401  (re-export para scripts)
    harvest_token,
    probe_session,
    store,
    validate_token,
    wait_for_login,
)


def acquire_token(force: bool = False) -> Dict[str, Any]:
    """Devuelve un token válido; si no hay, abre el login humano y espera."""
    env_token = (os.environ.get("GUMROAD_ACCESS_TOKEN") or "").strip()
    if env_token and not force:
        account = validate_token(env_token)
        if account:
            return store(env_token, account, "env_GUMROAD_ACCESS_TOKEN")
    stored = get_secret("gumroad", "access_token")
    if stored and not force:
        account = validate_token(stored)
        if account:
            return {"status": "connected", "source": "stored_secret", "account": account,
                    "evidence": f"GET /v2/user OK para {account.get('email')}"}
    return wait_for_login(timeout_sec=3600)
