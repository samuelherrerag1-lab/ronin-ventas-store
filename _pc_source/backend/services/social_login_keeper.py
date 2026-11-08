"""Ventana de login humano UNA vez sobre el perfil persistente.

El keeper abre Chrome con la UI real, espera a que el humano inicie sesión y
detecta el final de forma medible. No marca la cuenta como conectada si no ve
la señal: guarda el estado con la evidencia literal.
"""

import threading
import time
from typing import Any, Dict, Optional

from backend.services import social_browser as browser
from backend.services import social_config as cfg
from backend.services import social_detect as detect

_KEEPER_LOCK = threading.Lock()


class LoginKeeper:
    def __init__(self) -> None:
        self._guard = _KEEPER_LOCK
        self._thread: Optional[threading.Thread] = None
        self._state: Dict[str, Any] = {
            "running": False,
            "platform": None,
            "status": "idle",
            "started_at": None,
            "finished_at": None,
            "detail": "",
            "screenshot": None,
        }

    def _set(self, **fields: Any) -> None:
        with self._guard:
            self._state.update(fields)

    def status(self) -> Dict[str, Any]:
        with self._guard:
            state = dict(self._state)
            alive = self._thread is not None and self._thread.is_alive()
        if state.get("running") and not alive:
            state["running"] = False
        return state

    def start(self, platform: str) -> Dict[str, Any]:
        if platform not in cfg.PLATFORMS:
            raise cfg.SocialError(f"Plataforma no soportada: {platform}")
        with self._guard:
            if self._thread is not None and self._thread.is_alive():
                current = str(self._state.get("platform"))
                return {
                    "started": False,
                    "running": True,
                    "platform": current,
                    "status": "login_window_open",
                    "detail": (
                        f"Ya hay una ventana de login abierta para {current}. "
                        "Termínala antes de abrir otra."
                    ),
                    "login_url": cfg.PLATFORM_LOGIN.get(current, ""),
                    "profile": str(cfg.profile_dir()),
                }
            self._state = {
                "running": True,
                "platform": platform,
                "status": "starting",
                "started_at": cfg.now_iso(),
                "finished_at": None,
                "detail": "Abriendo Chrome persistente para login humano.",
                "screenshot": None,
            }
            thread = threading.Thread(
                target=self._run, args=(platform,), daemon=True, name=f"ronin-login-{platform}"
            )
            self._thread = thread
        thread.start()
        return {
            "started": True,
            "running": True,
            "platform": platform,
            "status": "login_window_open",
            "detail": (
                "Ventana de login abierta. Inicia sesión en esa ventana de Chrome; "
                "el sistema la detectará solo y cerrará la ventana. Si el perfil "
                "está en uso por otro proceso, primero hay que liberarlo."
            ),
            "login_url": cfg.PLATFORM_LOGIN[platform],
            "profile": str(cfg.profile_dir()),
        }

    def _run(self, platform: str) -> None:
        try:
            with browser.platform_session(platform) as page:
                self._set(status="waiting_for_human", detail="Esperando login humano en la ventana de Chrome.")
                deadline = time.time() + cfg.login_timeout_s()
                while time.time() < deadline:
                    measured = detect.detect_login(page, platform)
                    if measured["logged_in"]:
                        state = browser.measure_page(page, platform, f"login_{platform}")
                        state.update(measured)
                        browser.save_session(platform, state)
                        self._set(
                            running=False,
                            status="completed",
                            finished_at=cfg.now_iso(),
                            detail=f"Login detectado: {measured['evidence']}",
                            screenshot=state.get("screenshot"),
                        )
                        return
                    time.sleep(cfg.login_poll_s())
                browser.save_session(
                    platform,
                    {
                        **browser.empty_session(platform),
                        "status": "login_timeout",
                        "evidence": (
                            f"Se cerró la ventana de login tras {int(cfg.login_timeout_s())} s "
                            "sin detectar sesión activa."
                        ),
                        "checked_at": cfg.now_iso(),
                        "stale": False,
                    },
                )
                self._set(
                    running=False,
                    status="timeout",
                    finished_at=cfg.now_iso(),
                    detail="Tiempo de espera de login agotado sin sesión detectada.",
                )
        except Exception as exc:  # noqa: BLE001 - se reporta la causa literal
            browser.save_session(
                platform,
                {
                    **browser.empty_session(platform),
                    "status": "error",
                    "evidence": f"No se pudo abrir el login: {type(exc).__name__}: {exc}",
                    "checked_at": cfg.now_iso(),
                    "stale": False,
                },
            )
            self._set(
                running=False,
                status="error",
                finished_at=cfg.now_iso(),
                detail=f"{type(exc).__name__}: {exc}",
            )


login_keeper = LoginKeeper()
