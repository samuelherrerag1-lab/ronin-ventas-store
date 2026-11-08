"""Configuración persistente de la programación de publicaciones.

``data/publish_jobs/schedule.json`` guarda cuántas piezas se quieren por día,
las franjas horarias y si publican de verdad (dry_run=false). Aquí solo se
valida y persiste: no se publica nada.
"""

import datetime
from typing import Any, Dict, List, Optional

from backend.services import social_config as cfg
from backend.services import social_replies
from backend.services.json_store import lock_for, read_json, write_json_atomic

DEFAULT_SCHEDULE: Dict[str, Any] = {
    "enabled": False,
    "dry_run": True,
    "threads_per_day": 5,
    "pinterest_per_day": 5,
    "times_local": ["09:00", "13:00", "18:00"],
    "updated_at": None,
    "last_tick": None,
    "last_error": None,
    "runs": [],
}


def _load() -> Dict[str, Any]:
    with lock_for(cfg.SCHEDULE_PATH):
        data, error = read_json(cfg.SCHEDULE_PATH)
    config = dict(DEFAULT_SCHEDULE)
    config["times_local"] = list(DEFAULT_SCHEDULE["times_local"])
    config["runs"] = []
    if error or not isinstance(data, dict):
        return config
    for key, default in DEFAULT_SCHEDULE.items():
        value = data.get(key, default)
        if key == "runs" and not isinstance(value, list):
            value = []
        if key == "times_local" and not isinstance(value, list):
            value = list(DEFAULT_SCHEDULE["times_local"])
        config[key] = value
    return config


def _save(config: Dict[str, Any]) -> Dict[str, Any]:
    config["updated_at"] = cfg.now_iso()
    config["runs"] = config.get("runs", [])[-200:]
    write_json_atomic(cfg.SCHEDULE_PATH, config)
    return config


def _valid_time(value: Any) -> bool:
    try:
        hour, minute = str(value).split(":")
        return 0 <= int(hour) <= 23 and 0 <= int(minute) <= 59
    except (ValueError, AttributeError):
        return False


def update_schedule(payload: Dict[str, Any]) -> Dict[str, Any]:
    config = _load()
    if "enabled" in payload:
        config["enabled"] = bool(payload["enabled"])
    if "dry_run" in payload:
        config["dry_run"] = bool(payload["dry_run"])
    for key, maximum in (("threads_per_day", 20), ("pinterest_per_day", 20)):
        if key in payload:
            try:
                value = int(payload[key])
            except (TypeError, ValueError) as exc:
                raise cfg.SocialError(f"{key} debe ser un entero entre 0 y {maximum}.") from exc
            if not 0 <= value <= maximum:
                raise cfg.SocialError(f"{key} debe estar entre 0 y {maximum}.")
            config[key] = value
    if "times_local" in payload:
        times = payload["times_local"]
        if not isinstance(times, list) or not 1 <= len(times) <= 6:
            raise cfg.SocialError("times_local debe ser una lista de 1 a 6 horas 'HH:MM'.")
        if not all(_valid_time(item) for item in times):
            raise cfg.SocialError("times_local contiene una hora inválida (formato HH:MM).")
        config["times_local"] = [str(item) for item in times]
    return _save(config)


def _slot_minutes(slot: str) -> int:
    hour, minute = slot.split(":")
    return int(hour) * 60 + int(minute)


def slot_now(now: datetime.datetime, config: Dict[str, Any]) -> Optional[str]:
    """Franja más reciente ya vencida hoy (None si aún no toca ninguna)."""
    current = now.hour * 60 + now.minute
    due = [slot for slot in config.get("times_local", []) if _slot_minutes(slot) <= current]
    return sorted(due, key=_slot_minutes)[-1] if due else None


def next_slot(now: datetime.datetime, config: Dict[str, Any]) -> Optional[str]:
    current = now.hour * 60 + now.minute
    upcoming = sorted(
        (slot for slot in config.get("times_local", []) if _slot_minutes(slot) > current),
        key=_slot_minutes,
    )
    return upcoming[0] if upcoming else None


def get_schedule() -> Dict[str, Any]:
    config = _load()
    now = datetime.datetime.now()
    config["next_slot"] = next_slot(now, config)
    config["pending_replies"] = social_replies.pending_count()
    return config


def runs_today(config: Dict[str, Any], today: str) -> List[Dict[str, Any]]:
    return [run for run in config.get("runs", []) if run.get("date") == today]
