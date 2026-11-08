"""Cola persistente de auto-respuestas de Threads (2 en la primera hora).

Se encola al publicar el post real. El scheduler las publica cuando vencen; si
fallan se reintentan con un máximo de intentos y se guarda el error literal.
"""

import datetime
import os
import secrets
from typing import Any, Dict, List, Optional

from backend.services import social_config as cfg
from backend.services.json_store import lock_for, read_json, write_json_atomic

MAX_ATTEMPTS = 3


def _delays_minutes() -> List[float]:
    raw = os.environ.get("RONIN_SOCIAL_REPLY_DELAYS_MIN", "7,26").strip()
    delays: List[float] = []
    for chunk in raw.split(","):
        try:
            value = float(chunk.strip())
        except ValueError:
            continue
        if value > 0:
            delays.append(value)
    return delays or [7.0, 26.0]


def _load() -> Dict[str, Any]:
    with lock_for(cfg.REPLY_QUEUE_PATH):
        data, error = read_json(cfg.REPLY_QUEUE_PATH)
    if error or not isinstance(data, dict):
        return {"threads": [], "updated_at": None}
    if not isinstance(data.get("threads"), list):
        data["threads"] = []
    return data


def _save(data: Dict[str, Any]) -> Dict[str, Any]:
    data["updated_at"] = cfg.now_iso()
    write_json_atomic(cfg.REPLY_QUEUE_PATH, data)
    return data


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def enqueue_replies(post_url: str, replies: List[str], delay_minutes: Optional[List[float]] = None) -> List[Dict[str, Any]]:
    """Programa las auto-respuestas de un post publicado de verdad."""
    if not post_url or not replies:
        return []
    delays = delay_minutes if delay_minutes else _delays_minutes()
    now = _now()
    entries: List[Dict[str, Any]] = []
    for index, text in enumerate(replies[: len(delays)]):
        text = (text or "").strip()
        if not text:
            continue
        due = now + datetime.timedelta(minutes=delays[index])
        entries.append(
            {
                "reply_id": f"rpl_{secrets.token_hex(4)}",
                "platform": "threads",
                "post_url": post_url,
                "text": text,
                "due_at": due.isoformat(),
                "status": "pending",
                "attempts": 0,
                "last_error": None,
                "created_at": cfg.now_iso(),
                "published_at": None,
            }
        )
    if not entries:
        return []
    with lock_for(cfg.REPLY_QUEUE_PATH):
        data = _load()
        data["threads"].extend(entries)
        _save(data)
    return entries


def list_replies(limit: int = 100) -> List[Dict[str, Any]]:
    return _load()["threads"][-limit:]


def due_replies(now: Optional[datetime.datetime] = None) -> List[Dict[str, Any]]:
    reference = now or _now()
    due: List[Dict[str, Any]] = []
    for entry in _load()["threads"]:
        if entry.get("status") != "pending" or int(entry.get("attempts", 0)) >= MAX_ATTEMPTS:
            continue
        try:
            due_at = datetime.datetime.fromisoformat(str(entry.get("due_at")))
        except ValueError:
            continue
        if due_at <= reference:
            due.append(entry)
    return due


def update_reply(reply_id: str, **fields: Any) -> Optional[Dict[str, Any]]:
    with lock_for(cfg.REPLY_QUEUE_PATH):
        data = _load()
        for entry in data["threads"]:
            if entry.get("reply_id") == reply_id:
                entry.update(fields)
                _save(data)
                return entry
    return None


def mark_result(entry: Dict[str, Any], ok: bool, detail: str = "") -> Optional[Dict[str, Any]]:
    reply_id = str(entry.get("reply_id"))
    if ok:
        return update_reply(reply_id, status="published", published_at=cfg.now_iso(), last_error=None)
    attempts = int(entry.get("attempts", 0)) + 1
    status = "failed" if attempts >= MAX_ATTEMPTS else "pending"
    return update_reply(reply_id, attempts=attempts, status=status, last_error=detail[:1000])


def pending_count() -> int:
    return sum(1 for entry in _load()["threads"] if entry.get("status") == "pending")
