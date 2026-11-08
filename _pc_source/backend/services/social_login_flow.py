"""Login humano en UNA sola ventana persistente con dos pestañas.

Abre Chrome con `launch_persistent_context(user_data_dir=data/chrome_vault,
channel="chrome", headless=False)`, deja una pestaña en cada plataforma y espera
a que el humano inicie sesión. Guarda cada sesión medida en
`data/publish_jobs/sessions.json` y el estado del flujo en
`data/publish_jobs/login_flow.json` para poder consultarlo desde otro proceso.
"""

import threading
import time
from typing import Any, Dict, List, Optional

from backend.services import social_browser as browser
from backend.services import social_config as cfg
from backend.services import social_detect as detect
from backend.services.json_store import read_json, write_json_atomic

STATUS_PATH_NAME = "login_flow.json"
_GUARD = threading.Lock()


def status_path():
    return cfg.SOCIAL_DIR / STATUS_PATH_NAME


def read_flow_status() -> Dict[str, Any]:
    data, error = read_json(status_path())
    if error or not isinstance(data, dict):
        return {"running": False, "status": "idle", "platforms": {}, "detail": "Sin login multi-pestaña en curso."}
    return data


def _write_flow_status(state: Dict[str, Any]) -> None:
    cfg.ensure_dirs()
    write_json_atomic(status_path(), state)


class MultiLoginFlow:
    def __init__(self) -> None:
        self._thread: Optional[threading.Thread] = None
        self._state: Dict[str, Any] = {
            "running": False,
            "status": "idle",
            "platforms": {},
            "logged": [],
            "pending": [],
            "started_at": None,
            "deadline": None,
            "finished_at": None,
            "detail": "Sin login multi-pestaña en curso.",
        }

    def status(self) -> Dict[str, Any]:
        with _GUARD:
            state = dict(self._state)
            alive = self._thread is not None and self._thread.is_alive()
        if state.get("running") and not alive:
            state["running"] = False
        return state

    def _set(self, **fields: Any) -> Dict[str, Any]:
        with _GUARD:
            self._state.update(fields)
            snapshot = dict(self._state)
            snapshot["platforms"] = dict(self._state.get("platforms", {}))
        _write_flow_status(snapshot)
        return snapshot

    def start(self, platforms: Optional[List[str]] = None, timeout_s: Optional[float] = None) -> Dict[str, Any]:
        wanted = list(platforms or cfg.PLATFORMS)
        for platform in wanted:
            if platform not in cfg.PLATFORMS:
                raise cfg.SocialError(f"Plataforma no soportada: {platform}")
        timeout = float(timeout_s or cfg.login_timeout_s())
        cfg.assert_profile_available()
        with _GUARD:
            if self._thread is not None and self._thread.is_alive():
                return {
                    **self.status(),
                    "started": False,
                    "detail": "Ya hay una ventana de login multi-pestaña abierta; termínala antes.",
                }
            self._state = {
                "running": True,
                "status": "opening_browser",
                "platforms": {platform: {"logged_in": False, "status": "waiting"} for platform in wanted},
                "logged": [],
                "pending": wanted,
                "started_at": cfg.now_iso(),
                "deadline": cfg.now_iso(),
                "finished_at": None,
                "detail": "Abriendo Chrome persistente con una pestaña por plataforma.",
            }
            thread = threading.Thread(
                target=self._run, args=(wanted, timeout), daemon=True, name="ronin-login-multi"
            )
            self._thread = thread
        _write_flow_status(dict(self._state))
        thread.start()
        return {**self.status(), "started": True}

    def wait(self, max_extra_s: float = 120.0) -> Dict[str, Any]:
        thread = self._thread
        if thread is not None:
            thread.join(max_extra_s)
        return self.status()

    def _run(self, platforms: List[str], timeout_s: float) -> None:
        deadline = time.time() + timeout_s
        try:
            with browser.persistent_context() as (context, first_page):
                pages: Dict[str, Any] = {}
                for index, platform in enumerate(platforms):
                    page = first_page if index == 0 else context.new_page()
                    page.goto(
                        cfg.PLATFORM_LOGIN[platform],
                        wait_until="domcontentloaded",
                        timeout=cfg.goto_timeout_ms(),
                    )
                    pages[platform] = page
                self._set(
                    status="waiting_for_human",
                    detail=(
                        "Ventana abierta con dos pestañas (Threads y Pinterest). "
                        "Inicia sesión en cada una; el flujo detecta el login solo."
                    ),
                )
                pending = list(platforms)
                states: Dict[str, Any] = dict(self.status().get("platforms", {}))
                while pending and time.time() < deadline:
                    for platform in list(pending):
                        measured = detect.detect_login(pages[platform], platform)
                        if not measured["logged_in"]:
                            continue
                        state = browser.measure_page(pages[platform], platform, f"login_{platform}")
                        state.update(measured)
                        browser.save_session(platform, state)
                        states[platform] = {
                            "logged_in": True,
                            "status": "logged_in",
                            "account_label": state.get("account_label"),
                            "evidence": state.get("evidence"),
                            "screenshot": state.get("screenshot"),
                            "checked_at": state.get("checked_at"),
                        }
                        pending.remove(platform)
                        self._set(platforms=states, pending=list(pending), logged=[p for p in platforms if p not in pending])
                    if pending:
                        time.sleep(cfg.login_poll_s())
                for platform in pending:
                    states[platform] = {
                        "logged_in": False,
                        "status": "login_timeout",
                        "evidence": f"Sin login detectado en {int(timeout_s)} s de espera.",
                    }
                    browser.save_session(
                        platform,
                        {
                            **browser.empty_session(platform),
                            "status": "login_timeout",
                            "evidence": states[platform]["evidence"],
                            "checked_at": cfg.now_iso(),
                            "stale": False,
                        },
                    )
                finished = "completed" if not pending else "timeout"
                self._set(
                    running=False,
                    status=finished,
                    pending=list(pending),
                    platforms=states,
                    logged=[p for p in platforms if p not in pending],
                    finished_at=cfg.now_iso(),
                    detail=(
                        "Sesiones detectadas: " + ", ".join(p for p in platforms if p not in pending)
                        if not pending
                        else "Tiempo agotado. Sin sesión en: " + ", ".join(pending)
                    ),
                )
        except Exception as exc:  # noqa: BLE001 - la causa literal es la evidencia
            self._set(
                running=False,
                status="error",
                finished_at=cfg.now_iso(),
                detail=f"No se pudo abrir el login multi-pestaña: {type(exc).__name__}: {exc}",
            )


multi_login_flow = MultiLoginFlow()


def wait_for_logins(platforms: Optional[List[str]] = None, timeout_s: Optional[float] = None) -> Dict[str, Any]:
    """Bloquea hasta login de todas las plataformas o hasta el timeout."""
    flow = MultiLoginFlow()
    started = flow.start(platforms, timeout_s)
    print(f"login_flow started={started.get('started')} profile={cfg.profile_dir()}", flush=True)
    result = flow.wait(max_extra_s=float(timeout_s or cfg.login_timeout_s()) + 180.0)
    print(
        "login_flow finished status="
        + str(result.get("status"))
        + " logged="
        + ",".join(result.get("logged") or [])
        + " pending="
        + ",".join(result.get("pending") or []),
        flush=True,
    )
    return result
