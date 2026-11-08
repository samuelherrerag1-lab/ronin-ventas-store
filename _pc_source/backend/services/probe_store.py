"""Sondas de los conectores que tienen credencial propia.

Gumroad se prueba con el token guardado (no con "el dominio responde").
GitHub se prueba con la CLI oficial. Ninguna inventa un estado.
"""

import json
import subprocess
import time
import urllib.parse
import urllib.request

from backend.models.diagnostic_models import ConnectorTestResult
from backend.services.probe_runners import now_iso


def test_gumroad_api() -> ConnectorTestResult:
    """Prueba real contra la API de Gumroad usando el token almacenado."""
    t0 = time.time()
    now = now_iso()
    from backend.services.connect_jobs import get_secret

    token = get_secret("gumroad", "access_token")
    if not token:
        return ConnectorTestResult(
            connector_id="gumroad",
            name="Gumroad (Checkout Global USD)",
            status="SIN_VERIFICAR",
            latency_ms=0.0,
            detail="Sin token de API. Pulsa Conectar y completa el login en la ventana de Chrome.",
            checked_at=now,
        )
    query = urllib.parse.urlencode({"access_token": token})
    try:
        req = urllib.request.Request(
            f"https://api.gumroad.com/v2/user?{query}",
            headers={"User-Agent": "RoninVentasOS/2.0"},
        )
        with urllib.request.urlopen(req, timeout=12) as res:
            payload = json.loads(res.read().decode("utf-8", "replace"))
        ms = round((time.time() - t0) * 1000, 1)
        user = payload.get("user") or {}
        if not payload.get("success"):
            raise RuntimeError("La API respondió sin éxito")
        return ConnectorTestResult(
            connector_id="gumroad",
            name="Gumroad (Checkout Global USD)",
            status="CONECTADO",
            latency_ms=ms,
            detail=f"API validada con la cuenta {user.get('email', '(sin email)')} en {ms}ms",
            checked_at=now,
        )
    except Exception as exc:  # noqa: BLE001
        ms = round((time.time() - t0) * 1000, 1)
        err = f"Gumroad API: {type(exc).__name__} — {str(exc)[:180]}"
        return ConnectorTestResult(
            connector_id="gumroad",
            name="Gumroad (Checkout Global USD)",
            status="FALLA",
            latency_ms=ms,
            detail=err,
            checked_at=now,
            error_literal=err,
        )


def test_github_auth() -> ConnectorTestResult:
    """GitHub no usa navegador: se verifica con `gh auth status`."""
    t0 = time.time()
    now = now_iso()
    try:
        proc = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, timeout=15)
        ms = round((time.time() - t0) * 1000, 1)
        output = (proc.stdout + proc.stderr).strip()
        if proc.returncode == 0:
            account = next(
                (line.strip() for line in output.splitlines() if "account" in line.lower()),
                "sesión activa",
            )
            return ConnectorTestResult(
                connector_id="github_pages",
                name="GitHub / Cloudflare Deploy",
                status="CONECTADO",
                latency_ms=ms,
                detail=f"gh autenticado: {account}",
                checked_at=now,
            )
        first = output.splitlines()[0] if output else "sin salida"
        return ConnectorTestResult(
            connector_id="github_pages",
            name="GitHub / Cloudflare Deploy",
            status="FALLA",
            latency_ms=ms,
            detail=f"gh sin sesión: {first}",
            checked_at=now,
            error_literal=output[:200] or "gh auth status falló",
        )
    except Exception as exc:  # noqa: BLE001
        ms = round((time.time() - t0) * 1000, 1)
        err = f"GitHub CLI: {type(exc).__name__} — {exc}"
        return ConnectorTestResult(
            connector_id="github_pages",
            name="GitHub / Cloudflare Deploy",
            status="FALLA",
            latency_ms=ms,
            detail=err,
            checked_at=now,
            error_literal=err,
        )
