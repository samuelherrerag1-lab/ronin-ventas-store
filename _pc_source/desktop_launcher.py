import logging
import subprocess
import threading
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from backend.config import APP_HOST, APP_PORT, BIND_HOST, DATA_DIR, get_lan_ip

EDGE_CANDIDATES = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
]


def configure_logging() -> Path:
    """Log con rotación: si la ventana se cierra, queda evidencia del error."""
    log_dir = DATA_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "ronin_os.log"
    handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)
    return log_path


def launch_native_desktop_window(url: str) -> None:
    time.sleep(1.2)
    for exe in EDGE_CANDIDATES:
        if exe.exists():
            cmd = [
                str(exe),
                f"--app={url}",
                "--window-size=1440,920",
                "--disable-features=Translate",
            ]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return


if __name__ == "__main__":
    log_path = configure_logging()
    target_url = f"http://{APP_HOST}:{APP_PORT}"
    lan_ip = get_lan_ip()
    lan_url = f"http://{lan_ip}:{APP_PORT}" if lan_ip != "127.0.0.1" else "sin red privada detectada"
    print("=" * 68)
    print("  RONIN VENTAS OS — APLICATIVO DE ESCRITORIO & RED LAN (@ronOverthinks)")
    print(f"  Servidor Local (PC) : {target_url}")
    print(f"  Acceso Movil (LAN)  : {lan_url}")
    print(f"  Log                 : {log_path}")
    print("=" * 68)
    logging.getLogger("ronin.launcher").info(
        "Iniciando servidor en %s:%s (LAN %s)", BIND_HOST, APP_PORT, lan_ip
    )
    threading.Thread(target=launch_native_desktop_window, args=(target_url,), daemon=True).start()
    uvicorn.run("backend.main:app", host=BIND_HOST, port=APP_PORT, reload=False, log_config=None)
