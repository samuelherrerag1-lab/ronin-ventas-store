"""Abre Chrome como navegador normal y expone CDP para inspección posterior.

Google bloquea el login cuando detecta automatización (`navigator.webdriver`).
Playwright marca el navegador al lanzarlo. Por eso el login se hace en un Chrome
lanzado como proceso normal y solo después nos conectamos por CDP.
"""

import os
import socket
import subprocess
import time
from pathlib import Path
from typing import List, Optional, Tuple

from backend.config import CHROME_VAULT_DIR, ensure_dirs, find_chrome_executable

CDP_PORT = 9333


def port_open(port: int = CDP_PORT) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.4)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def wait_for_cdp(port: int = CDP_PORT, timeout: float = 25.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if port_open(port):
            return True
        time.sleep(0.5)
    return False


def vault_chrome_pids() -> List[int]:
    """PIDs de Chrome usando el perfil del vault (nunca el Chrome personal)."""
    if os.name != "nt":
        return []
    marker = str(CHROME_VAULT_DIR).replace("'", "")
    script = (
        "Get-CimInstance Win32_Process -Filter \"Name='chrome.exe'\" | "
        f"Where-Object {{ $_.CommandLine -like '*{marker}*' }} | "
        "Select-Object -ExpandProperty ProcessId"
    )
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True, text=True, timeout=25,
        )
        return [int(line.strip()) for line in out.stdout.splitlines() if line.strip().isdigit()]
    except Exception:
        return []


def close_stale_vault_chrome() -> int:
    """Cierra Chrome del vault que quedó sin puerto de depuración."""
    pids = vault_chrome_pids()
    for pid in pids:
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, timeout=15)
    if pids:
        time.sleep(2.0)
    return len(pids)


def open_login_browser(url: str, port: int = CDP_PORT) -> Tuple[int, Optional[subprocess.Popen]]:
    """Devuelve (puerto, proceso). Proceso None si ya había un CDP activo."""
    if port_open(port):
        return port, None

    # Un Chrome zombi del vault bloquea el perfil y no expone CDP.
    close_stale_vault_chrome()

    chrome = find_chrome_executable()
    if chrome is None:
        raise RuntimeError("No se encontró chrome.exe en el sistema.")

    ensure_dirs()
    profile = Path(CHROME_VAULT_DIR)
    if not profile.exists():
        profile.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(chrome),
        f"--user-data-dir={profile}",
        f"--remote-debugging-port={port}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-features=Translate",
        url,
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not wait_for_cdp(port):
        proc.terminate()
        raise RuntimeError(
            "Chrome no expuso el puerto de depuración tras cerrar las instancias del vault. "
            "Cierra Chrome manualmente y vuelve a intentar."
        )
    return port, proc


def close_browser(proc: Optional[subprocess.Popen]) -> None:
    """Cierra solo la instancia que abrimos nosotros."""
    if proc is None:
        return
    try:
        proc.terminate()
        proc.wait(timeout=8)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass
