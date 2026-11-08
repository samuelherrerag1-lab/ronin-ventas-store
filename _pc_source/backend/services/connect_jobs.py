"""Gestión de trabajos de conexión y almacenamiento local de secretos.

Cada conexión corre en un proceso aparte (`connect_worker`) para no bloquear el
servidor. El progreso se escribe en `data/connect_jobs/{connector}.json` con
lock y escritura atómica; la UI lo consulta.
"""

import datetime
import os
import re
import subprocess
import sys
from typing import Any, Dict, Optional

from backend.config import BASE_DIR, CONNECT_JOBS_DIR, SECRETS_JSON_PATH, ensure_dirs
from backend.services.json_store import lock_for, read_json, write_json_atomic


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _job_path(connector_id: str) -> "os.PathLike[str]":
    # El id viene de la URL: sin este filtro permitiría ../ y escribir fuera.
    if not re.fullmatch(r"[a-z0-9_]{1,32}", connector_id):
        raise ValueError(f"Identificador de conector inválido: {connector_id}")
    ensure_dirs()
    CONNECT_JOBS_DIR.mkdir(parents=True, exist_ok=True)
    return CONNECT_JOBS_DIR / f"{connector_id}.json"


def _read_job(connector_id: str) -> Optional[Dict[str, Any]]:
    path = _job_path(connector_id)
    data, error = read_json(path)
    return data if error is None and isinstance(data, dict) else None


def get_job(connector_id: str) -> Optional[Dict[str, Any]]:
    try:
        return _read_job(connector_id)
    except ValueError:
        return None


def _process_command_line(pid: int) -> str:
    """CommandLine del PID; se usa para no matar un proceso ajeno reciclado."""
    if os.name != "nt":
        return ""
    script = (
        "Get-CimInstance Win32_Process -Filter \"ProcessId="
        f"{int(pid)}\" | Select-Object -ExpandProperty CommandLine"
    )
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True,
            text=True,
            timeout=8,
        )
        return (out.stdout or "").strip()
    except Exception:
        return ""


def _is_alive(pid: Optional[int]) -> bool:
    if not pid:
        return False
    try:
        out = subprocess.run(
            ["tasklist", "/FI", f"PID eq {int(pid)}", "/NH"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if str(pid) not in (out.stdout or ""):
            return False
    except Exception:
        return False
    command_line = _process_command_line(int(pid))
    # Si no se puede leer el command line, se asume vivo: no matamos nada.
    return not command_line or "connect_worker" in command_line.lower()


def _write_job(connector_id: str, payload: Dict[str, Any]) -> None:
    write_json_atomic(_job_path(connector_id), payload)


def stop_job(connector_id: str) -> Dict[str, Any]:
    path = _job_path(connector_id)
    with lock_for(path):
        job = _read_job(connector_id) or {}
        pid = job.get("pid")
        if pid and _is_alive(pid):
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, timeout=10)
        job.update(
            {
                "status": "stopped",
                "detail": "Trabajo detenido por el usuario.",
                "updated_at": _now(),
            }
        )
        _write_job(connector_id, job)
    return job


def start_job(connector_id: str, target_url: str, provider: str) -> Dict[str, Any]:
    path = _job_path(connector_id)
    with lock_for(path):
        current = _read_job(connector_id)
        if current and current.get("status") in (
            "starting",
            "browser_open",
            "awaiting_login",
            "harvesting",
        ):
            if _is_alive(current.get("pid")):
                return {**current, "already_running": True}

        initial: Dict[str, Any] = {
            "connector_id": connector_id,
            "provider": provider,
            "status": "starting",
            "step": "Preparando Chrome con el perfil persistente",
            "detail": "Lanzando el trabajador de conexión.",
            "pid": None,
            "started_at": _now(),
            "updated_at": _now(),
            "evidence": None,
            "login_url": target_url,
        }
        _write_job(connector_id, initial)

        creationflags = 0
        if os.name == "nt":
            creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(
                subprocess, "DETACHED_PROCESS", 0
            )
        proc = subprocess.Popen(
            [sys.executable, "-m", "backend.services.connect_worker", connector_id, target_url, provider],
            cwd=str(BASE_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )
        initial["pid"] = proc.pid
        _write_job(connector_id, initial)
    return initial


def _load_secrets() -> Dict[str, Any]:
    ensure_dirs()
    data, error = read_json(SECRETS_JSON_PATH)
    return data if error is None and isinstance(data, dict) else {}


def _save_secrets(data: Dict[str, Any]) -> None:
    ensure_dirs()
    write_json_atomic(SECRETS_JSON_PATH, data)


def store_secret(provider: str, payload: Dict[str, Any]) -> None:
    with lock_for(SECRETS_JSON_PATH):
        data = _load_secrets()
        data[provider] = {**payload, "stored_at": _now()}
        _save_secrets(data)


def get_secret(provider: str, key: str) -> Optional[str]:
    return (_load_secrets().get(provider) or {}).get(key)


def masked_secrets() -> Dict[str, Any]:
    """Nunca devuelve el secreto completo: solo si existe y sus últimos 4."""
    out: Dict[str, Any] = {}
    for provider, payload in _load_secrets().items():
        masked: Dict[str, Any] = {}
        for key, value in payload.items():
            if key in ("access_token", "token", "secret", "password") and isinstance(value, str):
                masked[key] = f"****{value[-4:]}" if len(value) > 4 else "****"
            else:
                masked[key] = value
        out[provider] = masked
    return out
